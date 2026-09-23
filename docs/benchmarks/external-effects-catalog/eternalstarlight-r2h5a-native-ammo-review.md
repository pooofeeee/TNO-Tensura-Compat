# R2h5a — Eternal Starlight native ammunition

Remaining native snowball/bomb and four arrow variants plus thrown material spear core; reuse accepted custom-type and Tearing/boomerang work.

Static subsection complete. Runtime fixtures remain unexecuted; no Stage or production implementation.

## Snowball

AshenSnowball Player native throw speed1.5/inaccuracy1 and registered ownerless dispenser. Entity collision requests native thrown direct=snowball/causing=owner, amount5 if target instanceof Blaze else1.5; hurttrue &&Living gates Blindness50 amp0. onHit inherited dispatch occurs first, then server non-MISS impact independently applies Slowness60 amp0 to Living in AABB3 with shouldHarm(owner), no LOS and no hurt-success requirement, then discard. Block hit and rejected entity hit can still produce Slow aura. No explosion or custom freeze source. Stage final thrown damage once; Blindness/Slow admission/duration remain native.

## Frozen bomb

Native Player throw speed1.5/cooldown20 or registered ownerless dispenser. Server non-MISS onHit inherited dispatch -> actual Level.explode radius3, fire=false, ExplosionInteraction.TNT with null explicit source/calculator -> then Living AABB3 shouldHarm(owner): canFreeze gates +100 frozen ticks cap300, but Slowness60 amp0 is requested regardless canFreeze; no blast-hurt success test. Native explosion direct=bomb/causing=Living owner or null; factory owned player_explosion else explosion. Exposure/distance/ignoreExplosion/event checks apply to explosion, while later control cube has independent eligibility and no LOS. TNT block interaction follows native gamerules. Preserve owner/allied explosion behavior (shouldHarm only governs later control); each final native explosion hurt is single future Stage point, not radius or frozen ticks. This does not create ES FREEZE damage; subsequent native freezing uses normal native ticking/admission.

## Arrow common

Glacite, Malarite, Aethersent and AirSac use normal AbstractArrow with genuine owned bow/crossbow factories and explicitly registered ownerless dispenser factories. Direct=arrow/causing=owner; native speed/base/crit/enchantment and projectile impact/deflection/hurt-return gates remain. Extra post-hit effects occur only after successful Living hit and native Enderman early-return. Stage final native arrow hurt once for each; never separately multiply material/stat/base/speed bonuses. All statuses retain native canBeAffected, effect events and owner/effectSource semantics. Static source evidence is not a runtime guarantee of L2/Tensura outcome.

## Glacite malarite

Glacite successful post-hit adds saved duration(default200) frozen ticks capped300 only if canFreeze. No direct custom FREEZE request or additional poison-like DOT; retained native frozen counter and vanilla freeze ticking are separate. Malarite successful post-hit requests Poison(saved duration default200,amp0) with getEffectSource; it does not require absence of existing Poison. Native poison DOT source/damage floor/mitigation and effect immunity are preserved. Stranghoul native bow branch uses getMobArrow and default MalariteArrow when no supported held ammo, so mob-owned arrow is a proven additional route. Native Pungency spear Poison/Nausea and Tearing eligibility already pinned in R2h2b; this section adds core thrown-weapon formula and the Malarite spear path without changing that decision.

## Aethersent airsac

Aethersent owned and coordinate/dispenser constructors add3 pierce to existing byte value, then ordinary arrow behavior. Post-hit Aethersent explosion-looking particles are cosmetic: no second damage, meteor or Level.explode. Piercing retains native multiple-victim admission/shield interaction, and arbitrary later modifiers may change pierce. AirSac only changes water inertia to.99 and water gravity to half native gravity; outside water delegates normal gravity. This changes trajectory/speed feeding native arrow damage, not a separate hit/control effect. Leave pierce and physics native, scale final native HP request once.

## Spear damage

