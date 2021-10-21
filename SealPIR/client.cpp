#include "pir.hpp"
#include "pir_client.hpp"
#include "pir_server.hpp"
#include <seal/seal.h>
#include <chrono>
#include <memory>
#include <random>
#include <cstdint>
#include <cstddef>

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <string>
#include <unistd.h>
#include <sys/types.h>
#include <arpa/inet.h>

#define PORT 8080
#define IP_ADDR "127.0.0.1"
#define REPLY_LEN 328410

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

int connect_server() {
    int sock = 0;
    struct sockaddr_in serv_addr;

    if ((sock = socket(AF_INET, SOCK_STREAM, 0)) < 0)
    {
        printf("\n Socket creation error \n");
        return -1;
    }

    serv_addr.sin_family = AF_INET;
    serv_addr.sin_port = htons(PORT);

    if(inet_pton(AF_INET, IP_ADDR, &serv_addr.sin_addr)<=0) {
        printf("\nInvalid address/ Address not supported \n");
        return -1;
    }

    if (connect(sock, (struct sockaddr *)&serv_addr, sizeof(serv_addr)) < 0) {
        printf("\nConnection Failed \n");
        return -1;
    }

    return sock;

}

int main(int argc, char *argv[]) {

    int valread;
    char buffer[0x1000] = {0};
    char *full_buf = new char[0x500000];
    long total_recv = 0;

    uint64_t number_of_items = 1 << 12;
    uint64_t size_per_item = 288; // in bytes
    uint32_t N = 2048;

    // Recommended values: (logt, d) = (12, 2) or (8, 1).
    uint32_t logt = 12;
    uint32_t d = 2;

    EncryptionParameters params(scheme_type::BFV);
    PirParams pir_params;

    // Generates all parameters
    cout << "Client: Generating all parameters" << endl;
    gen_params(number_of_items, size_per_item, N, logt, d, params, pir_params);

    cout << "Client: Connecting to server" << endl;

    int sock = connect_server();

    random_device rd;

    // Initialize PIR client....
    PIRClient client(params, pir_params);
    GaloisKeys galois_keys = client.generate_galois_keys();

    std::string galois_keys_ser = serialize_galoiskeys(galois_keys);

    long galois_keys_length = galois_keys_ser.length();

    cout << "Client: sending galois keys, length: " << galois_keys_length << endl;
    /* send(sock, galois_keys_ser.c_str(), galois_keys_ser.length(), 0); */
    send_all(sock, (void *)galois_keys_ser.c_str(), galois_keys_ser.length());
    cout << "Client: galois keys sent" << endl;

    sleep(1);

    // Choose an index of an element in the DB
    cout << "Client: choosing element to retrieve" << endl;
    uint64_t ele_index = rd() % number_of_items; // element in DB at random position
    uint64_t index = client.get_fv_index(ele_index, size_per_item);   // index of FV plaintext
    uint64_t offset = client.get_fv_offset(ele_index, size_per_item); // offset in FV plaintext
    cout << "Client: element index = " << ele_index << " from [0, " << number_of_items -1 << "]" << endl;
    cout << "Client: FV index = " << index << ", FV offset = " << offset << endl;

    // Measure query generation
    auto time_query_s = high_resolution_clock::now();
    PirQuery query = client.generate_query(index);
    auto time_query_e = high_resolution_clock::now();
    auto time_query_us = duration_cast<microseconds>(time_query_e - time_query_s).count();
    cout << "Client: query generated" << endl;

    std::string query_ser = serialize_query(query);
    cout << "Client: serialized query length: " << query_ser.length() << "\n";
    cout << "Client: sending serialized query... " << endl;
    /* send(sock , query_ser.c_str() , query_ser.length(), 0); */
    send_all(sock, (void *)query_ser.c_str() , query_ser.length());

    sleep(1);

    cout << "Client: receiving reply... " << endl;
    memset(full_buf, 0, 0x500000);
    total_recv = 0;
    while (total_recv < REPLY_LEN) {
      valread = recv(sock, buffer, sizeof(buffer), 0);
      memcpy(full_buf + total_recv, buffer, valread);
      memset(buffer, 0, sizeof(buffer));
      total_recv += valread;
    }
    cout << "Client: received reply, total length: " << total_recv << endl;

    sleep(1);

    std::string reply_ser(full_buf, total_recv);
    cout << "Client: deserializing reply" << endl;
    //TODO Check parameters
    PirReply reply = deserialize_ciphertexts(number_of_items, reply_ser, size_per_item);
    cout << "Client: reply deserialized" << endl;

    // Measure response extraction
    auto time_decode_s = chrono::high_resolution_clock::now();
    Plaintext result = client.decode_reply(reply);
    auto time_decode_e = chrono::high_resolution_clock::now();
    auto time_decode_us = duration_cast<microseconds>(time_decode_e - time_decode_s).count();

    // Convert from FV plaintext (polynomial) to database element at the client
    vector<uint8_t> elems(N * logt / 8);
    coeffs_to_bytes(logt, result, elems.data(), (N * logt) / 8);

    /* // Check that we retrieved the correct element */
    /* for (uint32_t i = 0; i < size_per_item; i++) { */
    /*     if (elems[(offset * size_per_item) + i] != db_copy.get()[(ele_index * size_per_item) + i]) { */
    /*         cout << "Main: elems " << (int)elems[(offset * size_per_item) + i] << ", db " */
    /*              << (int) db_copy.get()[(ele_index * size_per_item) + i] << endl; */
    /*         cout << "Main: PIR result wrong!" << endl; */
    /*         return -1; */
    /*     } */
    /* } */

    // Output results
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
