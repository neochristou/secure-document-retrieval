#!/bin/bash

REPEATS=100
DEFAULT_SCORING="rv-opt"
DEFAULT_PIR="naive"
SOURCE_DIR="../source"
PYTHON_BIN=/usr/local/bin/python3.9
PORT1=9998
PORT2=9999

# This will only get benchmarks for the scoring part
do_bench_scores()
{
    $PYTHON_BIN $SOURCE_DIR/server.py --scheme $1 --pir $DEFAULT_PIR --port $PORT1 > /dev/null &
    server1_pid=`echo $!`
    $PYTHON_BIN $SOURCE_DIR/server.py --scheme $1 --pir $DEFAULT_PIR --port $PORT2 > /dev/null &
    server2_pid=`echo $!`
    sleep 8 # Wait for server startup
    for rep in $(seq 1 $REPEATS); do
        $PYTHON_BIN $SOURCE_DIR/$2 $PORT1 $PORT2 > /dev/null
    done
    kill -9 $server1_pid $server2_pid
}

do_bench_pir()
{
    $PYTHON_BIN $SOURCE_DIR/server.py --scheme $DEFAULT_SCORING --pir $1 --port $PORT1 > /dev/null &
    server1_pid=`echo $!`
    $PYTHON_BIN $SOURCE_DIR/server.py --scheme $DEFAULT_SCORING --pir $1 --port $PORT2 > /dev/null &
    server2_pid=`echo $!`
    sleep 8 # Wait for server startup
    for rep in $(seq 1 $REPEATS); do
        $PYTHON_BIN $SOURCE_DIR/$2 $PORT1 $PORT2 > /dev/null
    done
    kill -9 $server1_pid $server2_pid
}

main()
{
    case $1 in
        random-vectors)
            do_bench_scores "random-vectors" "random_vecs_cli.py"
            ;;
        rv-opt)
            do_bench_scores "rv-opt" "rv_opt_cli.py"
            ;;
        PPRF)
            do_bench_scores "PPRF" "PPRF_cli.py"
            ;;
        PPRF-opt)
            do_bench_scores "PPRF-opt" "PPRF_cli.py"
            ;;
        DPF)
            do_bench_scores "DPF" "DPF_cli.py"
            ;;
        naive-pir)
            do_bench_pir "naive" "naive_pir_cli.py"
            ;;
        it-pir)
            do_bench_pir "it-pir" "it_pir_cli.py"
            ;;
        all)
            do_bench_scores "random-vectors" "random_vecs_cli.py"

            # Don't wait for port to be released
            PORT1=$(($PORT1-2))
            PORT2=$(($PORT2-2))
            do_bench_scores "rv-opt" "rv_opt_cli.py"

            PORT1=$(($PORT1-2))
            PORT2=$(($PORT2-2))
            do_bench_scores "PPRF" "PPRF_cli.py"

            PORT1=$(($PORT1-2))
            PORT2=$(($PORT2-2))
            do_bench_scores "PPRF-opt" "PPRF_cli.py"

            PORT1=$(($PORT1-2))
            PORT2=$(($PORT2-2))
            do_bench_scores "DPF" "DPF_cli.py"

            PORT1=$(($PORT1-2))
            PORT2=$(($PORT2-2))
            # For GNU coreutils
            # sed -i 's/^PIR_SERVER_FILE = .*$/PIR_SERVER_FILE = \"naive_pir_ser.txt\"/g' $SOURCE_DIR/config.py
            # For BSD coreutils
            sed -i '' 's/^PIR_SERVER_FILE = .*$/PIR_SERVER_FILE = \"naive_pir_ser.txt\"/g' $SOURCE_DIR/config.py
            do_bench_pir "naive" "naive_pir_cli.py"

            PORT1=$(($PORT1-2))
            PORT2=$(($PORT2-2))
            sed -i '' 's/^PIR_SERVER_FILE = .*$/PIR_SERVER_FILE = \"it_pir_ser.txt\"/g' $SOURCE_DIR/config.py
            do_bench_pir "it-pir" "it_pir_cli.py"

            ;;
        clean)
            rm *.txt
            ;;
        *)
            echo "Wrong option"
            exit -1
    esac
}

main $@
