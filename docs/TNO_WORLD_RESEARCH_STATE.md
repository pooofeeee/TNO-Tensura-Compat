# TNO world redevelopment — decisions and research state

Updated: 2026-10-30. This is the compact record of the user's newer project direction and source decisions. It supersedes the old compatibility roadmap as the current objective; it does not invalidate or delete the existing implementation.


## Active reference programme — 2026-10-30

The user's latest instruction expands the research deliverable to a permanent, detailed LN reference for characters, behaviour, abilities and world laws, intended for later implementation work. It explicitly authorizes successive evidence batches without requesting general permission after each one, superseding the 2026-10-28 “await review / do not start another batch” checkpoint below. Historical evidence and its uncertainties remain preserved.

**Canonical entry point:** [docs/reference/README.md](reference/README.md), with coverage, sources, character/ability/world chapters and a gap/resume ledger. Initial priorities are Milim, Masayuki, Hinata, Glenda, Mariabell, Rimuru at True Demon Lord stage, and the user's “Weak Shinro” label after identity verification. These are priority targets, not a complete series census. No character dossier is claimed complete.

Baseline verified: `c52800e93cda5d48b0b1834268f024a3cd1df407`. New batches REF-01/02/03/04 directly inspected selected LN10 and LN6 scenes through Slime Reader's browser. Translation editions and electronic paragraph anchors are recorded in the source register. Existing embodiment records were linked without repeating their research. “Weak Shinro” remains unresolved; repository search returned incomplete results and is not absence evidence.

**Resume:** أُنجزت REF-88/89، MI-GOVERNANCE، من SR08-GH الفصل3 L1339–1439: خبر إسناد إدارة الأرض إلى Frey/Karion، طلب Milim المشاركة وردها على سؤال موافقتهما، وتفكير ريمورو في الاتصال ثم تركه. تفسير الدراسة/الهروب وقصد Frey من التقارير يعود لريمورو؛ لا صوت مباشر للطرفين أو سحر سيطرة/هزيمة في فكاهة المشهد. لا صفات ثابتة أو نقل معرفة LN11 إلى LN8. التالي MI-GOV-VOICE: عيّن تصريحًا/فعلًا مباشرًا لـFrey/Karion عن توزيع القرار والتواصل، بدءًا بمؤشر SR08-GH الفصل4 blob 043336df3d7e1adac1cc39e80a50f1e11b7d4bf0 عند97b06b7659fcfe30a3ec396a5c2c8fa0962bbe00؛ لم يقرأ بعد ولا جواب معتمد من البحث. اقرأ مقطعًا مطابقًا واحدًا، وإلا سجل قصور المؤشر بدل توسع غير محدد؛ لا تعاد دفعة الفصل3 أو القتال/Gaia. حدود Gaia والـavatar/Ramiris وقيود LN2/F03/P254 وJP/P98 والأهلية/Weak Shinro محفوظة. وثائق فقط؛ التغطية جزئية.

Documentation-only changes: new reference tree and this state. Checks: source/edition/speaker/locator review, internal relative-link validation, historical-evidence preservation and remote commit/content verification. No code or runtime tests.

## Repository and branch

- Repository: `pooofeeee/TNO-Tensura-Compat`.
- Active development branch, explicitly designated by its own AGENTS.md: `codex/production-continuation`.
- Verified head before this documentation reconciliation: `af391700ae546c748bd7621b29df4bd7bad654c3`; parent `eb37f0bfc0e7aa863632f163881566c0ae2a8701`.
- `main` is the default branch, not the current development baseline.
- No separate world-foundation branch was present in the branch inventory checked on 2026-10-26. This checkpoint changes documentation on the designated development branch only. Choose an isolated branch/worktree for future redesign when needed.
- Read the selected branch's AGENTS.md and relevant state before work. Do not assume another branch carries these instructions. Pin evidence to a commit when reproducibility matters.

## Current objective and boundaries

TNO aims to become a full alternative to the existing Tensura mod, representing the world as inhabitants experience it: consistent laws, conditions, causes, consequences, and interactions. Names and damage numbers alone do not meet the objective.

