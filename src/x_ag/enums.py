from enum import EnumMeta, IntEnum
from typing import Dict

class AGBool(IntEnum):
    # 0x00
    ZERO = 0
    NONE = 1
    TRUE = 2
    FALSE = 3


class AGInt(IntEnum):
    # 0x10
    INT8 = 0
    UINT8 = 1
    INT16 = 2
    UINT16 = 3
    INT32 = 4
    UINT32 = 5
    INT64 = 6
    UINT64 = 7


class AGFloat(IntEnum):
    # 0x20
    FLOAT = 0
    DOUBLE = 1


class AGChar(IntEnum):
    # 0x30
    CHAR8 = 0
    CHAR16 = 1
    CHAR32 = 2
    BYTES8 = 3
    BYTES16 = 4
    BYTES32 = 5
    LONGLONGINT = 6


class AGTime(IntEnum):
    # 0x40 # 4 Bytes Datetime::DateTime
    EPOCH = 0


class AGArray(IntEnum):
    # 0x50
    ARRAY8 = 0
    ARRAY16 = 1
    ARRAY32 = 2
    ARRAY64 = 3


class AGMap(IntEnum):
    # 0x60
    MAP8 = 0
    MAP16 = 1
    MAP32 = 2
    MAP64 = 3
    CompressedObject = 7 # Compressed Object. 1 byte compression type, then remaining bytes. If remaining bytes are not of type 8 (AGChar Binary) then compression disabled. So far only compression type ZLIB (0x1) exists.
    MAPU1 = 8 # LocalizedString
    Calendar = 9 # CalendarControlled # Buffer contains 2 objects. Parse objects 1 and 2. Remaining unimplemented yet.
    
class Unknown70(IntEnum):
    # 0x70
    UNK1 = 0 # HydraReference: Combination of 3 binaries in a row (AGChar Binary). The first 2 binaries are first converted into strings (AGChar Binary -> AGChar Char)
    UNK2 = 1 # CalendarControlledPoejctions #  Calendar event single object


AGMapEnum: Dict[EnumMeta, int] = {
    AGBool: 0x00,
    AGInt: 0x10,
    AGFloat: 0x20,
    AGChar: 0x30,
    AGTime: 0x40,
    AGArray: 0x50,
    AGMap: 0x60,
}

AGMapEnumReverse = {v:k for k, v in AGMapEnum.items()}

def enum_to_value(item: IntEnum):
    enum_type = type(item)
    enum_base = AGMapEnum[enum_type]
    enum_offset = item.value
    return enum_base + enum_offset
