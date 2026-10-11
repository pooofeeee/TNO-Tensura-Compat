"""Capture existing project experiment files; never execute or modify them."""
import gzip
import hashlib
import io
import json
from pathlib import Path
import re
import subprocess
import tarfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def digest(data):
    return hashlib.sha256(data).hexdigest()


def main():
    baseline = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    roots = sorted(p for p in (ROOT/'run').iterdir() if p.is_dir() and
                   (p.name.startswith('mod-intelligence') or p.name.startswith('five-defect-repair')
                    or p.name in ('task-preflight-experiment', 'task-preflight-ab')))
    for name in ('artifacts', 'manifests', 'reports'):
        (HERE/name).mkdir(exist_ok=True)
    index = dict(schema='tno.mod_intelligence.historical_archive.v1', cutoff='2026-10-11',
                 baseline_commit=baseline, experiments=[], reports=[], exclusions=[],
                 symlink_policy='Record link identity and backing repository Git tree; never dereference.')
    signature = re.compile(rb'(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{40,}|sk-proj-[A-Za-z0-9_-]{30,}|-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----)')
    for root in roots:
        files = sorted(p for p in root.rglob('*') if p.is_file() or p.is_symlink())
        inventory = dict(experiment=root.name, original_root=root.relative_to(ROOT).as_posix(),
                         capture_baseline=baseline, entries=[])
        archive = HERE/'artifacts'/f'{root.name}.tar.gz'
        with archive.open('wb') as raw, gzip.GzipFile(filename='', mode='wb', fileobj=raw, mtime=0) as gz:
            with tarfile.open(fileobj=gz, mode='w', format=tarfile.PAX_FORMAT) as tar:
                for path in files:
                    name = path.relative_to(ROOT).as_posix()
                    if path.is_symlink():
                        target = path.resolve()
                        if not target.is_relative_to(ROOT):
                            raise ValueError(f'Unexpected external reference: {name}')
                        relative = target.relative_to(ROOT).as_posix()
                        tree = subprocess.check_output(['git', 'rev-parse', f'{baseline}:{relative}'],
                                                       cwd=ROOT, text=True).strip()
                        inventory['entries'].append(dict(path=name, type='repository_reference',
                            original_link_target=str(path.readlink()), repository_path=relative,
                            git_commit=baseline, git_tree=tree))
                        continue
                    data = path.read_bytes()
                    if signature.search(data):
                        raise ValueError(f'Credential-like material requires review: {name}')
                    entry = dict(path=name, type='file', bytes=len(data), sha256=digest(data))
                    inventory['entries'].append(entry)
                    member = tarfile.TarInfo(name)
                    member.size = len(data)
                    member.mode = 0o755 if path.stat().st_mode & 0o111 else 0o644
                    member.mtime = 0
                    tar.addfile(member, io.BytesIO(data))
        manifest = HERE/'manifests'/f'{root.name}.json'
        manifest.write_text(json.dumps(inventory, indent=2)+'\n')
        index['experiments'].append(dict(name=root.name, archive=archive.relative_to(HERE).as_posix(),
            archive_sha256=digest(archive.read_bytes()), archive_bytes=archive.stat().st_size,
            manifest=manifest.relative_to(HERE).as_posix(), manifest_sha256=digest(manifest.read_bytes()),
            files=sum(e['type']=='file' for e in inventory['entries']),
            references=sum(e['type']=='repository_reference' for e in inventory['entries']),
            original_bytes=sum(e.get('bytes', 0) for e in inventory['entries'])))
        report = root/'report.md'
        if report.exists():
            copy = HERE/'reports'/f'{root.name}.md'
            copy.write_bytes(report.read_bytes())
            index['reports'].append(dict(path=copy.relative_to(HERE).as_posix(),
                                        original=report.relative_to(ROOT).as_posix(), sha256=digest(copy.read_bytes())))
    (HERE/'artifact-index.json').write_text(json.dumps(index, indent=2)+'\n')
    lines = ['# Artifact index', '',
        'Every regular file in these 16 available project experiment directories is captured. '
        'Archives contain regular files only; symlink dependencies are recorded in manifests and backed by Git trees. '
        'Raw historical text, absolute paths, failure logs and discarded attempts are unchanged.', '',
        '| Experiment | Files | References | Compressed bytes | Evidence |',
        '| --- | ---: | ---: | ---: | --- |']
    for item in index['experiments']:
        name = item['name']
        links = f"[Archive]({item['archive']}) · [SHA-256 manifest]({item['manifest']})"
        if (HERE/'reports'/f'{name}.md').exists():
            links += f' · [Original report](reports/{name}.md)'
        lines.append(f"| {name} | {item['files']} | {item['references']} | {item['archive_bytes']:,} | {links} |")
    lines += ['', '[Machine-readable package index](artifact-index.json). '
        'Use `python3 docs/mod-intelligence-archive/verify_archive.py` to check every package/member and readable report.', '',
        'The source catalog is already committed under `docs/benchmarks/external-effects-catalog`; '
        'archives do not duplicate symlinked research trees or include third-party JARs. '
        'The `mod-intelligence-real-coding-benchmark` archive includes `discarded-attempt1/` and runner authentication-probe diagnostics.', '',
        'A preexisting, uncommitted change-request draft is preserved separately in '
        '[notes/draft-sugar-rush-change.json](notes/draft-sugar-rush-change.json). '
        'It remains a draft, not an active manifest or applied change.']
    (HERE/'artifact-index.md').write_text('\n'.join(lines)+'\n')
    print(json.dumps({'experiments':len(roots), 'files':sum(x['files'] for x in index['experiments']),
                      'compressed_bytes':sum(x['archive_bytes'] for x in index['experiments']),
                      'original_bytes':sum(x['original_bytes'] for x in index['experiments'])}))


if __name__ == '__main__':
    main()