The target remains Minecraft 1.21.1. TNO is separate from Infinity Mod (formerly TNO Impact). Infinity's four-component ontology, files, plan, and progression decisions are not TNO canon or architecture.

Preserve prior work and assess reuse before rewriting anything. Existing compatibility code and verified mod research are implementation evidence, not authority on Tensura's original world.

Older small-scope goals, damage-based Stages, and EP-based control proposals are not automatically approved for the new design. Their presence in production documents describes legacy implementation, not canon approval. The canonical meaning of EP must be researched separately from any mod's EP/Stage mechanisms.

Research and clarify the source-to-design relationship before broad gameplay changes. Neither complete system architecture nor a first-release acceptance standard has been approved yet.

Do not require Infinity to finish first, impose a fixed weekly schedule, or offer month/year estimates without defined work and measured execution. “Best Tensura mod” is an aspiration to evaluate with evidence, not an established result.

## Source policy

### User-selected Light Novel reading sources

1. Slime Reader: https://tensurafan.github.io/
2. User-provided Volume 1 reader: https://fliphtml5.com/rhvsa/tpus/That_Time_I_Got_Reincarnated_as_a_Slime%2C_Vol._1/

Use these as the primary access points for reading available Light Novel text. The second link identifies Volume 1 only; do not assume other volumes are present or that either site covers the entire series.

Record the actual translation, edition/revision, language, volume, chapter/section, and location consulted. Verify translator/publisher information from the copy when available; do not infer official status from the hosting platform. Distinguish printed page numbers from viewer page indexes.

Access evidence from the preceding conversation: Slime Reader opened without readable chapter text in the web extraction; the supplied FlipHTML5 page initially timed out, while its indexed basic page showed the Volume 1 title but no text content. These are tool-access observations, not proof the books are unavailable. No novel scene was verified through these two links in that check.

Try the site's exposed reading/export options when needed. Opening a landing page or seeing a search snippet is not reading the novel. If a passage remains inaccessible, record that limit and continue other available work without inventing pages, quotations, or findings.

### Continuity and evidence

- The Light Novel is the primary continuity for this project. Japanese LN text and applicable official supplemental material are the reference for resolving wording disputes when available.
- Translations can support research directly, with their identity and limits recorded. Do not block all research merely because the Japanese text is unavailable.
- Web Novel, manga, anime, games, spin-offs, and author statements must retain separate continuity/adaptation/provenance labels. Never use WN as an automatic missing-volume substitute.
- Official status alone does not establish that a glossary statement applies identically to every version. Record the source's demonstrable scope.
- Wikis and discussions can locate passages; mark unverified source pointers as such.
- When sources conflict, preserve both claims and their context. Distinguish translation ambiguity, adaptation changes, character knowledge, and later clarification. Prefer explicit applicable evidence; do not silently merge or automatically let a later statement erase an earlier contextual rule.
- Maintain separate fields for explicit source statements, inference, unresolved questions, and proposed game approximation. Absence of a statement is not proof of its negation.
- Each rule record should identify the source/edition/location/access level, speaker/context, conditions, mechanism, cost, limits, exceptions, and interactions. Unknown fields stay unknown.
- Summarize in original wording and use short quotations only when necessary. Preserve research notes and source locations in GitHub rather than copying entire books into the repository.

## Research already attempted — preserve, do not restart

- Batch 0 established the need for a source register, terminology register, rule template, and access/conflict tracking. Pasted drafts contained unreliable bibliography, translations, and extrapolations; they are working notes, not an approved canon database.
- The official dictionary at https://www.ten-sura.com/keyword was used for targeted terminology checks: 魔素, 技術 (アーツ), 物質体, 精神体, 星幽体, 名付け, 不死系魔物, and 魔法不能領域.
- Follow-up focused on 蟲型魔獣, 精霊召喚, and 悪魔 to investigate world types, summoning, manifestation, embodiment, and vessels.
- Preserve the methodological corrections: a vessel is not automatically a corpse; “natural incarnation” alone does not prove the absence of a vessel or ritual; summoning and embodiment are not established as mutually exclusive processes; differing glossary descriptions do not prove there are no shared laws.
- Do not classify every revived being as undead, infer universal body/identity rules from a short entry, or use failure to mention EP/Stages as proof of their absence from the LN.
- The initial handoff had no verified novel scenes. The 2026-10-26 [embodiment evidence checkpoint](TNO_EMBODIMENT_EVIDENCE.md) now records directly inspected translated LN passages for both cases. Japanese comparison and broader generalization remain open; earlier glossary speculation is not promoted to law.
- Do not repeat the dictionary summaries as a substitute for the next evidence task.

