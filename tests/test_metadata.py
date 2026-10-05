import datetime
import io
import struct
import unittest

from project_metadata import read_metadata
from test_zip_import import flp_bytes


def project(events):
    return struct.pack('<4sIhHH', b'FLhd', 6, 0, 0, 96) + b'FLdt' + struct.pack('<I', len(events)) + events


class MetadataTests(unittest.TestCase):
    def test_legacy(self):
        self.assertEqual(read_metadata(io.BytesIO(flp_bytes())).time_spent,
                         datetime.timedelta(hours=2.5))

    def test_fl26_extended_events(self):
        version = b'26.1.0.5530\0'
        events = bytes([199, len(version)]) + version
        events += b'\xac' + struct.pack('<I', 0xc0000101) + b'\x04test'
        events += b'\xac' + struct.pack('<I', 256) + b'\x00'
        events += b'\xed\x10' + struct.pack('<dd', 45000, 2.5 / 24)
        events += b'\xd5\x03bad'
        self.assertEqual(read_metadata(io.BytesIO(project(events))).time_spent,
                         datetime.timedelta(hours=2.5))

    def test_invalid_metadata_and_truncation(self):
        for events in (b'\xed\x10short', b'\xed\x01x',
                       b'\xed\x10' + struct.pack('<dd', 45000, -1),
                       b'\xed\x10' + struct.pack('<dd', 45000, float('nan')),
                       b'\xd5\x80\x80\x80\x80\x80', b'\x0c\x00'):
            with self.subTest(events=events), self.assertRaises(ValueError):
                read_metadata(io.BytesIO(project(events)))
