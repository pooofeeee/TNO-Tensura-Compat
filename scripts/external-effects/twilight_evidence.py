"""Incremental selected witnesses for Twilight; reuse protected methods/resources."""
from catalog_common import *
from classfile import ClassFile
from native_evidence import collect as collect_native
from selected_reference import collect as collect_reference
from vanilla_reference import prepare


def native(batch, classes, resources=()):
    inventory=read_json(OUT/'jar-inventory.json')
    target=next(t for t in inventory['targets'] if t['key']=='twilightforest')
    known={}
    for p in sorted((OUT/'native-evidence').glob('*.json')):
        if p.stem==batch: continue
        for w in read_json(p).get('witnesses',[]):
            if w.get('mod_key')!='twilightforest': continue
            known.setdefault(w['entry'],[]).append((p.name,w))
    specs=[]
    with zipfile.ZipFile(target['path']) as jar:
        for short, wanted in classes.items():
            entry='twilightforest/'+short+'.class'
            cls=ClassFile(jar.read(entry))
            allnames={m['name'] for m in cls.methods}
            wanted=allnames if wanted==['*'] else set(wanted)
            assert wanted<=allnames,(entry,wanted-allnames)
            prior={m['name'] for _,w in known.get(entry,[]) for m in w.get('methods',[])}
            missing=sorted(wanted-prior)
            if missing: specs.append(dict(id='tf:'+short,mod_key='twilightforest',entry=entry,methods=missing))
        for entry in resources:
            if entry not in known: specs.append(dict(id='tf:data:'+entry,mod_key='twilightforest',entry=entry))
    document=dict(schema='tno.external_effects.native_specification.v1',baseline=BASELINE,
                  scope='Selected incremental Twilight semantic witnesses; previously pinned methods/resources reused.',evidence_specifications=specs)
    write_json(OUT/'native-specifications'/f'{batch}.json',document)
    result=collect_native(document)
    write_json(OUT/'native-evidence'/f'{batch}.json',result)
    return len(result['witnesses'])


def references(batch, raw_classes, loader_classes, hook_classes=None):
    raw_known={}; loader_known={}
    for p in sorted((OUT/'vanilla-specifications').glob('*.json')):
        if p.stem==batch:continue
        for c,ms in read_json(p).get('classes',{}).items():raw_known.setdefault(c,set()).update(ms)
    for p in sorted((OUT/'reference-specifications').glob('*.json')):
        if p.stem==batch+'-244':continue
        for a in read_json(p).get('archives',[]):
            if '/21.1.244/' not in a['path'].replace('\\','/'):continue
            for c,ms in a.get('classes',{}).items():loader_known.setdefault(c,set()).update(ms)
    raw_missing={c:sorted(set(ms)-raw_known.get(c,set())) for c,ms in raw_classes.items()}
    raw_missing={c:ms for c,ms in raw_missing.items() if ms}
    raw_spec=dict(classes=raw_missing,resources=[])
    write_json(OUT/'vanilla-specifications'/f'{batch}.json',raw_spec)
    raw=prepare(raw_spec)
    write_json(OUT/'vanilla-evidence'/f'{batch}.json',raw)
    template=read_json(OUT/'reference-specifications/vv-loader-244.json')
    archives=[]; raw_routing=[]
    for suffix,classes in [('client.jar',loader_classes),('universal.jar',hook_classes or {})]:
        if not classes:continue
        a=next(a for a in template['archives'] if a['path'].endswith(suffix))
        with zipfile.ZipFile(a['path']) as jar:
            available=set(jar.namelist())
        for c in classes:
            if c not in available:
                assert suffix=='client.jar',c
                raw_routing.append(dict(entry=c,absent_from=a['path'],archive_sha256=a['sha256'],authority='Raw Minecraft1.21.1; no replacement class in installed patched client archive'))
        missing={c:sorted(set(ms)-loader_known.get(c,set())) for c,ms in classes.items() if c in available}
        missing={c:ms for c,ms in missing.items() if ms}
        if missing:archives.append(dict(path=a['path'],sha256=a['sha256'],classes=missing,resources=[]))
    spec=dict(id=batch+'-244',scope='Exact installed NeoForge21.1.244 supplemental Twilight comparisons; reused earlier witnesses are not recopied.',archives=archives)
    write_json(OUT/'reference-specifications'/f'{batch}-244.json',spec)
    result=collect_reference(spec,source_aids=True)
    write_json(OUT/'reference-evidence'/f'{batch}-244.json',result)
    write_json(OUT/'reference-routing'/f'{batch}.json',dict(baseline=BASELINE,raw_fallbacks=raw_routing))
    return dict(raw_classes=len(raw['classes']),loader_classes=len(result['witnesses']))


def native_refs(*shorts):
    result=[]
    wanted={'twilightforest/'+s+'.class' for s in shorts}
    for p in sorted((OUT/'native-evidence').glob('*.json')):
        for w in read_json(p).get('witnesses',[]):
            if w.get('mod_key')=='twilightforest' and w['entry'] in wanted:
                result.append(dict(evidence_file='native-evidence/'+p.name,witness_id=w['id'],entry=w['entry'],methods=[m['name'] for m in w.get('methods',[])]))
    assert {r['entry'] for r in result}==wanted,wanted-{r['entry'] for r in result}
    return result