ThrownSpear builds item damage from owner ATTACK_DAMAGE base (fallback1); copied weapon ATTACK_DAMAGE component modifiers replace same-ID live modifiers, weapon entries added in native reverse insertion order then remaining live modifiers. Applies each native operation sequentially: ADD_VALUE adds amount, ADD_MULTIPLIED_BASE adds amount*base, ADD_MULTIPLIED_TOTAL adds amount*current result. Thus preserve this implemented order rather than recomputing an assumed attribute formula. Multiply result by native scale2 (Malarite) or2.5 (Pungency), then native enchant modifyDamage. No speed or AbstractArrow base/crit damage term. Source native thrown direct=spear/causing=owner, or spear itself when owner null. dealtDamage set BEFORE hurt; hurtfalse still ends further entity targeting; grounded time>4 also does so. Hurttrue Enderman exits before post callbacks; otherwise enchantment post source remains thrown (unlike boomerang rewrite), then Living knockback/material post-effect. Malarite addsPoison60 amp0; Pungency addsPoison80 amp1+Nausea120 independent of each effect acceptance. No iframe reset, source armor/shield/Resistance/protection remain ordinary. Stage only final thrown hurt after this full formula.

## Spear paths

Spear Player native use rejects too-damaged stack; release requires>=10 ticks and same durability check, server durability1 -> copied pickup/weapon spear, speed3/inaccuracy1; removes noncreative held stack, creative pickup-only. Both material spears register real ownerless dispenser behavior, retaining weapon stack and fallback base1; ownerless causing=spear matters for source-based native admission and Tearing. Stranghoul native SpearItem branch creates owned spear from mainhand, speed1.6/inaccuracy14-4*difficultyId, retains native pickup defaults and does not remove held weapon. This actual mob path and Player/dispenser are distinct. dealtDamage persists with superclass state; no native loyalty-return logic in ThrownSpear. Ordinary pickup restrictions stay native, not Stage. Energy Boomerang sole native subtype and shared boomerang formula/return/enchantments remain accepted R2h3a; no duplicate package or new dispenser path is introduced here.

## Scope

Freeze/control quantities, status amplification/duration, ammo/durability, projectile pierce/velocity and callback cadence remain unscaled. Independent vanilla freezing/Poison DOT follow their existing final native damage processing. Rendering/acquisition/repair and pickup visuals are excluded. No runtime, custom fallback source, direct HP/SHP subtraction or Stage implementation.

## TNO integration decisions

- **Ashen Snowball native hit**: COMPOSITE, ADMISSION_GATED, NUMERIC_SCALABLE. Stage: Once at native thrown5/1.5 hurt, after Blaze predicate.
- **Ashen Snowball hit Blindness and independent Slow aura**: COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE. Stage: no additional multiplier; Native status/control and item resource remain unscaled.
- **Frozen Bomb native TNT-interaction explosion**: COMPOSITE, ADMISSION_GATED, NUMERIC_SCALABLE. Stage: Once at per-victim native explosion final hurt.
- **Frozen Bomb independent freezing and Slowness**: COMPOSITE, ADMISSION_GATED, NO_STAGE_VALUE. Stage: no additional multiplier; Native status/control and item resource remain unscaled.
- **Glacite native arrow**: COMPOSITE, ADMISSION_GATED, NUMERIC_SCALABLE. Stage: Once at native AbstractArrow final hurt; secondary status or projectile physics unscaled.
- **Malarite native arrow**: COMPOSITE, ADMISSION_GATED, NUMERIC_SCALABLE. Stage: Once at native AbstractArrow final hurt; secondary status or projectile physics unscaled.
- **Aethersent native arrow**: COMPOSITE, ADMISSION_GATED, NUMERIC_SCALABLE. Stage: Once at native AbstractArrow final hurt; secondary status or projectile physics unscaled.
- **Airsac native arrow**: COMPOSITE, ADMISSION_GATED, NUMERIC_SCALABLE. Stage: Once at native AbstractArrow final hurt; secondary status or projectile physics unscaled.
- **Malarite and Pungency native thrown spear damage**: COMPOSITE, ADMISSION_GATED, NUMERIC_SCALABLE. Stage: Once at final native thrown hurt after ordered attribute reconstruction, material factor and enchantments.

[Machine-readable packages, delivery paths and future fixtures](eternalstarlight-r2h5a-native-ammo.json). Exact archive/method witnesses and targeted semantic assertions are reproducible. No whole-mod completion claim.

Exact next task: R2h5b: remaining special melee, shields, armor/attribute procs and resource modifiers; then spells/crests and non-boss creatures/hazards, whole ES closure/promotion/full validation, then Bosses Rise. Gleech Egg remains with Gleech creature review; Aetherstrike weather trigger with hazards.
