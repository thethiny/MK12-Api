import datetime
import struct

from math import ceil, log

from .enums import AGArray, AGBool, AGChar, AGFloat, AGInt, AGMap, AGTime, IntEnum, enum_to_value

def check_float_double(value):
    d = struct.pack("d", value)
    d = struct.unpack("d", d)[0]
    if d == value:
        return "d"
    
    f = struct.pack("f", value)
    f = struct.unpack("f", f)[0]
    if int(f) == int(value):
        return "f"

    return "d"

def get_size(x: object):
    if hasattr(x, "__len__"):
        if isinstance(x, str):
            data = len(x.encode())
        else:
            data = len(x)  # type: ignore
    else:
        data: int = x  # type: ignore

    if not data:
        return 1

    data = ceil(log(data, 255))

    if not data:
        return 1

    size = 2 ** ceil(log(data, 2))
    if size > 8:
        raise ValueError(f"Value is bigger than 8 bytes: {size}")
    return size


def value_to_bytes(data: int, size):
    return data.to_bytes(size, "big")


def adjust_type(type_, size, step_size = 1):
    if size:
        increment = ceil(log(size, 2))
        type_ += increment * step_size
    return type_


def obj_to_type_bytes(obj: object, zero_as_int: bool = True):
    type_: IntEnum
    size = 0
    has_extra = 0
    if isinstance(obj, dict):
        type_ = AGMap.MAP8
        serial_type = "map"
        has_extra = 1
    elif isinstance(obj, (list, set)):
        type_ = AGArray.ARRAY8
        serial_type = "container"
        has_extra = 1
    elif isinstance(obj, str):
        type_ = AGChar.CHAR8
        serial_type = "value"
        has_extra = 1
    elif isinstance(obj, bytes):
        type_ = AGChar.BYTES8
        serial_type = "value"
        has_extra = 1
    elif isinstance(obj, datetime.datetime):
        type_ = AGTime.EPOCH
        size = 8
        serial_type = "value"
    elif obj is None:
        type_ = AGBool.NONE
        serial_type = "value"
    elif obj is True:
        type_ = AGBool.TRUE
        serial_type = "value"
    elif obj is False:
        type_ = AGBool.FALSE
        serial_type = "value"
    elif obj == 0:
        if zero_as_int:
            type_ = AGInt.UINT8
            size = 1
            serial_type = "value"
            has_extra = 2
        else:
            type_ = AGBool.ZERO
            serial_type = "value"
    elif isinstance(obj, int):
        serial_type = "value"
        if obj > 0:
            type_ = AGInt.UINT8
            has_extra = 2
        elif obj == 0:  # Impossible cuz checked above
            type_ = AGBool.ZERO
            raise ValueError(f"You've reached an impossible scenario!")
        else:
            type_ = AGInt.INT8
            obj = abs(obj)
            has_extra = 2
    elif isinstance(obj, float):
        serial_type = "value"
        type__ = check_float_double(obj)
        if type__ == "f":
            size = 4
            type_ = AGFloat._FLT
        elif type__ == "d":
            size = 8
            type_ = AGFloat.FLOAT
        else:
            raise ValueError(f"Impossible float type {type__}")
    else:
        raise ValueError(f"Unsupported Object: {type(obj)}")

    type_value: int = enum_to_value(type_)
    if has_extra:
        size = get_size(obj)
        type_value = adjust_type(type_value, size, has_extra)

    type_data = value_to_bytes(type_value, 1)

    if has_extra and hasattr(obj, "__len__"):
        data = len(obj)  # type: ignore
        extra_data = value_to_bytes(data, size)
    else:
        extra_data = b""

    return type_data + extra_data, serial_type, size

def int_to_signed_bytes(data: int, size: int):
    data = data + 2 ** (size*8)
    return data.to_bytes(size, "big")

def json_to_ag(data, zero_as_int: bool = True):
    resp, type_, size = obj_to_type_bytes(data, zero_as_int = zero_as_int)
    if type_ == "value":
        if size:
            if isinstance(data, str):
                add_data = data.encode()
            elif isinstance(data, int):
                if data > 0:
                    add_data = value_to_bytes(data, size)
                elif data == 0: # Manually enabled
                    if not zero_as_int:
                        raise ValueError(f"You've reached a 2nd impossible scenario!")
                    add_data = value_to_bytes(data, 1)
                else:
                    add_data = int_to_signed_bytes(data, size)          
            elif isinstance(data, float):
                add_data = struct.pack(">d" if size == 8 else ">f", data)
            elif isinstance(data, bytes):
                add_data = resp
            elif isinstance(data, datetime.datetime):
                add_data = value_to_bytes(int(data.timestamp() / 1000), 8)
            else:
                raise ValueError(f"Unsupported Value Type: {type(data)}")
            resp += add_data
    elif type_ == "container":
        for item in data:
            resp += json_to_ag(item)
    elif type_ == "map":
        for key, value in data.items():
            resp += json_to_ag(key)
            resp += json_to_ag(value)

    return resp
