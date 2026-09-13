"""Offline integration checks: python3 -m unittest discover -s tests -v."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts/update-antigravity'


class UpdaterTests(unittest.TestCase):
    def test_verified_update_and_failures(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            control = root / 'pkg/DEBIAN'
            control.mkdir(parents=True)
            arch = subprocess.check_output(['dpkg', '--print-architecture'], text=True).strip()
            control.joinpath('control').write_text(
                f'Package: antigravity\nVersion: 0:2.3.1-1\nArchitecture: {arch}\n'
                'Maintainer: Test <test@example.org>\nDescription: Test fixture\n'
            )
            deb = root / 'package.deb'
            subprocess.run(['dpkg-deb', '--build', str(control.parent), str(deb)], check=True, capture_output=True)
            name = f'antigravity_2.3.1_{arch}.deb'
            checksum = root / 'checksum'
            checksum.write_text(f'{hashlib.sha256(deb.read_bytes()).hexdigest()}  {name}\n')
            prefix = 'https://github.com/MohamedElashri/antigravity-linux/releases/download/antigravity-v2.3.1/'
            release = dict(draft=False, prerelease=False, tag_name='antigravity-v2.3.1', assets=[
                dict(name=n, browser_download_url=prefix+n)
                for n in [name, 'checksums_antigravity_2.3.1.txt']])
            # A newer incomplete release must not hide the usable release.
            incomplete = dict(release, tag_name='antigravity-v9.0.0', assets=[])
            root.joinpath('releases').write_text(json.dumps([incomplete, release]))
            binpath = root / 'bin'
            binpath.mkdir()
            mocks = {
                'curl': '''#!/bin/bash
for arg in "$@"; do
 case "$arg" in
  https://api.github.com/*) source="$FIXTURE/releases" ;;
  https://github.com/*.deb) source="$FIXTURE/package.deb" ;;
  https://github.com/*.txt) source="$FIXTURE/checksum" ;;
 esac
 if [[ ${previous:-} == -o ]]; then dest="$arg"; fi
 previous="$arg"
done
cp "$source" "$dest"
''',
                'dpkg-query': '''#!/bin/bash
[[ -n ${MOCK_INSTALLED:-} ]] || exit 1
if [[ "$*" == *Status* ]]; then printf 'install ok installed'; else printf '%s' "$MOCK_INSTALLED"; fi
''',
                'apt-get': '#!/bin/bash\nexit 99\n',
            }
            for name, content in mocks.items():
                path = binpath / name
                path.write_text(content)
                path.chmod(0o755)
            env = dict(os.environ, PATH=f'{binpath}:'+os.environ['PATH'], FIXTURE=str(root), MOCK_INSTALLED='')

            def run():
                return subprocess.run([str(SCRIPT), '--check'], env=env, capture_output=True, text=True)

            result = run()
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn('Check only; verified package', result.stdout)
            for version in ['0:2.3.1-1', '0:3.0.0-1']:
                env['MOCK_INSTALLED'] = version
                result = run()
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertIn('No upgrade', result.stdout)
            checksum.write_text('0'*64 + f'  antigravity_2.3.1_{arch}.deb\n')
            result = run()
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('Checksum mismatch', result.stderr)


if __name__ == '__main__':
    unittest.main()
