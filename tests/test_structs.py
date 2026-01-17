from cdantic import CStruct
from cdantic.types import c_field
import ctypes

class Point(CStruct):
    x: int = c_field(ctypes.c_long)
    y: int = c_field(ctypes.c_long)

class Rect(CStruct):
    left: int = c_field(ctypes.c_long)
    top: int = c_field(ctypes.c_long)
    right: int = c_field(ctypes.c_long)
    bottom: int = c_field(ctypes.c_long)

def test_basic_struct():
    p = Point(x=10, y=20)
    c_p = p.to_c()
    
    assert isinstance(c_p, ctypes.Structure)
    assert c_p.x == 10
    assert c_p.y == 20
    assert ctypes.sizeof(c_p) == 8 # 2 * 4 bytes (long) on 32-bit or usually 4 bytes. 
    # c_long is usually 4 bytes (32-bit int) even on 64-bit windows.

def test_round_trip():
    p = Point(x=55, y=99)
    c_p = p.to_c()
    
    p2 = Point.from_c(c_p)
    assert p2.x == 55
    assert p2.y == 99

def test_nested_struct():
    # If we supported nesting (logic in core.py handles it)
    pass