## Current evidence checkpoint and next research task

The initial passage-location task and its targeted rule refinement are complete for the inspected scenes: see [TNO_EMBODIMENT_EVIDENCE.md](TNO_EMBODIMENT_EVIDENCE.md), records E-BER-001-R1 and E-DIA-001-R1. Body, energy, vessel/offering and contract/service fields now separate explicit evidence, inference and unresolved limits. The bounded physical-presence follow-up is recorded as E-BER-001-Q1: the official Japanese sample did not reach the matching passage; E-LN11-001 supplies a conditional comparison, not a definitive wording resolution. Keep that ambiguity open; resume it only with the specified Japanese counterpart or a directly connecting LN passage, not another general access hunt. Reuse the recorded access routes rather than repeating the search. The earlier access observations above remain historical, not a current claim that no text is readable.

### 2026-10-28 continuation

Verified branch baseline: `f78a02df3dfe94645925668c66cc805b7418bb6b`. Read this branch's AGENTS.md, this state, the evidence record and relevant CODEX_STATE.md context. No literal STATE.md was found in the root/docs listings; these are the canonical research files designated by AGENTS.md. No local checkout was available.

Completed the bounded artificial-vessel/transfer batch as **E-LN11-002**, with explicit statements, interpretation, unknowns and a documented P98 image-access/extraction limit. Use that record rather than repeating the scene or treating the earlier provisional design as the implemented vessel. E-BER-001-Q1 is still open; no new Japanese locator was obtained and its completed sample search was not repeated.

**Next bounded task:** LN11 chapter 2, viewer P85–88, Ifrit's separate case; consult P79–80 only for necessary vessel-preparation context. Record compatibility, transfer/naming conditions and any stated energy source, keeping character claims and inference separate. Stop at one reviewable case record with explicit gaps. Do not presume demon mechanics apply to Ifrit or reopen the Japanese search without the source specified in Q1.

Only the evidence and world-research-state documents are updated for this checkpoint. Validation is source/location review, preservation/scope review and remote commit/content verification; no code/build/runtime tests are warranted for this documentation-only batch.

### Ifrit batch completed — 2026-10-28

Baseline checked: `dba3b18133fba4d25d99cae6bcee8f2a47df4320`. The previously queued Ifrit task is complete as **E-LN11-003** in [the evidence file](TNO_EMBODIMENT_EVIDENCE.md). Read LN11 chapter 2, viewer P85–88 directly through the existing upload; source identity reused from the register. No preparatory reread of P79–80 was needed.

The record distinguishes Veldora's compatibility explanation and Raphael's agreement, Rimuru's tolerance expectation, the reported transfer/body sequence, and naming safeguards. Keep its unknowns explicit; do not turn this case or E-LN11-002 into universal spirit/demon laws. The extraction-order caveat is recorded separately from the cross-page sequence.

**Current stopping point:** this bounded batch is complete and awaits review. Do not start another batch automatically. The earlier “Next bounded task” paragraph above is historical and now satisfied. Any post-P88 follow-up needs a new bounded scope; no such work is claimed here. Beretta Q1's Japanese gap and E-LN11-002's P98 image-access issue remain unchanged.

Changed paths: evidence and this state only. Checks: source/speaker/location review, prior-record preservation, documentation-only scope and remote head/content verification. No code, main, builds or runtime tests.

Original bounded task (retained for acceptance criteria): find inspectable LN passages for:

