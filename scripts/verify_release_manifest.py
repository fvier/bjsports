"""Confere um pacote em disco, sem importar a aplicação ou acessar seu banco."""
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import re


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('root', type=Path, help='Raiz da fonte ou /app no contêiner publicado')
    parser.add_argument('manifest', type=Path, help='JSON: caminho relativo -> SHA-256, ou null para remoção')
    args = parser.parse_args()
    expected = json.loads(args.manifest.read_text())
    if not isinstance(expected, dict) or not expected:
        parser.error('O manifesto deve ser um objeto não vazio.')
    mismatches = []
    for name, value in expected.items():
        relative = PurePosixPath(name)
        if relative.is_absolute() or '..' in relative.parts or not relative.parts:
            parser.error(f'Caminho inválido: {name}')
        if value is not None and (not isinstance(value, str) or not re.fullmatch(r'[0-9a-f]{64}', value)):
            parser.error(f'SHA-256 inválido: {name}')
        path = args.root / relative
        if value is None:
            matches = not path.exists() and not path.is_symlink()
        else:
            matches = path.is_file() and hashlib.sha256(path.read_bytes()).hexdigest() == value
        if not matches:
            mismatches.append(name)
    print(json.dumps({'checked': len(expected), 'mismatches': mismatches}, ensure_ascii=False))
    return bool(mismatches)


if __name__ == '__main__':
    raise SystemExit(main())
