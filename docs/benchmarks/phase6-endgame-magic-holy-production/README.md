# Phase 6 Magic/Holy production acceptance

This directory is reserved for production-path acceptance evidence. It does not replace or alter the accepted calibration A-I artifacts.

## Checkpoint status

- P1: production Stage policy, optional existing-L2 adapter, live native generic-health formula, and synchronous event context implemented.
- P2-P6: not yet executed at this checkpoint.

P1 is intentionally behavior-neutral: the context is not yet connected to the native event and no L2 damage modifier is registered. The adapter uses `getExisting`, requires an initialized attachment, reads the target's current level plus live `healthFactor`, `exponentialHealth`, and entity `healthScale`, and returns no view if any required read fails.
