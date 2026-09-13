"""Catálogo do firmware: fonte versionada e binário somente com manifesto válido."""
import hashlib
import io
import json
import re
import zipfile
from pathlib import Path

SOURCE_FILES = ('platformio.ini', 'README.md', 'esp32_catraca/esp32_catraca.ino',
                'esp32_catraca/access_policy.h')


def firmware_info(root):
    root = Path(root)
    source = root / 'esp32_catraca/esp32_catraca.ino'
    version = re.search(r'FIRMWARE_VERSION\s*=\s*"([^"]+)"', source.read_text()).group(1)
    binary = root / 'esp32_catraca/firmware.bin'
    available = False
    try:
        manifest = json.loads((root / 'esp32_catraca/firmware.json').read_text())
        available = (manifest['version'] == version
                     and manifest['sha256'] == hashlib.sha256(binary.read_bytes()).hexdigest()
                     and all(manifest['sources'][name] == hashlib.sha256((root / name).read_bytes()).hexdigest()
                             for name in SOURCE_FILES))
    except (OSError, ValueError, KeyError, TypeError):
        pass
    return {'version': version, 'bin_exists': available}


def source_archive(root):
    output = io.BytesIO()
    with zipfile.ZipFile(output, 'w', zipfile.ZIP_DEFLATED) as archive:
        for name in SOURCE_FILES:
            archive.write(Path(root) / name, 'bjsports-firmware/' + name)
    output.seek(0)
    return output
