import datetime
import importlib.util
import os
from pathlib import Path
import struct
import tempfile
import unittest
import zipfile

from project_sources import discover_projects


def flp_bytes():
    version = b'20.0.0\0'
    events = bytes([199, len(version)]) + version
    events += b'\x0c\x00' * 600
    events += bytes([237, 16]) + struct.pack('<dd', 45000, 2.5 / 24)
    return struct.pack('<4sIhHH', b'FLhd', 6, 0, 0, 96) + b'FLdt' + struct.pack('<I', len(events)) + events


class ZipImportTests(unittest.TestCase):
    def test_discovery_and_streams(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / 'raw.FLP').write_bytes(flp_bytes())
            with zipfile.ZipFile(root / 'beat.ZIP', 'w', zipfile.ZIP_DEFLATED) as z:
                z.writestr('nested/beat.FLP', flp_bytes())
                z.writestr('second.flp', flp_bytes())
                z.writestr('autosave.flp', flp_bytes())
                z.writestr('sample.wav', b'sample')
            (root / 'broken.zip').write_bytes(b'broken')
            with zipfile.ZipFile(root / 'empty.zip', 'w') as z:
                z.writestr('sample.wav', b'sample')
            sources, errors = discover_projects(root)
            self.assertEqual(len(sources), 3)
            self.assertEqual(len(errors), 2)
            before = sorted(p.relative_to(root) for p in root.rglob('*'))
            from project_metadata import read_metadata
            for source in sources:
                with source.open() as stream:
                    project = read_metadata(stream)
                self.assertEqual(project.time_spent, datetime.timedelta(hours=2.5))
                self.assertIsNotNone(project.created_on)
            self.assertEqual(before, sorted(p.relative_to(root) for p in root.rglob('*')))

    def test_gui_import_and_failure(self):
        from PySide6.QtWidgets import QApplication, QFileDialog
        from unittest.mock import patch
        app = QApplication.instance() or QApplication([])
        spec = importlib.util.spec_from_file_location('calculator_gui', '__main__.py')
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        window = module.Window()
        with tempfile.TemporaryDirectory() as folder:
            with zipfile.ZipFile(Path(folder) / 'beats.zip', 'w') as z:
                z.writestr('a/beat.flp', flp_bytes())
                z.writestr('b/beat.flp', flp_bytes())
                z.writestr('bad.flp', b'bad')
            with patch.object(QFileDialog, 'getExistingDirectory', return_value=folder):
                window.load_folders()
            self.assertEqual(window.total_num_files.text(), '2')
            self.assertEqual(window.total_time_hours.text(), '5.00')
            window.tabs.setCurrentIndex(1)
            window.update_visuals()
            self.assertTrue(all(p.tree_item.treeWidget() is window.filetree.tree for p in window.flp_objects))
            self.assertEqual(window.total_time_hours.text(), '5.00')
        window.close()


if __name__ == '__main__':
    unittest.main()
