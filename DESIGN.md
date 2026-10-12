# Reference design

Objective: maintain public, app-independent BLE protocol documentation for eight battery models, following the evidence-first approach of Dashcam Camera Profiles. Cellink Neo, PC8 F141, BP100 V39 and B-130X1.61 now have their own scoped hardware evidence; preserve wider-model/firmware unknowns.

Success checks: exact tested-model/firmware scope; transport, framing, lengths, field units and unknowns documented; private raw data excluded; synthetic vectors agree with the working parser; local links/privacy checks pass; public GitHub files and CI match the reviewed commit.

The reference distinguishes scoped hardware telemetry evidence from source-derived branches and synthetic examples. iVolt has hardware-corroborated DAT telemetry through strict production-parser acceptance, but unknown firmware/model identity and no retained raw replay. Keep source attribution pinned and maintain one shared BlackVue layout with model-specific evidence pages. Add future firmware layouts without rewriting established evidence.

Rollback: correct an erroneous claim with a new commit that preserves history and explains the evidence. Never force-push or import private app/capture directories. The standalone repository contains only reviewed public documentation, profiles, synthetic examples and validation code.

The audience is developers building custom apps/interfaces and maintaining batteries after manufacturer support ends. Document UUIDs, initialization, read/write commands, fields, units and firmware branches. Omit test readings, screenshot comparisons, sample counts and session narratives. Camera Bluetooth research and application planning belong in separate projects.

HK6-F extension: add a separate hardwire-accessory broadcast reference without
changing the eight battery profiles or claiming an app integration. Publish
reviewed voltage offsets and synthetic placeholders, qualify firmware/family
coverage, and keep raw identities and captures local. Scope is Bluetooth
discovery, advertisement fields and remaining Bluetooth protocol gaps only;
exclude USB pinouts, wiring and electrical-signaling documentation.
Success checks are the existing links/privacy/vector validator, a focused diff,
GitHub CI and live-document equality. Rollback uses a corrective commit.
