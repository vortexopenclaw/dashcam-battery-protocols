# Sources and attribution

## BI-750

[kennygarreau/esp32-bi750](https://github.com/kennygarreau/esp32-bi750), inspected commit `775abc7948c22eae4d1bc1d4ef243469862ae31c`:

- [Packet structures](https://github.com/kennygarreau/esp32-bi750/blob/775abc7948c22eae4d1bc1d4ef243469862ae31c/src/esp32-bi750.h)
- [Transport, requests and scaling](https://github.com/kennygarreau/esp32-bi750/blob/775abc7948c22eae4d1bc1d4ef243469862ae31c/src/esp32-bi750.cpp)

The upstream implementation supplies the ITSC transport and measurement map. This project's hardware captures independently corroborate basic telemetry on firmware 1.6 and identify raw mode 4 as an incomplete semantic mapping.

## BlackVue legacy

- [Official battery-management integration announcement](https://media.blackvue.com/blackvue-app-battery-management-ui-update-and-integration-to-the-main-app/)
- [Official app-update post linking the China Android download](https://media.blackvue.com/blackvue-app-update-save-to-your-photo-gallery-cloud-battery-mapbox-integration/)
- [Manufacturer's Android China download page](https://media.blackvue.com/download/blackvue-aos-china/)

Analyzed app: BlackVue Android China **3.60**, version code **36000**, package `comb.blackvuec`. The reviewed APK's SHA-256 is `6f0c4fd87179132d65addf21ea05fd63f326838f3e6409ab90f143da43d3c221`. The download page may later serve a different version; match the artifact before reproducing this analysis.

Targeted offline analysis of the battery activity, Bluetooth connection manager and battery-info view established request framing, firmware-aware offsets and estimate-display behavior. This repository publishes independently written protocol facts, not the APK or manufacturer application source. Hardware observations corroborate B-124 1.44 and B-130A 1.61. The public blog posts establish provenance/integration, not an official wire specification.

## Cellink Neo+

[RobXYZ/cellink2mqtt](https://github.com/RobXYZ/cellink2mqtt), inspected commit `d97ab241aa92d22a00482ecdcddf28e491ad13b5`:

- [Protocol and evidence limits](https://github.com/RobXYZ/cellink2mqtt/blob/d97ab241aa92d22a00482ecdcddf28e491ad13b5/PROTOCOL.md)
- [Supported-model context](https://github.com/RobXYZ/cellink2mqtt/blob/d97ab241aa92d22a00482ecdcddf28e491ad13b5/README.md)

The upstream hardware validation is Neo 8+; its manufacturer-app model list provides a PowerCell 8 research lead. No upstream setting implementation is copied into this reference.

## Original Cellink Neo6

Original-Neo context comes from the pinned [cellink2mqtt protocol notes](https://github.com/RobXYZ/cellink2mqtt/blob/d97ab241aa92d22a00482ecdcddf28e491ad13b5/PROTOCOL.md), which distinguish the older `kr.co.egens.cellinkbatterybtcontrol` family and `43 06` framing. The shared legacy field map is independently interpreted from the BlackVue implementation above and corroborated by Neo6/1.52 replies. Other Neo variants and Neo-specific settings remain unverified.

## VIOFO BP100

- [Official current app page](https://www.viofo.com/pages/viofo-app), package `com.viofo.dashcam`.
- [Manufacturer BP100/HK6 setup and display behavior](https://www.viofo.com/blogs/viofo-car-dash-camera-guide-faq-and-news/bp100-hk6-dashcam-app-setup).
- [Manufacturer BP100 manual](https://viofotech.com/download/manual/BP100/UserManual.pdf).

Targeted offline analysis used Android2.2.03, base APK SHA256 `6b0ec5a846cbe88b804fedc458ad0bebb38fbb2bee157bfe9f246f47e7a9fe2d`, privately obtained from a third-party mirror, not an official APK delivery endpoint. APK signature/hash checks establish artifact identity, not an independently proven manufacturer delivery chain. No APK or decompiled source is redistributed.

Battery transport, builders/parsers and session initialization establish C0 UUIDs, read-only GET41/01–04, XMODEM outgoing CRC and command-specific fields. The actual session's explicit incoming-CRC-disabled override corrects the earlier default-parser inference. Direct phone/Mac V39 responses independently corroborate the documented measurements. Unknown timeA/configured extension scaling/binding behavior is not silently promoted to hardware evidence. Public app/manual pages establish provenance and user-visible behavior, not an official wire specification.

This is an unofficial protocol reference. Public examples are synthetic; manufacturer software and private device captures are not redistributed.
