# Codex project instructions

## Current project direction (2026-10-26)

- TNO's current objective is a comprehensive, source-grounded redevelopment of the Tensura world, separate from Infinity Mod.
- Read `docs/TNO_WORLD_RESEARCH_STATE.md` for world research, source policy, redevelopment scope, and the current evidence task; read `docs/CODEX_STATE.md` for the relationship to preserved implementation.
- The compatibility/Stage rules below protect the existing implementation. They do not approve Stages, EP-based control, or the old compatibility roadmap for the new world design.
- Use the user's selected Slime Reader and FlipHTML5 LN access points documented in the research state; record the actual translation, edition, location, and access level.
- Current work is source research and documentation. Preserve production while the source-to-design relationship is established; no broad gameplay rewrite or Royal Variations pilot is authorized by this checkpoint.

## Preserved implementation and execution constraints

- Treat this file as a map, not a request to preload the repository.
- Read `docs/CODEX_STATE.md` only for architecture, Stage-system, or project-wide decisions. For local tasks, read only the files needed for that task.
- Work on `codex/production-continuation`. Do not modify `main` or `external-effects-catalog-research` unless explicitly requested.
- Phase 6 production behavior is the accepted baseline. Do not redesign or rebalance it unless the task explicitly authorizes that.
- The accepted native Stage families are Magic Weapon, Holy Weapon, Soul Eater, Elemental/Slotting, Energy Steal, and Severance.
- Tensura native Gear EP is authoritative. Do not add a second EP counter, Stage store, Stage XP system, or duplicate progression state.
- Preserve native source identity, events, eligibility, immunity, cancellation, lifecycle, ownership, and delivery paths unless the current task explicitly targets one of them.
- External mechanics may scale only an explicitly selected numeric parameter at one proven boundary. Do not recreate the native mechanic, emit duplicate damage/effects/events, or apply Stage twice.
- Binary/native gates are not Stage-scaled by default: applicability, immunity, nullification, cancellation, teleport permission, team checks, death gates, and lifecycle rules remain native.
- For delayed mechanics, snapshot activation-time Stage only when needed to preserve the original source owner's progression.
- `external-effects-catalog-research` is a cold reference archive. Never recursively inspect or summarize it by default.
- Investigate only facts that can change the implementation of the current task. Stop investigating once the implementation decision is determined.
- Reuse existing research before starting new research. If evidence is needed, open only the exact mechanic/class/method/evidence file required.
- Do not start broad boss, L2, balance, whole-JAR, or compatibility research unless explicitly requested.
- Keep each task narrow: prefer one shared primitive or one mechanic at a time.
- Prefer existing production patterns over new abstractions unless the task clearly needs a reusable primitive.
- Run the narrowest relevant test first. Run broader tests only after the narrow test passes. Run a full clean build only at a meaningful closure point.
- Keep terminal output bounded. Redirect verbose Gradle/Minecraft output to a file; inspect the failure, matching errors, or a short tail instead of dumping full logs into context.
- Do not create benchmark/evidence trees for ordinary implementation work.
- Do not start the Royal Variations pilot until explicitly requested. Current pilot candidates are Dazed, Marked, and Time Bomb.

## Usage budget discipline
- Keep the user's selected Sol 6.1 / High reasoning unchanged; save work through focused context and fewer redundant calls, not by lowering reasoning.
- Define the task's required outcome and stop condition before exploring. Start with `rg`, specific file paths, and existing decision records.
- Single agent by default; use subagents only for genuinely independent subproblems with a demonstrable net benefit.
- If the same operation fails twice without changed conditions, investigate the cause rather than looping.
- For task transitions, use the canonical state instead of replaying previous chats; compact only when necessary and preserve key decisions and unresolved blockers.
- Final report: changed paths, targeted/full checks actually run, and outstanding issues. No unrequested third-party token hooks or broad MCP additions.
