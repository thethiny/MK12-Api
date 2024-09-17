import struct
from base64 import b64encode
from enum import IntEnum

from .enums import AGArray, AGBool, AGChar, AGFloat, AGInt, AGMap, AGTime, AGMapEnumReverse


def bytes_to_int(data: bytes, signed:bool) -> int:
    length = len(data)
    if length == 1:
        format = 'B'
    elif length == 2:
        format = 'H'
    elif length == 4:
        format = 'I'
    elif length == 8:
        format = 'Q'
    else:
        raise ValueError(f"Wrong Size of data: {length}")
    if signed:
        format = format.lower()
    return struct.unpack(f">{format}", data)[0]

def bytes_to_float(data: bytes) -> float:
    length = len(data)
    if length == 4:
        format = 'f'
    elif length == 8:
        format = 'd'
    else:
        raise ValueError(f"Wrong Size of data: {length}")
    return struct.unpack(f">{format}", data)[0]

def parse_bools(value_type: IntEnum):
    if value_type == AGBool.ZERO:
        return "0"
    if value_type == AGBool.NONE:
        return "None"
    if value_type == AGBool.TRUE:
        return "True"
    if value_type == AGBool.FALSE:
        return "False"
    # Not Possible
    raise ValueError("Unknown Type")


def data_to_int(data: bytes, cursor: int, length: int, signed = False):
    data = data[cursor : cursor + length]
    return bytes_to_int(data, signed)


def parse_ints(data: bytes, cursor: int, data_sub_type):
    data_length = 2 ** (data_sub_type // 2)
    is_signed = not bool(data_sub_type % 2)
    value = data_to_int(data, cursor, data_length, is_signed)
    cursor += data_length
    return str(value), cursor


def parse_strings(data: bytes, cursor: int, data_sub_type):
    if data_sub_type > 5:
        raise NotImplementedError(f"Long Long Ints are unsupported in Strings yet! {data_sub_type}")
    is_binary = data_sub_type > 2
    if is_binary:
        data_sub_type -= 3
    data_length = 2 ** data_sub_type
    string_length = data_to_int(data, cursor, data_length)
    cursor += data_length
    string_data = data[cursor : cursor + string_length]
    if is_binary:
        string_data = b64encode(string_data).decode('utf-8')
    else:
        string_data = string_data.decode("utf-8").replace('\"', '\\\"')
    cursor += string_length
    return '"' + string_data + '"', cursor


def parse_arrays(data, cursor, data_sub_type):
    data_length = 2 ** data_sub_type
    elements_count = data_to_int(data, cursor, data_length)
    cursor += data_length
    elements = []
    for _ in range(elements_count):
        element, cursor = parse_general(data, cursor)
        elements.append(element)
    return "[" + ",".join(elements) + "]", cursor


def parse_maps(data, cursor, data_sub_type):
    elements = []
    data_length = 2 ** (data_sub_type%4)
    if data_sub_type < 4:
        elements_count = data_to_int(data, cursor, data_length)
        cursor += data_length
        for _ in range(elements_count):
            key, cursor = parse_general(data, cursor)
            val, cursor = parse_general(data, cursor)
            string = f"{key}:{val}"
            elements.append(string)
    elif data_sub_type == 9:
        for i in range(data_length):
            val, cursor = parse_general(data, cursor)
            string = f'"unk{i+1}":{val}'
            elements.append(string)
    else:
        raise NotImplementedError(f"Unknown Subtype {data_sub_type} for Maps!")
    return "{" + ",".join(elements) + "}", cursor


def parse_time(data, cursor, data_sub_type):
    if data_sub_type != AGTime.EPOCH:
        raise NotImplementedError(f"Only {str(AGTime.EPOCH)} time is supported!")
    data_length = 4
    time_ = data_to_int(data, cursor, data_length)
    cursor += data_length
    return str(time_), cursor

def parse_floats(data, cursor, data_sub_type):
    data_length = 2 ** (data_sub_type + 2)
    float_value = data[cursor:cursor+data_length]
    cursor += data_length
    if data_sub_type not in [0, 1]:
        raise NotImplementedError(f"Sub Type {str(get_subtype(data_sub_type))} is not supported!")
    parsed_float = bytes_to_float(float_value)
    return str(parsed_float), cursor

def parse_general(data, cursor):
    var = data[cursor]
    value_type = get_subtype(var)
    data_type = type(value_type)
    data_sub_type = value_type.value
    
    cursor += 1
    if data_type == AGBool:
        return parse_bools(value_type), cursor
    elif data_type == AGInt:
        return parse_ints(data, cursor, data_sub_type)
    elif data_type == AGFloat:
        return parse_floats(data, cursor, data_sub_type)
    elif data_type == AGChar:
        return parse_strings(data, cursor, data_sub_type)
    elif data_type == AGTime:
        return parse_time(data, cursor, data_sub_type)
    elif data_type == AGArray:
        return parse_arrays(data, cursor, data_sub_type)
    elif data_type == AGMap:
        return parse_maps(data, cursor, data_sub_type)
    raise NotImplementedError(f"{value_type} is not yet implemented.")

def deserialize(data: bytes):
    if not data:
        return None
    cursor: int = 0
    parsed_string = ""
    string, cursor = parse_general(data, cursor)
    parsed_string += string

    return eval(parsed_string.encode("unicode-escape").decode())


def get_subtype(value) -> IntEnum:
    type_: int = value // 0x10
    subtype: int = value % 0x10
    enum_type = AGMapEnumReverse.get(type_ << 4)
    if enum_type is None:
        raise Exception(f"Couldn't map byte {value}!")
    try:
        enum_subtype: IntEnum = enum_type(subtype) # type: ignore
    except Exception as e:
        raise Exception(f"Type {enum_type} has no subtype {subtype}")
    return enum_subtype

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python3 deserialize.py <file>")
        ### Debug 
        sys.argv.append(r".\requests\1695537568.12056_GET_ssc+invoke+inbox_messages_unread\response.bin")
        # exit(1)
    with open(sys.argv[1], "rb") as f:
        data = f.read()
        # Compare first 4 bytes with magic number
        MAGIC = bytes.fromhex("E3 61 45 90")
        if data[:4] == MAGIC:
            print("Found a Save File!")
            data = data[6:]
        
        deserialized_data = deserialize(data)

    if len(sys.argv) > 2:
        save_to = sys.argv[2]
        print(f"Saving to {save_to}")
        with open(sys.argv[2], "w") as f:
            f.write(str(deserialized_data))
    else:
        print(deserialized_data)