1. Diablo's summoning and what the passage says about his appearance/body.
2. Beretta's summoning and preparation of the associated body.

Test the relationship between summoning, manifestation, incarnation, and a vessel without assuming in advance that they are separate stages or the same operation.

For each case, return the verified book/volume/chapter/edition/language, direct source link, actual access level (novel text, preview, or secondary pointer), a faithful short account, the exact claim supported, and what remains unresolved. Do not invent a chapter or page. If access fails, record the attempted route and remaining gap.

Stop this bounded task when the two evidence records are reviewable or their genuine access blockers are documented. This is a research checkpoint, not authorization to implement a universal summoning/body system.

## Full research scope and unresolved design work

The overall research scope remains comprehensive: world structure and existence; bodies, souls and identity; energy/magicules; magic and acquired arts; skills; races and evolution; naming and contracts; attacks, defenses and resistances; healing, death and revival; materials, ecology, equipment and industry; space, time and information; exceptional abilities; society and everyday life.

Order work by dependencies and revise previous conclusions when stronger evidence appears. Later mechanics must not be excluded merely to keep the current research batch small.

Still unresolved:
- Complete source register with verified editions and access coverage.
- A source-backed world-system map and its dependencies.
- Reuse/redesign assessment of the existing code under the new objective.
- Precise ontology and exceptions for the current embodiment questions.
- Reviewable source-to-design proposals and measurable first-release acceptance criteria.
- No new game architecture, Stage policy, or universal EP control has been approved by this documentation checkpoint.

## Protected existing work

- Phase 6 production and its six native integrations remain preserved.
- `external-effects-catalog-research` is a cold archive, verified at `301601ec6afa62e5cc8dc8f0c24759c937c1ba71`. Its AGENTS.md, compact STATE.md, and CAMPAIGN.md were inspected without reopening the full evidence trees.
- That archive reports `tensura_neb` PARTIAL at R2p3, blocked on exact original-instance ManasCore identity/bytes; its available local scope is reconciled. Preserve the completed reviews and do not restart its census or unrelated mod campaigns.
- The archive's test results are historical reported evidence; they were not rerun during this documentation reconciliation.
- The old CODEX_STATE.md's archive checkpoint and “next implementation milestone” are historical. They do not authorize a Royal Variations pilot or override the current source-first research task.

## Efficiency and handoff

Latest user instruction received through the parent on 2026-10-28: use GPT-6.1 Sol / High for this Codex task's subsequent turns. This explicitly supersedes the 2026-10-26 Astra / Extra High (xhigh) request; the user's exception retaining Astra / Extra High applies only to the separate Work coordinator, not this task. Preserve this instruction history rather than treating the change as an autonomous usage-saving downgrade. A requested setting is not proof of actual runtime identity, and this checkpoint does not claim a runtime-confirmed switch. Save usage through targeted reads/searches, reuse of verified results, bounded tool output and relevant validation; do not change the user's selected model/effort autonomously.

Use one agent by default. Do not install Caveman, RTK, Headroom, Ponytail, hooks, or MCP servers merely because their names came up. No savings measurement or installation is claimed by this checkpoint.

At meaningful milestones, update the appropriate GitHub state and evidence records within authorized scope. Record changed paths, checks actually executed, unresolved blockers, and the next bounded task. Do not replay entire conversations or reread unchanged repositories.

## Reference continuation REF-05/06/07 — 2026-10-30

Baseline: `86fc5c8d0f66ec3fd08442cefbf3dd91246a3610`. Rechecked the designated branch and AGENTS, reused SR10's seventh-edition register and inspected the targeted text in-browser.

- REF-05 follows Glenda's capture report, questioning, curse removal and recruitment; it does not invent the offscreen remainder of the duel. The curse and desire influence stay distinct pending a demonstrated connection.
- REF-06 adds Greed's field applications and failures, preserving earlier character/analysis beliefs alongside Yuuki's later deception disclosure. No universal Unique/Ultimate immunity or skill-transfer formula is approved.
- REF-07 adds Milim/Rimuru cooperation and the Gaia core operation; vessel preparation is separated from expected future recovery. No completed general resurrection system is claimed.

