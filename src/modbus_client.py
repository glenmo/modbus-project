import argparse
from typing import List
from pymodbus.client import ModbusTcpClient
from pymodbus.exceptions import ConnectionException
from .utils import chunk_values

def write_registers(client: ModbusTcpClient, address: int, values: List[int], unit: int) -> None:
    for i, chunk in enumerate(chunk_values(values)):
        resp = client.write_registers(address=address + i*len(chunk), values=chunk, slave=unit)
        if resp.isError():
            raise RuntimeError(f"Write failed at {address + i*len(chunk)}: {resp}")
        else:
            print(f"Wrote {len(chunk)} reg(s) at {address + i*len(chunk)}")

def read_registers(client: ModbusTcpClient, address: int, count: int, unit: int) -> List[int]:
    resp = client.read_holding_registers(address=address, count=count, slave=unit)
    if resp.isError():
        raise RuntimeError(f"Read failed at {address}: {resp}")
    return list(resp.registers)

def main():
    parser = argparse.ArgumentParser(description="Simple Modbus TCP client (holding registers).")
    parser.add_argument("--host", required=True, help="Server IP/hostname")
    parser.add_argument("--port", type=int, default=502, help="Server TCP port (default 502)")
    parser.add_argument("--unit", type=int, default=1, help="Unit/Slave id (default 1)")
    parser.add_argument("--write", nargs="+", type=int, help="Write: <address> <val1> [val2 ...]")
    parser.add_argument("--read", nargs=2, type=int, metavar=("ADDRESS","COUNT"), help="Read: <address> <count>")
    args = parser.parse_args()

    client = ModbusTcpClient(host=args.host, port=args.port, timeout=3)
    if not client.connect():
        raise ConnectionException(f"Failed to connect to {args.host}:{args.port}")

    try:
        if args.write:
            addr = args.write[0]
            vals = args.write[1:]
            if not vals:
                raise SystemExit("When using --write, supply at least one value.")
            write_registers(client, addr, vals, unit=args.unit)

        if args.read:
            addr, count = args.read
            data = read_registers(client, addr, count, unit=args.unit)
            print(f"Read @ {addr} -> {data}")
    finally:
        client.close()

if __name__ == "__main__":
    main()
