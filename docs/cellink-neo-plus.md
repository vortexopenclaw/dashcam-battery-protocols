# Cellink Neo+ research appendix

Evidence: **upstream-source-derived**, not hardware-tested by this project. [RobXYZ/cellink2mqtt](sources.md#cellink-neo) documents Neo 8+ hardware validation and a wider manufacturer-app model list that includes `PWC8`. That list does not prove PowerCell 8 compatibility.

This family uses service `FF12`, writer `FF01` and notification characteristic `FF02`. Replies begin ASCII `@@` (`40 40`), carry command/subcommand/length, and end `0A 0D`; complete reply length is the byte at offset 4 plus 7. Identification and status requests in the upstream source are `40 40 30 00 0A 0D` and `40 40 41 00 0A 0D`. Multi-byte measurement fields are little-endian, unlike the two hardware-verified families in this reference.

The upstream standard status is 75 bytes. Its payload includes settings and a PIN-bearing region at complete-frame offsets 59–60. **Do not publish full unreviewed replies.** Prefer a reviewed telemetry-only field summary. Unknown response types can contain different private fields, so zeroing those two bytes is not a universal sanitizer. Extended/status/setting details and their evidence limits remain in the [pinned upstream protocol document](https://github.com/RobXYZ/cellink2mqtt/blob/d97ab241aa92d22a00482ecdcddf28e491ad13b5/PROTOCOL.md).

The older original-Neo family uses different framing. Keep `@@` and `43 06` decoders separate, and preserve the [PowerCell 8 discovery-only status](powercell8.md) until its own replies verify a profile.
