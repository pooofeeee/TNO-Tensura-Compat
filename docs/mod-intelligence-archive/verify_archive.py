"""Verify published archive hashes and safe member paths without extracting."""
import hashlib
import json
from pathlib import Path, PurePosixPath
import subprocess
import tarfile

HERE = Path(__file__).resolve().parent


def sha(data):
    return hashlib.sha256(data).hexdigest()


def require(condition, message):
    if not condition:
        raise ValueError(message)


def local(name):
    path = (HERE/name).resolve()
    require(path.is_relative_to(HERE) and path.is_file(), f'Invalid archive path: {name}')
    return path


def main():
    index = json.loads((HERE/'artifact-index.json').read_text())
    count = 0
    references = {}
    for package in index['experiments']:
        archive, manifest = local(package['archive']), local(package['manifest'])
        require(sha(archive.read_bytes()) == package['archive_sha256'], f'Archive hash: {archive}')
        require(sha(manifest.read_bytes()) == package['manifest_sha256'], f'Manifest hash: {manifest}')
        inventory = json.loads(manifest.read_text())
        for entry in inventory['entries']:
            if entry['type'] == 'repository_reference':
                key = (entry['git_commit'], entry['repository_path'])
                if key not in references:
                    references[key] = subprocess.check_output(
                        ['git', 'rev-parse', f'{key[0]}:{key[1]}'], cwd=HERE, text=True).strip()
                require(references[key] == entry['git_tree'], f'Git reference mismatch: {entry["path"]}')
        files = {e['path']:e for e in inventory['entries'] if e['type']=='file'}
        require(len(files) == package['files'], 'File count mismatch')
        with tarfile.open(archive, 'r:gz') as tar:
            seen = set()
            for member in tar:
                name = PurePosixPath(member.name)
                require(member.isfile() and not name.is_absolute() and '..' not in name.parts,
                        f'Unsafe archive member: {member.name}')
                require(member.name in files and member.name not in seen, f'Unexpected member: {member.name}')
                expected = files[member.name]
                data = tar.extractfile(member).read()
                require(len(data) == expected['bytes'] and sha(data) == expected['sha256'],
                        f'Member mismatch: {member.name}')
                seen.add(member.name)
                count += 1
            require(seen == set(files), f'Missing members in {archive}')
    for report in index['reports']:
        require(sha(local(report['path']).read_bytes()) == report['sha256'], f'Report mismatch: {report["path"]}')
    print(json.dumps({'status':'PASS','experiments':len(index['experiments']),
                      'regular_files':count,'reports':len(index['reports']),
                      'backing_git_trees':len(references)}))


if __name__ == '__main__':
    main()
