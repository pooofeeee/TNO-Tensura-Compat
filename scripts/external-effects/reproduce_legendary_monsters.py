"""Reproduce saved Legendary Monsters evidence with explicitly supplied pinned artifacts.

This composes existing extractors; it does not regenerate authored semantics.
--extra-only extends an unchanged previous full reproduction receipt with the
closure lightning/loader checks, avoiding another expensive template extraction.
"""
import argparse
import zipfile
from pathlib import Path

from catalog_common import OUT, read_json, write_json, sha256, byte_hash
from native_evidence import collect
from collect_combat_census import collect as census_collect
from index_native_fields import index, pack
from group_native_methods import group
from vanilla_reference import prepare_raw
from classfile import ClassFile
from collect_cataclysm_ignited_revenant_offense import instructions


def reproduce(jar, vanilla, loader_dir, extra_only=False):
    report = dict(status='PASS', native_jar_sha256=sha256(jar), reproduced=[])
    output = OUT/'legendary_monsters-reproduction.json'
    if extra_only:
        report = read_json(output)
        assert report['status']=='PASS' and report['native_jar_sha256']==sha256(jar)
        for receipt in report['reproduced']:
            assert receipt['sha256']==sha256(OUT/receipt['file'])

    def receipt(name, comparison):
        report['reproduced'] = [r for r in report['reproduced'] if r['file']!=name]
        report['reproduced'].append(dict(file=name, sha256=sha256(OUT/name), comparison=comparison))
        print('PASS', name, flush=True)

    def equal(name, actual):
        assert actual==read_json(OUT/name), ('reproduction mismatch', name)
        receipt(name, 'EXACT_STRUCTURED_EQUALITY')

    if not extra_only:
        for part in ('core', 'ancillary', 'resources', 'structures'):
            name=f'native-evidence/legendary_monsters-{part}.json'
            equal(name, collect(read_json(OUT/f'native-specifications/legendary_monsters-{part}.json'),
                                {'legendary_monsters':jar}))
        census=read_json(OUT/'legendary_monsters-combat-census.json')
        equal('legendary_monsters-combat-census.json', census_collect('legendary_monsters', jar))
        fields=read_json(OUT/'legendary_monsters-native-field-use-index.json')
        selection={(m['entry'], m['method'], m['descriptor']) for m in fields['selection']}
        with zipfile.ZipFile(jar) as archive:
            equal('legendary_monsters-native-field-use-index.json', pack(index(census, archive.read, selection, True)))
        for stem, part in [('body', 'core'), ('ancillary-body', 'ancillary')]:
            evidence=OUT/f'native-evidence/legendary_monsters-{part}.json'
            name=f'legendary_monsters-{stem}-groups.json'
            result=group(census, read_json(evidence), jar)
            if 'input_hashes' in read_json(OUT/name):
                result['input_hashes']=dict(census=sha256(OUT/'legendary_monsters-combat-census.json'), evidence=sha256(evidence))
            equal(name, result)

    for spec in sorted((OUT/'vanilla-specifications').glob('legendary-monsters-*.json')):
        if extra_only and spec.name!='legendary-monsters-lightning.json':
            continue
        equal('vanilla-evidence/'+spec.name, prepare_raw(read_json(spec), vanilla/'client.jar',
              vanilla/'client_mappings.txt', vanilla/'version.json'))

    loader=loader_dir/'neoforge-21.1.244-userdev.jar'
    with zipfile.ZipFile(loader) as archive:
        for name in ('legendary_monsters-status-loader-patches.json',
                     'legendary_monsters-goal-loader-patch.json',
                     'legendary_monsters-closure-loader-patches.json'):
            document=read_json(OUT/name)
            assert document['jar_sha256']==sha256(loader)
            for patch in document['patches']:
                raw=archive.read(patch['entry'])
                assert byte_hash(raw)==patch['entry_sha256'] and raw.decode()==patch['text']
            assert all(e not in archive.NameToInfo for e in document.get('absent_entries', []))
            receipt(name, 'EXACT_PATCH_BYTES_AND_ABSENCE')
        name='reference-evidence/arphex-native-template-loading-244.json'
        for witness in read_json(OUT/name)['witnesses']:
            raw=archive.read(witness['entry'])
            assert witness['archive_sha256']==sha256(loader) and byte_hash(raw)==witness['entry_sha256']
            if 'text' in witness:
                assert raw.decode()==witness['text']
        receipt(name, 'EXACT_EXISTING_DEPENDENCY_ENTRY_BYTES')

    name='legendary_monsters-item-attribute-loader.json'
    document=read_json(OUT/name)
    for artifact in document['artifacts']:
        assert sha256(loader_dir/artifact['file'])==artifact['sha256']
    for witness in document['witnesses']:
        with zipfile.ZipFile(loader_dir/witness['artifact']) as archive:
            raw=archive.read(witness['entry'])
        assert byte_hash(raw)==witness['entry_sha256']
        if 'text' in witness:
            assert raw.decode()==witness['text']
        else:
            parsed=ClassFile(raw)
            assert parsed.name==witness['class_name']
            for method in witness['methods']:
                matches=[m for m in parsed.methods if m['name']==method['name'] and m['descriptor']==method['descriptor']]
                assert len(matches)==1
                code=matches[0].get('code', b'')
                assert byte_hash(code)==method['code_sha256'] and instructions(parsed, code)==method['instructions']
    receipt(name, 'EXACT_SOURCE_PATCH_CLASS_AND_METHOD_BYTES')
    report['original_discovery_index_recovery']='BYTE_IDENTICAL'
    write_json(output, report)
    print('COMPLETE', len(report['reproduced']), flush=True)
    return report


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--jar', type=Path, required=True)
    parser.add_argument('--vanilla', type=Path, required=True)
    parser.add_argument('--loader-dir', type=Path, required=True)
    parser.add_argument('--extra-only', action='store_true')
    args=parser.parse_args()
    reproduce(args.jar, args.vanilla, args.loader_dir, args.extra_only)
