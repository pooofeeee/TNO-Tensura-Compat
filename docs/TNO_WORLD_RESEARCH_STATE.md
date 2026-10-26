# TNO world redevelopment — decisions and research state

Updated: 2026-10-26. This is the compact record of the user's newer project direction and source decisions. It supersedes the old compatibility roadmap as the current objective; it does not invalidate or delete the existing implementation.

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
- Full novel passages supporting the current Diablo/Beretta questions have not yet been verified in this research handoff. Do not promote earlier glossary paraphrases or speculative questions into novel-backed laws.
- Do not repeat the dictionary summaries as a substitute for the next evidence task.

## Immediate next research task

Find inspectable LN passages for:

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

Keep the user's selected GPT-6.1 Sol with High reasoning. Save usage through targeted reads/searches, reuse of verified results, bounded tool output, and relevant validation; never by reducing model capability or dropping necessary evidence.

Use one agent by default. Do not install Caveman, RTK, Headroom, Ponytail, hooks, or MCP servers merely because their names came up. No savings measurement or installation is claimed by this checkpoint.

At meaningful milestones, update the appropriate GitHub state and evidence records within authorized scope. Record changed paths, checks actually executed, unresolved blockers, and the next bounded task. Do not replay entire conversations or reread unchanged repositories.
