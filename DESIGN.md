# Reference design

Objective: maintain public, app-independent BLE protocol documentation for the five battery models, following the evidence-first approach of Dashcam Camera Profiles.

Success checks: exact tested-model/firmware scope; transport, framing, lengths, field units and unknowns documented; private raw data excluded; synthetic vectors agree with the working parser; local links/privacy checks pass; public GitHub files and CI match the reviewed commit.

The reference intentionally separates discovery-only profiles from decoded telemetry. Keep source attribution pinned and maintain one shared BlackVue layout with model-specific evidence pages. Add future firmware layouts without rewriting established evidence.

Rollback: correct an erroneous claim with a new commit that preserves history and explains the evidence. Never force-push or import private app/capture directories. The standalone repository contains only reviewed public documentation, profiles, synthetic examples and validation code.