Source ranges, interpretation, capability limits and new gaps are linked through the reference index. Coverage remains partial. Next: RTDL-BASE, followed by specific Masayuki/Hinata evidence. No general permission request is needed. Only reference documentation and this state changed; internal-link/preservation/scope checks and remote head/content verification are the validation for this batch. No code/build/runtime tests.

## Reference continuation REF-08/09/10 — 2026-10-30

Baseline checked: `bec913a4855cf62526f1d35cd7255a818f973610`. Followed the saved queue without repeating Diablo's case or earlier character scenes.

- REF-08 locates Rimuru's eligibility statement, condition discussion, Harvest Festival onset and selected body/skill changes in F05. Quantity alone is not adopted as a sufficient universal rule; original eligibility and full skill inventory remain gaps.
- REF-09 adds SR09's Chosen One description and the tournament withdrawal, with SR10's later worry about Gozer. Withdrawal is not reported as skill deactivation; reputation, party effects and personal fighting ability stay separate.
- REF-10 records SR07's Usurper, Mathematician and Melt Slash in their LN7 phase, including interference, training/body constraints and Raphael's later clarification. Figurative “ultimate” is not a classification change, and a counterfactual survival explanation is not an observed hit without defense.

Sources, coverage and gaps now point to RTDL-SKILLS; identity/Japanese/access gaps remain preserved. Only reference documentation and this state changed. Checks: source/edition/speaker/phase review, relative-link and preservation/scope review, remote head/content verification. No code/build/runtime tests.

## Reference continuation REF-11/12/13 — 2026-10-30

Baseline checked: `6f3f6bbb6a800efa6ffa0354cb9993ab3672f0d5`. Reused AGENTS, canonical source/coverage records and completed case evidence.

REF-11 adds the LN5 post-awakening inventory, separating the initial review, Veldora soul-corridor event and later Food Chain/Ability Adjust consolidation. Function names do not establish full mechanics or independent Ultimate ranks. REF-12 distinguishes tentative resistance attributed to Bernie from Rimuru's own non-effect report. REF-13 resolves the earlier Beelzebuth-copy gap with a newly located passage before the already-read defense explanation; it does not approve universal skill backup.

The active queue moves to H-FIRST, then uncovered R-FUNCTIONS. Character phases, translation labels and open costs/ranges remain explicit. Documentation only. Validation: source/speaker/phase review, relative-link/scope checks and remote commit/content verification. No code, builds, runtime tests, main edits or external messages.

## Reference continuation REF-14/15/16 — 2026-10-30

Baseline checked: `36886768ba799d1c27029f94ef5d06eee54dfca6`. Reused branch AGENTS and the source/coverage/gap records. This continuation reads the specifically requested first confrontation and two linked function cases; no prior Beretta/Diablo research was repeated.

REF-14 fixes the first fight's locator to LN4's epilogue; REF-15 follows its resolution in LN5 chapter 3, separating an original's survival from a defense test. REF-16 adds a pre-awakening comparison for the analysis/learning functions listed in V5-INV. Detailed statements, speakers, page markers and uncertainties are in [the clash record](reference/abilities/hinata-first-clash.md) and [the learning record](reference/abilities/rimuru-analysis-learning.md). No cross-phase equivalence or universal soul/body law is established.

H-FIRST is closed as a bounded scene, while the new field/weapon/replication and knowledge limits remain in the gap ledger. The active queue is R-FUNCTIONS-BASE, not another access search for the unresolved Japanese Beretta passage. Coverage remains partial; no complete character or world system is claimed. Documentation only, on the designated branch. Checks: source/speaker/phase/locator review, relative-link and preservation/scope checks, remote commit/content verification. No code/build/runtime tests or external messages.

## Reference continuation REF-17/18/19/20 — 2026-10-30

Baseline checked: `4f60daf7604e844db7b949e8f3e488d004b143eb`. Rechecked the designated branch AGENTS, active state and gap/source/coverage records. No model identity verification is inferred from these documents.

