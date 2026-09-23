"""Validate preserved partial multiplayer source evidence; not semantic acceptance."""
from catalog_common import *
from classfile import ClassFile
from selected_reference import collect
from vanilla_reference import prepare

FOLDER=OUT/'partial-evidence/twilightforest-multiplayer'
WORDS=['MULTIPLAYER_FIGHT','group_health_boost','multiplayerFightAdjuster','MultiplayerBased','MultiplayerInclusivity','HURT_BOSS']


def census():
    target=next(t for t in read_json(OUT/'jar-inventory.json')['targets'] if t['key']=='twilightforest')
    hits=[];resources=[]
    assert sha256(target['path'])==target['sha256']
    with zipfile.ZipFile(target['path']) as jar:
        for entry in jar.namelist():
            b=jar.read(entry)
            if entry.endswith('.class') and any(w.encode() in b for w in WORDS):
                c=ClassFile(b)
                for m in c.methods:
                    ii=list(c.instructions(m.get('code',b'')))
                    match=[i for i in ii if any(w in str(i['operand']) for w in WORDS)]
                    if match:hits.append(dict(entry=entry,sha256=byte_hash(b),method=m['name'],instructions=match))
        for entry,row in read_json(WORK/'twilightforest/resources.json').items():
            if entry.startswith('data/') and any(w in entry+' '+str(row.get('data','')) for w in ['multiplayer','hurt_boss']):
                assert byte_hash(jar.read(entry))==row['sha256']
                if 'data' in row:assert json.loads(jar.read(entry))==row['data']
                resources.append(dict(entry=entry,**row))
    return dict(hits=hits,resources=resources)


def validate():
    manifest=read_json(FOLDER/'manifest.json')
    assert manifest['status']=='PARTIAL_READ_AHEAD_NOT_SEMANTIC_REVIEWED'
    for row in manifest['files']:assert sha256(FOLDER/row['file'])==row['sha256'],row['file']
    assert sha256(OUT/manifest['resume_notes'])==manifest['resume_sha256']
    assert manifest['accepted_mechanics_added']==manifest['accepted_paths_added']==manifest['review_required_added']==0
    assert all(manifest[k] is False for k in boundary_flags())
    for prefix in ['multiplayer','multiplayer-loader']:
        assert collect(read_json(FOLDER/(prefix+'-preview-spec.json')))==read_json(FOLDER/(prefix+'-preview.json'))
    assert prepare(read_json(FOLDER/'multiplayer-native-preview-spec.json'))==read_json(FOLDER/'multiplayer-native-preview.json')
    assert census()==read_json(FOLDER/'multiplayer-census-preview.json')
    # The partial bundle adds no accepted or reviewed draft mechanics/paths.
    review=read_json(OUT/'mod-reviews/twilightforest.json')
    assert review['draft_mechanic_count']==270 and review['draft_path_count']==996
    assert review['status']=='PARTIAL'
    draft=read_json(OUT/review['draft_file'])
    assert draft['checkpoint']=='R2f8ad-fence-leash-complete'
    assert read_json(OUT/'research-decision.json')['save_mode'] is True
    return dict(schema='tno.external_effects.partial_evidence_validation.v1',status='PASS',scope='Saved source bytes/census and resume integrity only; multiplayer semantics incomplete.',evidence_files=len(manifest['files']),reviewed_twilight_mechanics=270,reviewed_twilight_paths=996,review_required_added=0,twilight_promoted=False,runtime_tests=0,**boundary_flags())


if __name__=='__main__':
    result=validate();write_json(OUT/'r2f8ae-multiplayer-read-ahead-validation.json',result);print(json.dumps(result,indent=2))
