import argparse
from pymodbus.datastore import ModbusServerContext, ModbusSequentialDataBlock
from pymodbus.datastore.context import ModbusSlaveContext
from pymodbus.server import StartTcpServer

def build_context(size: int = 1000) -> ModbusServerContext:
    # Initialize all register spaces. Start with zeros.
    store = ModbusSlaveContext(
        di = ModbusSequentialDataBlock(0, [0]*size),
        co = ModbusSequentialDataBlock(0, [0]*size),
        hr = ModbusSequentialDataBlock(0, [0]*size),
        ir = ModbusSequentialDataBlock(0, [0]*size),
        zero_mode=True,  # addressing starts at 0
    )
    return ModbusServerContext(slaves={1: store}, single=False)

def main():
    parser = argparse.ArgumentParser(description="Simple Modbus TCP server with in-memory datastore.")
    parser.add_argument("--host", default="0.0.0.0", help="Bind IP (default 0.0.0.0)")
    parser.add_argument("--port", type=int, default=5020, help="TCP Port (default 5020)")
    parser.add_argument("--size", type=int, default=1000, help="Registers per table (default 1000)")
    args = parser.parse_args()

    context = build_context(size=args.size)
    print(f"Starting Modbus TCP server on {args.host}:{args.port} (unit id 1)")
    StartTcpServer(context, address=(args.host, args.port))

if __name__ == "__main__":
    main()
