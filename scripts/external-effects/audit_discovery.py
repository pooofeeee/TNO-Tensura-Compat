"""Summarize reproducible scan and decompiler caveats without claiming discovery complete."""
import re
from catalog_common import *

def audit():
    scan=read_json(OUT/'discovery-scan.json')
    inv=read_json(OUT/'jar-inventory.json')
    expected={t['key']:t for t in inv['targets']+inv['compat_candidates'] if t['status']!='UNAVAILABLE' and t['role']!='BASE_TENSURA_REFERENCE'}
    assert {r['mod_key'] for r in scan['mods']}==set(expected)
    for row in scan['mods']:
        assert row['jar_sha256']==expected[row['mod_key']]['sha256']
        assert row['archive_classes']==row['parsed_classes']+len(row['parse_errors'])
        assert not row['parse_errors'], row['mod_key']
        for artifact in row['index_artifacts']:
            assert sha256(ROOT/artifact['path'])==artifact['sha256']
        for name,digest in row['tool_sources'].items():
            assert sha256(Path(__file__).parent/name)==digest
    decompilation=read_json(OUT/'decompilation-provenance.json')
    assert {r['mod_key'] for r in decompilation['results']}==set(expected)
    anomalies=[]
    for row in decompilation['results']:
        folder=WORK/row['mod_key']; log=folder/'decompile.log'
        assert sha256(log)==row['log_sha256']
        assert row['jar_sha256']==expected[row['mod_key']]['sha256']
        markers=[]
        for source in (folder/'source').rglob('*.java'):
            for number,line in enumerate(source.read_text(encoding='utf-8').splitlines(),1):
                if re.search(r"couldn't be decompiled|Couldn't be decompiled|\$VF: Could",line):
                    markers.append(dict(path=source.relative_to(ROOT).as_posix(),line=number,text=line.strip()))
        lines=[line.strip() for line in log.read_text(encoding='utf-8').splitlines() if re.search(r'ERROR|WARN|could not|failed',line,re.I)]
        if lines or markers or row['exit_code']!=0:
            anomalies.append(dict(mod_key=row['mod_key'],exit_code=row['exit_code'],log_messages=lines,
                source_error_markers=markers,resolution='UNVERIFIED: inspect relevant bytecode; do not trust failed decompiled bodies.'))
    return dict(schema='tno.external_effects.discovery_audit.v1',status='PASS',checkpoint='R2a_PARTIAL',baseline=BASELINE,
        external_targets_scanned=sum(t['role']!='BASE_TENSURA_REFERENCE' and t['status']!='UNAVAILABLE' for t in inv['targets']),
        reference_only_targets=1,compat_candidates_scanned=len(inv['compat_candidates']),
        parsed_classes=sum(r['parsed_classes'] for r in scan['mods']),
        candidate_classes=sum(r['candidate_classes'] for r in scan['mods']),
        candidate_methods=sum(r['candidate_methods'] for r in scan['mods']),
        class_parse_errors=sum(len(r['parse_errors']) for r in scan['mods']),
        resource_parse_errors=[dict(mod_key=r['mod_key'],errors=r['resource_parse_errors']) for r in scan['mods'] if r['resource_parse_errors']],
        nested_archives=[dict(mod_key=r['mod_key'],archives=r['nested_archives']) for r in scan['mods'] if r['nested_archives']],
        decompiler_anomalies=anomalies,semantic_coverage_complete=False,
        note='PASS means scan identity/count/index provenance checks passed. It does not mean every mechanic or nested archive is reviewed.')

if __name__=='__main__':
    report=audit();write_json(OUT/'discovery-audit.json',report)
    print(json.dumps({k:v for k,v in report.items() if k not in ('nested_archives','decompiler_anomalies')},indent=2))
    print('Decompiler anomaly JARs:',[x['mod_key'] for x in report['decompiler_anomalies']])
    print('Nested archive parent JARs:',[x['mod_key'] for x in report['nested_archives']])
