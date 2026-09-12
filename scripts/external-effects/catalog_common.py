"""Read-only helpers for the separate installed-JAR catalog research."""
from pathlib import Path
import hashlib
import json
import subprocess
import zipfile

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'docs/benchmarks/external-effects-catalog'
WORK = ROOT / 'run/external-effects-catalog'
BASELINE = 'a5e85e610349120e21d62f4a80f1b607e36607fe'
MODS = Path('C:/Users/youra/curseforge/minecraft/Instances/new/mods')
TARGETS = [
 ('cultofazazel','cultofazazelneo-1.1.3.1.jar'),
 ('variantsandventures','variantsandventures-neoforge-1.0.23+mc1.21.1.jar'),
 ('royalvariations','royal-variations-[NeoForge]_1.21.1_2.0.4.jar'),
 ('friendsandfoes','friendsandfoes-neoforge-4.0.23+mc1.21.1.jar'),
 ('twilightforest','twilightforest-1.21.1-4.8.3345-universal.jar'),
 ('iceandfire','IceAndFireCE-2.0-beta.15-1.21.1-neoforge.jar'),
 ('eternalstarlight','eternalstarlight-0.8.1+1.21.1+neoforge.jar'),
 ('block_factorys_bosses','block_factorys_bosses-2.1.2-neo-1.21.1.jar'),
 ('bosses_of_mass_destruction','BOMD-NeoForge-1.21-1.3.3.jar'),
 ('cataclysm',"L_Ender's Cataclysm 1.21.1-3.27.jar"),
 ('tensura_neb','tensura_neb-neoforge-2.0.0.3.jar'),
 ('netherexp','Jadens-Nether-Expansion-2.4.0-BETA.7.jar'),
 ('illagerinvasion','IllagerInvasion-v21.1.6-1.21.1-NeoForge.jar'),
 ('mowziesmobs','mowziesmobs-1.21.1-1.8.2.jar'),
 ('lycanitesmobs','lycanitesmobs-0.0.1.jar'),
 ('alexsmobs','alexsmobs-1.22.17.jar'),
 ('darkestsouls','DarkestSouls-Neoforge1.21.1-v1.2.3.3.jar'),
 ('arphex','ArPhEx-5.0.2-neoforge-1.21.1.jar'),
 ('alexscaves','alexscaves-2.0.10.jar'),
 ('tennogamenolife','tennogamenolife-1.1.4.3.jar'),
 ('tensura','tensura-neoforge-2.0.1.1.jar'),
 ('antarchy','antarchy-1.1.1+1.21.1-neoforge.jar'),
 ('legendary_monsters','legendary_monsters-2.2.1 MC 1.21.1.jar'),
]
CLASSIFICATIONS = ['VANILLA_DIRECT','VANILLA_EQUIVALENT','VANILLA_COMPOSITE',
 'VANILLA_LIKE_EXTENDED','CUSTOM_STATUS','CUSTOM_DAMAGE','CUSTOM_CONTROL',
 'CUSTOM_RESOURCE','BINARY_MECHANIC','REVIEW_REQUIRED']
DELIVERIES = ['MELEE','PROJECTILE','THROWN_PROJECTILE','EXPLOSION','AOE',
 'SUMMONED_ATTACK','SPELL','SKILL','ACTIVE_ITEM','PASSIVE_ITEM','ARMOR_PROC',
 'ACCESSORY_PROC','PASSIVE_AURA','MOB_ATTACK','BOSS_ATTACK','ENVIRONMENT','OTHER']

def sha256(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()

def byte_hash(data):
    return hashlib.sha256(data).hexdigest()

def read_json(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))

def write_json(path, obj):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

def git(*args):
    return subprocess.check_output(['git', *args], cwd=ROOT, text=True).strip()

def archive_text(archive, name):
    return archive.read(name).decode('utf-8-sig')

def boundary_flags():
    return dict(phase6_reopened=False, production_changed=False, stage_changed=False,
                boss_testing_started=False, l2_testing_started=False,
                compatibility_fixes_started=False, phase7_started=False)
