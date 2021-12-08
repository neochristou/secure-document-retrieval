import argparse
import subprocess
import time
from multiprocessing import Process

REPEATS = 1
DEFAULT_SCORING = "rv-opt"
DEFAULT_PIR = "naive"
SOURCE_DIR = "../source/"
PYTHON_BIN = "/usr/local/bin/python3.9"
PORT1 = "9998"
PORT2 = "9999"

if __name__ == "__main__":

    arg_parser = argparse.ArgumentParser(
        description="Choose scheme for benchmarking")

#     arg_parser.add_argument("random-vectors", action='store_true')
#     arg_parser.add_argument("rv-opt", action='store_true')
#     arg_parser.add_argument("PPRF", action='store_true')
#     arg_parser.add_argument("PPRD-opt", action='store_true')
    arg_parser.add_argument("--DPF", action='store_true')
    # arg_parser.add_argument("naive-pir", action='store_true')
    # arg_parser.add_argument("it-pir", action='store_true')
    # arg_parser.add_argument("all", action='store_true')

    args = arg_parser.parse_args()

    if args.DPF:
        scheme = "DPF"
        cli = "DPF_cli.py"

    server_args = [PYTHON_BIN, SOURCE_DIR + "server.py", "--scheme", scheme, "--pir", DEFAULT_PIR,
                   "--port"]
    cli_args = [PYTHON_BIN, SOURCE_DIR + cli]

    # server_out = open(scheme + '_server.txt', 'w')
    s1 = subprocess.Popen(server_args + [PORT1])
    s2 = subprocess.Popen(server_args + [PORT2], stdout=subprocess.DEVNULL)
    time.sleep(8)

    cli_output = subprocess.check_output(cli_args)
    print(cli_output)

    # server_out = s1.communicate()[0]
    # print(server_out)

    s1.kill()
    s2.kill()

    # server_out.close()
