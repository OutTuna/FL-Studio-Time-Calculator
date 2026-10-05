from dataclasses import dataclass
import datetime
import math
import struct


@dataclass(frozen=True)
class ProjectMetadata:
    created_on: datetime.datetime
    time_spent: datetime.timedelta


def read_metadata(stream):
    data = stream.read()
    if len(data) < 22:
        raise ValueError('Incomplete FLP header')
    magic, header_size, file_format, _, ppq = struct.unpack_from('<4sIhHH', data)
    if magic != b'FLhd' or header_size != 6 or file_format != 0 or ppq == 0:
        raise ValueError('Invalid FLP header')
    if data[14:18] != b'FLdt' or struct.unpack_from('<I', data, 18)[0] != len(data) - 22:
        raise ValueError('Invalid FLP data chunk size')
    position = 22
    version = None
    timestamp = None

    def take(size):
        nonlocal position
        if size < 0 or position + size > len(data):
            raise ValueError('Truncated FLP event')
        value = data[position:position + size]
        position += size
        return value

    def variable_size():
        value = 0
        for shift in range(0, 35, 7):
            byte = take(1)[0]
            value |= (byte & 127) << shift
            if byte < 128:
                return value
        raise ValueError('Invalid FLP event length')

    while position < len(data):
        event_id = take(1)[0]
        if event_id == 172 and version is not None and version >= 26:
            take(4)
            size = variable_size()
        elif event_id >= 192:
            size = variable_size()
        else:
            size = 1 if event_id < 64 else 2 if event_id < 128 else 4
        value = take(size)
        if event_id == 199:
            version = int(value.decode('ascii').rstrip('\0').split('.')[0])
        elif event_id == 237:
            if len(value) != 16:
                raise ValueError('Invalid project time metadata')
            timestamp = struct.unpack('<dd', value)
    if timestamp is None:
        raise ValueError('Project has no time metadata')
    created, spent = timestamp
    if not math.isfinite(created) or not math.isfinite(spent) or spent < 0:
        raise ValueError('Invalid project time metadata')
    return ProjectMetadata(
        datetime.datetime(1899, 12, 30) + datetime.timedelta(days=created),
        datetime.timedelta(days=spent),
    )
