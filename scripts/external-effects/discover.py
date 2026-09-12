"""Over-approximate all class/method surfaces; discoveries require semantic review."""
import re
from classfile import ClassFile
from catalog_common import *

COMBAT = re.compile(r'MobEffect|MobEffects|Living(?:Damage|IncomingDamage|Heal|Death|Attack|Hurt|Tick)|'
 r'Damage(?:Source|Type)|damage|hurt|attack|heal|bleed|stun|daz|petrif|freez|frozen|'
 r'paraly|poison|wither|curse|silenc|fear|blind|darkness|knock|levitat|pull|push|'
 r'gravity|velocity|setDeltaMovement|setPos|setNoAi|stopUsingItem|disableShield|'
 r'shield|block|immune|invul|armor|Attribute|resist|exhaust|food|mana|magicule|'
 r'aura|energy|stamina|resource|stack|buildup|threshold|Cooldown|Counter|Timer|'
 r'Enchant|Skill|Spell|Ability|Curios|Accessory|Attachment|Capability|PersistentData|'
 r'EntityData|EntityEvent|Projectile|Explosion|[.]setHealth|[.]setAbsorption|'
 r'[.]addEffect|[.]removeEffect|[.]isUsingItem|[.]setSecondsOnFire|[.]igniteFor',re.I)

def scan(target):
    index=[]; candidates=[]; resources={}; failures=[]; resource_errors=[]; nested_archives=[]
    with zipfile.ZipFile(target['path']) as jar:
        for entry in sorted(jar.namelist()):
            if entry.endswith('.class'):
                data=jar.read(entry)
                try:
                    cls=ClassFile(data)
                    refs=cls.references(); strings=cls.strings()
                    memberlist=[]; methodhits=[]
                    for m in cls.methods:
                        row=dict(name=m['name'],descriptor=m['descriptor'],access=m['access'])
                        if 'code' in m:
                            ins=list(cls.instructions(m['code']))
                            row.update(code_sha256=byte_hash(m['code']),code_bytes=len(m['code']))
                            hits=[i for i in ins if isinstance(i['operand'],str) and COMBAT.search(i['operand'])]
                            if hits or COMBAT.search(m['name']+m['descriptor']):
                                methodhits.append(dict(**row,hits=hits))
                        memberlist.append(row)
                    hitrefs=[ref for ref in refs if COMBAT.search(ref)]
                    fields=[{k:v for k,v in field.items() if k!='code'} for field in cls.fields]
                    item=dict(entry=entry,sha256=byte_hash(data),name=cls.name,super=cls.super,
                        interfaces=cls.interfaces,methods=memberlist,fields=fields)
                    index.append(item)
                    if methodhits or hitrefs or COMBAT.search(cls.name+' '+str(cls.super)):
                        candidates.append(dict(entry=entry,sha256=item['sha256'],name=cls.name,
                            super=cls.super,matched_references=hitrefs,methods=methodhits,
                            strings=strings,inspection_status='UNVERIFIED',disposition=None))
                except Exception as error:
                    failures.append(dict(entry=entry,error=repr(error)))
            elif entry.endswith('.jar'):
                nested_archives.append(dict(entry=entry,sha256=byte_hash(jar.read(entry)),inspection_status='UNVERIFIED'))
            elif entry.endswith(('.mcfunction','.js','.zs','.kts','.groovy','.lua')):
                data=jar.read(entry)
                resources[entry]=dict(sha256=byte_hash(data),text=data.decode('utf-8','replace'))
            elif entry.endswith('.json') and (entry.startswith('data/') or entry.endswith('/lang/en_us.json') or 'mixin' in entry.lower()):
                data=jar.read(entry)
                try: value=json.loads(data)
                except (ValueError,UnicodeError) as error:
                    resource_errors.append(dict(entry=entry,error=repr(error))); continue
                if entry.endswith('/lang/en_us.json'):
                    value={k:v for k,v in value.items() if k.startswith(('effect.','enchantment.','death.','attribute.','item.','entity.','skill.','ability.'))}
                resources[entry]=dict(sha256=byte_hash(data),data=value)
    folder=WORK/target['key'];folder.mkdir(parents=True,exist_ok=True)
    write_json(folder/'class-index.json',index)
    write_json(folder/'candidates.json',candidates)
    write_json(folder/'resources.json',resources)
    # Small immutable per-JAR locator ledger; large derived indexes remain reproducible in run/.
    record=dict(mod_key=target['key'],jar_sha256=target['sha256'],role=target['role'],
        archive_classes=target['classes'],parsed_classes=len(index),parse_errors=failures,
        resource_parse_errors=resource_errors,nested_archives=nested_archives,
        candidate_classes=len(candidates),candidate_methods=sum(len(c['methods']) for c in candidates),
        discovery_method='Every class/member/code instruction parsed; broad combat/API/state keyword over-approximation plus JSON resources. Candidate counts are not mechanics.',
        index_artifacts=[dict(path=str((folder/name).relative_to(ROOT)).replace('\\','/'),sha256=sha256(folder/name))
                        for name in ('class-index.json','candidates.json','resources.json')],
        semantic_review='Consult native-findings and effect-catalog; this automated scan never grants semantic coverage.',coverage_complete=False,
        tool_sources={name:sha256(Path(__file__).parent/name) for name in ('classfile.py','discover.py','catalog_common.py')},
        special_surface_classes=[c['name'] for c in index if any(x in c['name'].lower() for x in ('effect','damage','mixin','capab','attach','skill','spell'))])
    write_json(OUT/'discovery'/f'{target["key"]}-scan.json',record)
    print(json.dumps({k:record[k] for k in ('mod_key','archive_classes','parsed_classes','candidate_classes','candidate_methods')})+' errors='+str(len(failures)),flush=True)
    return record

if __name__=='__main__':
    inv=read_json(OUT/'jar-inventory.json')
    results=[]
    for target in inv['targets']+inv['compat_candidates']:
        if target['status']=='UNAVAILABLE':continue
        # Base Tensura remains reference-only; do not turn its large skill catalog into new research.
        if target['role']=='BASE_TENSURA_REFERENCE':continue
        results.append(scan(target))
    write_json(OUT/'discovery-scan.json',dict(schema='tno.external_effects.discovery_scan.v1',
        status='PARTIAL',checkpoint='R2_DISCOVERY_SCAN',baseline=BASELINE,mods=results,
        semantic_coverage_complete=False,notes=['No mechanic classified from name/keyword alone.',
        'Indexes cover non-MobEffect callback, data/state, resource and source surfaces; every candidate still needs disposition.',
        'Dynamic/reflection/data-driven indirection and shared helpers require follow-up; scanner is not completeness proof.']))
