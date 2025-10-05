from typing import Sequence

def chunk_values(values: Sequence[int], chunk_size: int = 120) -> list[list[int]]:
    """Split a sequence of register values into chunks suitable for Modbus writes.
    Many devices cap multi-register writes; 120 is a safe default for many stacks.
    """
    out = []
    chunk = []
    for v in values:
        chunk.append(int(v) & 0xFFFF)
        if len(chunk) >= chunk_size:
            out.append(chunk)
            chunk = []
    if chunk:
        out.append(chunk)
    return out
