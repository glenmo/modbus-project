# Modbus Project (Python 3)

A simple, collaborative Python 3 project to **read/write Modbus registers** over TCP.

## Features
- Example **Modbus TCP client** using `pymodbus`
- Example **Modbus TCP server** with in-memory data store
- `pytest` tests
- GitHub Actions CI for Python

## Quick Start

### 1) Setup
```bash
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2) Run the Modbus server
```bash
python -m src.modbus_server --host 127.0.0.1 --port 5020
```

### 3) Run the client (read/write demo)
```bash
python -m src.modbus_client --host 127.0.0.1 --port 5020 --unit 1 --write 0 123 456 --read 0 4
```

The above writes two holding registers at address 0, then reads 4 registers starting at 0.

## Project Structure
```
modbus-project/
├── src/
│   ├── __init__.py
│   ├── modbus_client.py
│   ├── modbus_server.py
│   └── utils.py
├── tests/
│   ├── __init__.py
│   └── test_smoke.py
├── requirements.txt
├── README.md
├── .gitignore
├── LICENSE
└── .github/
    └── workflows/
        └── python-app.yml
```

## Notes
- This example targets **`pymodbus>=3.0.0`**. Use the `slave` kwarg (not `unit`) for read/write calls.
- Default server **unit id is 1**.

## License
MIT
