# Soul native-path evidence

S1: `s1-native-path-audit.json`, reproduced by `scripts/audit-phase6-soul-native-path.ps1`. The installed artifact and recorded bytecode descriptors are authoritative. Historical evidence is read without modification.

S2: `s2-runtime.jsonl` is the formal two-case native bow control. Reproduce with `gradlew.bat runServer -Pphase6_soul_native_path=true -Pphase5f_runtime_mods_dir=run/elemental-runtime-mods` (Java 21), then run `scripts/extract-phase6-soul-native-path.ps1 -LogPath <log>` and `scripts/test-soul-native-path-extractor.ps1`. `s2-validation.json` is independently derived. `s2-provenance.json` records stack hashes/build results. Both earlier diagnostics retain their actual status; they are not substitutes for formal evidence.

See [research record](../../phase-6-soul-native-event-path-research.md). No production prototype or permanent fix is included.
