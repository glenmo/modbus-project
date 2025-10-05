#!/usr/bin/env python3
"""
Simple Modbus TCP server (pymodbus 3.x)

- Exposes Coils (00001+), Discrete Inputs (10001+),
  Holding Registers (40001+), and Input Registers (30001+)
- By default, Holding Register at address 0 increments every second so you can test reads easily.
- Works with ANY unit-id by default (single=True). Change to multi-slave if you need separate unit-ids.

Run:
  python3 modbus_server.py --host 0.0.0.0 --port 5020

Test (from another shell/python):
  python3 - <<'PY'
from pymodbus.client import ModbusTcpClient
c = ModbusTcpClient("127.0.0.1", port=5020)
print("Connect:", c.connect())
print("Read HR 0..4:", c.read_holding_registers(0, 5, unit=1).registers)
print("Write HR[1]=1234:", c.write_register(1, 1234, unit=1))
print("Read HR 0..4:", c.read_holding_registers(0, 5, unit=1).registers)
c.close()
PY
"""
import argparse
import logging
import threading
import time

from pymodbus.datastore import (
    ModbusServerContext,
    ModbusSlaveContext,
    ModbusSequentialDataBlock,
)
from pymodbus.device import ModbusDeviceIdentification
from pymodbus.server import StartTcpServer

# --------- Logging ----------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
log = logging.getLogger("modbus_server")


def build_single_slave_context(size_coils=1000, size_di=1000, size_hr=1000, size_ir=1000):
    """
    Create a single Modbus slave context with sequential (contiguous) datablocks.
    Addresses are 0-based inside pymodbus:
      - Coils:            0..size_coils-1
      - Discrete inputs:  0..size_di-1
      - Holding regs:     0..size_hr-1
      - Input regs:       0..size_ir-1
    """
    store = ModbusSlaveContext(
        di=ModbusSequentialDataBlock(0, [0] * size_di),
        co=ModbusSequentialDataBlock(0, [0] * size_coils),
        hr=ModbusSequentialDataBlock(0, [0] * size_hr),
        ir=ModbusSequentialDataBlock(0, [0] * size_ir),
        zero_mode=True,  # treat addresses as 0-based
    )
    # single=True allows any unit-id to hit the same store (easiest for testing)
    context = ModbusServerContext(slaves=store, single=True)
    return context


def start_demo_updater(context, interval_sec=1.0):
    """
    Background thread: increments Holding Register 0 every `interval_sec`.
    Demonstrates data changing for easy client testing.
    """
    def worker():
        i = 0
        while True:
            try:
                # unit_id is ignored when single=True, but .setValues requires one; 0x00 or 0x01 both fine
                hr_values = context[0x00].getValues(3, 0, count=1)  # function code 3 (holding), address 0
                current = hr_values[0] if hr_values else 0
                new_val = (current + 1) & 0xFFFF
                context[0x00].setValues(3, 0, [new_val])
                if i % 5 == 0:
                    log.info("HR[0] -> %d", new_val)
                i += 1
                time.sleep(interval_sec)
            except Exception as e:
                log.exception("Updater error: %s", e)
                time.sleep(2.0)

    t = threading.Thread(target=worker, name="hr-updater", daemon=True)
    t.start()


def build_identity(vendor_name="ExampleCo", product_code="MBsrv", product_name="Python Modbus Server"):
    identity = ModbusDeviceIdentification()
    identity.VendorName = vendor_name
    identity.ProductCode = product_code
    identity.VendorUrl = "https://example.com"
    identity.ProductName = product_name
    identity.ModelName = "pymodbus"
    identity.MajorMinorRevision = "1.0"
    return identity


def main():
    parser = argparse.ArgumentParser(description="Simple Modbus TCP server (pymodbus 3.x)")
    parser.add_argument("--host", default="127.0.0.1", help="Listen address (default: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=5020, help="TCP port (default: 5020)")
    parser.add_argument("--no-demo", action="store_true", help="Disable demo updater of HR[0]")
    parser.add_argument("--hr-size", type=int, default=100, help="Holding register block size")
    parser.add_argument("--ir-size", type=int, default=100, help="Input register block size")
    parser.add_argument("--co-size", type=int, default=100, help="Coils block size")
    parser.add_argument("--di-size", type=int, default=100, help="Discrete inputs block size")
    args = parser.parse_args()

    context = build_single_slave_context(
        size_coils=args.co_size, size_di=args.di_size, size_hr=args.hr_size, size_ir=args.ir_size
    )

    # Seed a few example values
    context[0x00].setValues(3, 0, [42, 100, 200])  # holding regs HR[0..2]
    context[0x00].setValues(1, 0, [1, 0, 1, 1])    # coils CO[0..3]

    if not args.no_demo:
        start_demo_updater(context)

    identity = build_identity()

    log.info("Starting Modbus TCP server on %s:%d", args.host, args.port)
    # Blocks forever; press Ctrl+C to stop
    StartTcpServer(
        context=context,
        identity=identity,
        address=(args.host, args.port),
    )


if __name__ == "__main__":
    main()

