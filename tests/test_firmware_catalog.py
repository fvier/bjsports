import hashlib
import json
from pathlib import Path
import tempfile
import unittest
import zipfile
from firmware_catalog import SOURCE_FILES, firmware_info, source_archive


class FirmwareCatalogTest(unittest.TestCase):
    def test_zip_contains_complete_project(self):
        with zipfile.ZipFile(source_archive('firmware')) as archive:
            self.assertEqual(set(archive.namelist()), {'bjsports-firmware/' + name for name in SOURCE_FILES})

    def test_binary_requires_matching_manifest_and_sources(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for name in SOURCE_FILES:
                target = root / name
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes((Path('firmware') / name).read_bytes())
            binary = root / 'esp32_catraca/firmware.bin'
            binary.write_bytes(b'test-artifact')
            self.assertFalse(firmware_info(root)['bin_exists'])
            manifest = {'version': 'v2.2.0', 'sha256': hashlib.sha256(binary.read_bytes()).hexdigest(),
                        'sources': {name: hashlib.sha256((root / name).read_bytes()).hexdigest() for name in SOURCE_FILES}}
            (binary.parent / 'firmware.json').write_text(json.dumps(manifest))
            self.assertTrue(firmware_info(root)['bin_exists'])
            binary.write_bytes(b'corrupted')
            self.assertFalse(firmware_info(root)['bin_exists'])
            binary.write_bytes(b'test-artifact')
            (root / 'esp32_catraca/access_policy.h').write_text('changed')
            self.assertFalse(firmware_info(root)['bin_exists'])
