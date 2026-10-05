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

    def test_extended_events(self):
        for version in (b'25.2.4.5242\0', b'25.2.5.5319\0', b'26.1.0.5530\0'):
            with self.subTest(version=version):
                events = bytes([199, len(version)]) + version
                events += b'\xac' + struct.pack('<I', 0xc0000101) + b'\x04test'
                events += b'\xac' + struct.pack('<I', 256) + b'\x00'
                events += b'\xed\x10' + struct.pack('<dd', 45000, 2.5 / 24)
                events += b'\xd5\x03bad'
                self.assertEqual(read_metadata(io.BytesIO(project(events))).time_spent,
                                 datetime.timedelta(hours=2.5))

    def test_legacy_event_172(self):
        for version in (b'12.5.1\0', b'19.0.0\0', b'20.0.0\0', b'20.6.2.1549\0',
                        b'20.9.2.2963\0', b'21.0.3.3517\0', b'21.2.3.4004\0',
                        b'24.2.2.4597\0', b'25.1.0\0'):
            with self.subTest(version=version):
                events = bytes([199, len(version)]) + version
                events += b'\xac' + struct.pack('<I', 123)
                events += b'\xc2\x03\xff\x00\xfe'
                events += b'\x0c\x00' * 600
                events += b'\xed\x10' + struct.pack('<dd', 45000, 2.5 / 24)
                self.assertEqual(read_metadata(io.BytesIO(project(events))).time_spent,
                                 datetime.timedelta(hours=2.5))

    def test_zero_time_in_old_project(self):
        events = b'\xc7\x0719.0.0\0'
        events += b'\xed\x10' + struct.pack('<dd', 43466, 0)
        result = read_metadata(io.BytesIO(project(events)))
        self.assertEqual(result.time_spent, datetime.timedelta(0))
        self.assertEqual(result.created_on, datetime.datetime(2019, 1, 1))

    def test_invalid_metadata_and_truncation(self):
        for events in (b'\xed\x10short', b'\xed\x01x',
                       b'\xed\x10' + struct.pack('<dd', 45000, -1),
                       b'\xed\x10' + struct.pack('<dd', 45000, float('nan')),
                       b'\xd5\x80\x80\x80\x80\x80', b'\x0c\x00'):
            with self.subTest(events=events), self.assertRaises(ValueError):
                read_metadata(io.BytesIO(project(events)))
