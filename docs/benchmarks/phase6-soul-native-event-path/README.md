# Soul native-path evidence

S1: `s1-native-path-audit.json`, reproduced by `scripts/audit-phase6-soul-native-path.ps1`. The installed artifact and recorded bytecode descriptors are authoritative. Historical evidence is read without modification.

S2: `s2-runtime.jsonl` is the formal two-case native bow control. Reproduce with `gradlew.bat runServer -Pphase6_soul_native_path=true -Pphase5f_runtime_mods_dir=run/elemental-runtime-mods` (Java 21), then run `scripts/extract-phase6-soul-native-path.ps1 -LogPath <log>` and `scripts/test-soul-native-path-extractor.ps1`. `s2-validation.json` is independently derived. `s2-provenance.json` records stack hashes/build results. Both earlier diagnostics retain their actual status; they are not substitutes for formal evidence.

See [research record](../../phase-6-soul-native-event-path-research.md). No production prototype or permanent fix is included.

S3: `s3-runtime.jsonl` preserves the recovered 20-case capture, including one explicitly unresolved flight. `s3f-runtime.jsonl` contains the three focused follow-ups only. Reproduce the first with `-Pphase6_soul_comparison=true`, the latter with `-Pphase6_soul_followup=true`, always alongside `-Pphase6_soul_native_path=true` and the S2 full-stack runtime directory. Extract with `-Checkpoint S3` or `-Checkpoint S3F`, respectively. Run the corresponding corruption tests with the same checkpoint and evidence path. Do not rerun accepted captures merely to recreate files.

`s3-comparison.json` aggregates both independently validated captures. `s3-native-audit.json` supplies installed Gazel/NEB/regeneration/resource-cap source checks. `s3a-recovery.json` records the intermediate protected state. Diagnostics are preserved without reinterpretation as successful official matrices. The later centered lane resolves the missing Hinata S7 native gate observation, without claiming a proved cause for the earlier missed trajectory.

S4: `s4-decision.json` records `SOUL_NATIVE_PATH_VALID_NO_FIX`, checkpoint ancestry, final clean-build/test results, scope comparison and limitations. All requested work ends with owner review. No permanent production implementation or next-family work is included.
