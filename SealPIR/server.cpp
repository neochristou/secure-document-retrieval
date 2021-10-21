#include "pir.hpp"
#include "pir_client.hpp"
#include "pir_server.hpp"
#include <seal/galoiskeys.h>
#include <seal/seal.h>
#include <chrono>
#include <memory>
#include <random>
#include <cstdint>
#include <cstddef>

#include <unistd.h>
#include <stdio.h>
#include <sys/socket.h>
#include <stdlib.h>
#include <netinet/in.h>
#include <string.h>

#define PORT 8080
#define GALOIS_KEYS_LEN 3621711
#define QUERY_LEN 65682

using namespace std::chrono;
using namespace std;
using namespace seal;

bool send_all(int socket, void *buffer, size_t length) {
    char *ptr = (char*) buffer;
    while (length > 0)
    {
        int i = send(socket , ptr, length, 0);
        if (i < 1) return false;
        ptr += i;
        length -= i;
    }
    return true;
}

int setup() {
    int server_fd, sock, valread;
    struct sockaddr_in address;
    int addrlen = sizeof(address);
    int opt = 1;

    // Creating socket file descriptor
    if ((server_fd = socket(AF_INET, SOCK_STREAM, 0)) == 0) {
        perror("socket failed");
        exit(EXIT_FAILURE);
    }

    // Forcefully attaching socket to the port 8080
    if (setsockopt(server_fd, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt))) {
        perror("setsockopt");
        exit(EXIT_FAILURE);
    }

    address.sin_family = AF_INET;
    address.sin_addr.s_addr = INADDR_ANY;
    address.sin_port = htons( PORT );

    // Forcefully attaching socket to the port 8080
    if (::bind(server_fd, (struct sockaddr *)&address, sizeof(address)) < 0) {
        perror("bind failed");
        exit(EXIT_FAILURE);
    }

    if (listen(server_fd, 3) < 0) {
        perror("listen");
        exit(EXIT_FAILURE);
    }

    if ((sock = accept(server_fd, (struct sockaddr *)&address,
                       (socklen_t*)&addrlen))<0) {
        perror("accept");
        exit(EXIT_FAILURE);
    }

    return sock;

}

int main(int argc, char *argv[]) {
    char buffer[0x1000] = {0};
    char *full_buf = new char[0x500000];
    long total_recv = 0;
    int valread;

    uint64_t number_of_items = 1 << 12;
    uint64_t size_per_item = 288; // in bytes
    uint32_t N = 2048;

    // Recommended values: (logt, d) = (12, 2) or (8, 1).
    uint32_t logt = 12;
    uint32_t d = 2;

    EncryptionParameters params(scheme_type::BFV);
    PirParams pir_params;

    // Generates all parameters
    cout << "Server: Generating all parameters" << endl;
    gen_params(number_of_items, size_per_item, N, logt, d, params, pir_params);

    cout << "Server: Initializing the database (this may take some time) ..." << endl;

    // Create test database
    auto db(make_unique<uint8_t[]>(number_of_items * size_per_item));

    // Copy of the database. We use this at the end to make sure we retrieved
    // the correct element.
    auto db_copy(make_unique<uint8_t[]>(number_of_items * size_per_item));

    random_device rd;
    for (uint64_t i = 0; i < number_of_items; i++) {
        for (uint64_t j = 0; j < size_per_item; j++) {
            auto val = rd() % 256;
            db.get()[(i * size_per_item) + j] = val;
            db_copy.get()[(i * size_per_item) + j] = val;
        }
    }

    // Initialize PIR Server
    cout << "Server: Initializing..." << endl;
    PIRServer server(params, pir_params);

    int sock = setup();

    // Set galois key for client with id 0
    cout << "Server: Receiving galois keys..." << endl;
    memset(buffer, 0, sizeof(buffer));
    while (total_recv < GALOIS_KEYS_LEN) {
      valread = recv(sock, buffer, sizeof(buffer), 0);
      memcpy(full_buf + total_recv, buffer, valread);
      memset(buffer, 0, sizeof(buffer));
      total_recv += valread;
    }

    cout << "Server: Galois keys received, total length:" << total_recv << endl;

    cout << "Server: Deserializing galois keys..." << endl;
    std::string galois_keys_ser(full_buf, total_recv);
    GaloisKeys *galois_keys = deserialize_galoiskeys(galois_keys_ser);

    cout << "Server: Setting Galois keys...";
    server.set_galois_key(0, *galois_keys);

    // Measure database setup
    auto time_pre_s = high_resolution_clock::now();
    server.set_database(move(db), number_of_items, size_per_item);
    server.preprocess_database();
    cout << "Server: database pre processed " << endl;
    auto time_pre_e = high_resolution_clock::now();
    auto time_pre_us = duration_cast<microseconds>(time_pre_e - time_pre_s).count();

    cout << "Server: receiving seriailzed query " << endl;
    memset(full_buf, 0, 0x500000);
    total_recv = 0;
    while (total_recv < QUERY_LEN) {
      valread = recv(sock, buffer, sizeof(buffer), 0);
      memcpy(full_buf + total_recv, buffer, valread);
      memset(buffer, 0, sizeof(buffer));
      total_recv += valread;
    }
    cout << "Server: received seriailzed query, length: " << total_recv << endl;

    cout << "Server: deserializing query..." << endl;
    std::string query_ser(full_buf, total_recv);
    PirQuery query = deserialize_query(d, 1, query_ser, CIPHER_SIZE);

    // Measure query processing (including expansion)
    cout << "Server: generating reply..." << endl;
    auto time_server_s = high_resolution_clock::now();
    PirReply reply = server.generate_reply(query, 0);
    auto time_server_e = high_resolution_clock::now();
    auto time_server_us = duration_cast<microseconds>(time_server_e - time_server_s).count();

    cout << "Server: sending reply to client..." << endl;
    std::string reply_ser = serialize_ciphertexts(reply);
    deserialize_ciphertexts(number_of_items, reply_ser, size_per_item);
    cout << "Server: serialized reply length: " << reply_ser.length()  << endl;
    send_all(sock , (void *)reply_ser.c_str() , reply_ser.length());

    sleep(1);

    /* // Output results */
    /* cout << "Main: PIR result correct!" << endl; */
    /* cout << "Main: PIRServer pre-processing time: " << time_pre_us / 1000 << " ms" << endl; */
    /* cout << "Main: PIRClient query generation time: " << time_query_us / 1000 << " ms" << endl; */
    /* cout << "Main: PIRServer reply generation time: " << time_server_us / 1000 << " ms" */
    /*      << endl; */
    /* cout << "Main: PIRClient answer decode time: " << time_decode_us / 1000 << " ms" << endl; */
    /* cout << "Main: Reply num ciphertexts: " << reply.size() << endl; */

    delete[] full_buf;
    return 0;
}
