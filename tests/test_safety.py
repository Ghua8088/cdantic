import pytest
import ctypes
import cdantic
import sys
from typing import Annotated
from cdantic import (
    CStruct, 
    CFunction, 
    bind_library, 
    LibraryNotBoundError, 
    is_null, 
    assert_not_null, 
    ValidationBoundaryError
)

class ExampleStruct(CStruct):
    __test__ = False # Tell pytest this is not a test class
    x: int
    y: int

def test_binding_safety():
    class MockEngine:
        # Use GetTickCount from kernel32 (returns int, takes no args)
        @CFunction(func_name="GetTickCount")
        def get_ticks(self) -> int: ...
    
    engine = MockEngine()
    
    # Attempting to call without binding should raise LibraryNotBoundError
    with pytest.raises(LibraryNotBoundError):
        engine.get_ticks()
        
    # Bind it
    bind_library(engine, "kernel32")
    # Should work now
    res = engine.get_ticks()
    assert isinstance(res, int)

def test_struct_abi_helpers():
    class Point(CStruct):
        x: Annotated[int, ctypes.c_int]
        y: Annotated[int, ctypes.c_int]
    
    assert Point.sizeof() == 8 # 2 * 4 bytes
    assert Point.offsetof("x") == 0
    assert Point.offsetof("y") == 4

def test_null_helpers():
    assert is_null(0) is True
    assert is_null(None) is True
    assert is_null(ctypes.c_void_p(0)) is True
    assert is_null(1) is False
    
    with pytest.raises(ValidationBoundaryError):
        assert_not_null(0, "Handle")

def test_packing():
    class Packed(CStruct):
        __pack__ = 1  # Using dunder is safest with Pydantic V2
        a: Annotated[int, ctypes.c_byte]
        b: Annotated[int, ctypes.c_int]

    # a is 1 byte. With pack=1, b starts at offset 1.
    assert Packed.offsetof("b") == 1
    assert Packed.sizeof() == 5

def test_nested_packing():
    class Inner(CStruct):
        __pack__ = 1
        a: Annotated[int, ctypes.c_byte]
        b: Annotated[int, ctypes.c_int] # offset 1, size 5
        
    class Outer(CStruct):
        __pack__ = 1
        c: Annotated[int, ctypes.c_byte]
        d: Inner # If Inner is size 5 and Outer is pack=1, d starts at 1.
        
    assert Inner.offsetof("b") == 1
    assert Outer.offsetof("d") == 1
    assert Outer.sizeof() == 6
