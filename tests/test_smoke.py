def test_imports():
    import src.modbus_client as mc
    import src.modbus_server as ms
    assert hasattr(mc, "write_registers")
    assert hasattr(ms, "build_context")
