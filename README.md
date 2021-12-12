# Private document search, ranking and retrieval

Make sure to clone with `--recursive`, in order to download the `libdpf` dependency.

## Usage

The two main files of the project are `source/client.py` and `source/server.py`

First, start two server instances on two different ports by running

```python3 server.py --scheme scoring_scheme --pir pir_scheme -p portnum```

on two different ports. 

Choices for scoring scheme are `random-vectors`, `rv-opt`, `PPRF`, `PPRF-opt`, and `DPF`.
Choises for PIR scheme are `naive` and `it-pir`.

Make sure to use the same scoring and PIR scheme on both servers.

Finally, run the client using

```python3.9 client.py --scheme scoring_scheme --pir pir_scheme --ports port1 port2```,

replacing `port1` and `port2` with the server ports.