REF-17 and REF-18 add [the original Predator functions and an analysis-link case](reference/abilities/rimuru-predator.md). REF-19 adds [the Glutton transition and phase comparison](reference/abilities/rimuru-glutton-phases.md), reusing REF-08/11/14/15/16 and V7-H-COUNTER2 rather than rereading them. REF-20 adds an early observer case in [Milim's dossier](reference/characters/milim.md), distinguishing judgments about her from tested capabilities and her own decisions.

Source editions, exact viewer markers and access modes are in SOURCES. The F02 P254 table is clipped in the source image as well as extraction; missing wording is not reconstructed. F03 root extraction failed, but relevant individual pages were read in-browser; access to this bounded scene is not blocked. The next queue is MI-EARLY-ACTION, with its location still to be established. R-FUNCTIONS and the whole-series/identity/Japanese gaps remain open. Coverage is partial.

Documentation only on the same branch. Validation: source/speaker/phase/locator review, relative-link and preservation/scope checks, remote commit/content verification. No code, main edits, build/runtime tests, installations, server operations or messages to other tasks.

## Reference continuation REF-21-A/22/23/24 — 2026-10-30

Baseline checked: `4ce8695de1f64de3c7d736207ae858322df56676`. Rechecked designated branch AGENTS and active source/gap/coverage records; one researcher.

The exact blocked action was opening the published F03 reading link at https://online.fliphtml5.com/efxnj/pjte/ to locate Milim/Rimuru's first meeting. It returned No reading rights after loading. Status: denied by the reader, no uncertain outcome or pending approval. Stopped without retry or same-copy extraction. The official Yen Press product page was read as bibliography, with no visible sample route; its Book Walker link redirected to migration/search and failed non-retryably. No denial bypass, purchase, subscription or whole-novel upload. REF-21-A is an access record, not novel evidence or increased scene coverage.

Independent useful work completed: REF-22 [Masayuki's early agency](reference/characters/masayuki.md), REF-23 [a group-effect case](reference/abilities/chosen-one.md), and REF-24 [Hinata's suspicion and the altered recording](reference/characters/hinata.md). Each separates scene chronology, speaker knowledge, interpretation and unknown limits. H-MESSAGE closes only for the demonstrated deletion; technical actor/recovery mechanism remains open.

The next bounded task is MI-LN6-ACTION while MI-EARLY-ACTION waits for permitted text. The previous F02 P254 defect remains unchanged; its image/text were not reopened. Reference coverage is partial. Documentation only on the same branch. Checks: source/edition/locator/speaker review, relative-link and preservation/scope checks, remote commit/content verification. No code, main edits, builds/runtime tests, installations or external messages.

## Reference continuation REF-25/26/27 — 2026-10-30

Baseline: `ccc902c7cd6685638fbe79f06d6746e1db5c9065`. Rechecked the active branch AGENTS, state, source/coverage/gap records. After the parent reported a capacity interruption, checked the remote head and state/Milim contents again: unchanged; the new drafts had not been committed. Continued them without rereading the source or duplicating a saved batch.

REF-25/26 add [the LN6 pre-reveal action/resource case](reference/abilities/milim-walpurgis.md), separating observed behaviour, Raphael's actual report, Rimuru's interpretation and counterfactual regeneration estimates. The earlier reveal is linked, not reread. REF-27 adds [a nonhuman Holy Magic case](reference/world/holy-magic-cases.md), preserving the difference between observation and explanation without treating it as a complete world system.

Source edition/anchors and read boundaries are recorded. MI-LN6-ACTION closes only for the inspected passages; MI-FULL-POWER, resource quantities and HOLY-CHANNELS remain open. LN3's No reading rights and F02's source-image clipping remain unchanged; neither source was retried or reconstructed. Next: the targeted later Holy Magic explanation, then independent uncovered functions as available. No complete character or world-system coverage is claimed.

Documentation only on the designated branch. Checks: source/speaker/phase/locator review, relative-link and preservation/scope checks, remote commit/content verification. No code/main edits, builds/runtime tests, installations, server actions or external messages.

## Reference continuation REF-28/29/30/31 — 2026-10-30

Baseline: `12f0694375fc16fc428bbdccdd42ed5d682db0d2`. Rechecked branch AGENTS and active source/coverage/gap records. One researcher; no previous completed scene was restarted.

REF-28 adds [the Hinata healing/compatibility case](reference/world/holy-magic-cases.md); REF-29 adds the later SR08 faith-contract statement, explicitly separate from a complete supply/delegation system. REF-30 adds [a learning and pre-activation interference case](reference/world/magic-activation-cases.md). REF-31 adds [the public-result proposal during reconciliation](reference/characters/hinata.md), without rewriting the combat result.

All entries identify edition, phase, section, electronic paragraph range and speaker limits. Spiritron use, faith, a contract and a healing name do not by themselves define a universal channel, lifecycle or resurrection law. No full system or character dossier is claimed complete. Next: the bounded Holy Cannon application/resistance pointer, then available uncovered functions; supply/delegation needs explicit evidence. F03 denial and F02 clipping remain unchanged without renewed access.

Documentation only on the designated branch. Validation: source/speaker/phase/locator review, relative-link and preservation/scope checks, remote commit/content verification. No code/main edits, builds/runtime tests, installations, server operations or external messages.

## Publication recovery and REF-32/33/34/35 — 2026-10-30

Rechecked remote head `12f0694375fc16fc428bbdccdd42ed5d682db0d2`, current AGENTS and the saved 13-file review bundle. No uncertain commit outcome was found. The blocked create_commit operation was retried once in the authorized recovery and succeeded; the branch update used the expected head. REF-28–31 are published at `6479b6564b4301a47056c06ea17c46dd2764040d`; all 11 changed paths and full contents matched, and the remote head was verified. Local review status was changed from pending to published. No source research was repeated to recover publication.

New research baseline: that verified commit. REF-32/33/34 add [the Holy Cannon/barrier/Cook case](reference/world/holy-cannon-barrier.md); REF-35 adds [a bounded Shion dossier](reference/characters/shion.md). The source locator was verified as LN7 chapter 5 and the actual owner corrected from the broad R-RESIST queue label to Shion. Reflected attacks, physical passage, regenerated injury and the narrative's outcome claim remain distinct mechanisms/claims. A described resistance condition is preserved without inventing a universal matchup formula.

The extra character case does not redefine the seven-priority denominator as a series census. Holy supply/delegation, quantitative limits and full phase coverage remain open. Next: H-ARMAMENT in the saved unread gap. F03 reading denial and F02 clipped text remain unchanged without new access attempts.

Documentation only on the designated branch. Checks: source/edition/section/speaker/phase review, relative-link and history/scope checks, remote commit/content verification. No code/main edits, builds/runtime tests, installations, server operations or external messages.

## Reference continuation REF-36/37/38/39/40 — 2026-10-30

Baseline: `a89c18e73bcde633ed5bf828aacf9c49593a34f2`. Rechecked active AGENTS and canonical source/gap/coverage/state records; one researcher.

REF-36 fills [the Hinata equipment gap](reference/abilities/hinata-ln7.md). REF-37/38 add [Rimuru's weapon preparation and learned attack prediction](reference/abilities/rimuru-ln7-combat.md), keeping character estimates and reported costs separate from universal mechanics. REF-39 adds [a human title/evolution case](reference/world/human-evolution-cases.md), retaining both the prior Hinata attribution and later equipment-state wording. REF-40 adds [Glenda's earlier introduction](reference/characters/glenda.md), without importing her later secrets into earlier observers' knowledge.

Source ranges, edition and speaker limits are recorded. No permanent transformation from an item, infinite resource, movement-speed multiplier, all-purpose future sight or universal ranking rule is established. Next: check the explicit eligibility-origin gap through a bounded earlier Geld passage; its proposed locator remains unverified. F03 denial and F02 P254 clipping remain unchanged; neither was reopened.

Documentation only on the designated branch. Checks: source/edition/section/speaker/phase review, relative-link and history/scope checks, remote commit/content verification. No code/main edits, builds/runtime tests, installations, server operations or external messages.
