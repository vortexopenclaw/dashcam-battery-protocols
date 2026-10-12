# Sources and attribution

## VIOFO HK6 / HK6-F

- [Official HK6-F product documentation](https://www.viofo.com/products/viofo-type-c-hk6-f-acc-hardwire-kit-for-t330-t340-support-parking-mode).
- [Official HK6/BP100 app setup guide](https://www.viofo.com/blogs/viofo-car-dash-camera-guide-faq-and-news/bp100-hk6-dashcam-app-setup).

Controlled passive observations on one HK6-F powering a T330W support the
[manufacturer-data voltage map](hk6.md). Accessory firmware is unknown.
Supply changes and a fixed-supply ACC round trip distinguish battery and ACC
inputs. Unknown prefix/trailer bytes, private radio identities and captures
are not redistributed. The decoding illustration is synthetic.
Native-app agreement, calibration, wider-model compatibility and checksum
semantics remain unverified. Product documentation establishes user-facing
features, not undocumented Bluetooth commands.

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

Targeted offline analysis of the battery activity, Bluetooth connection manager and battery-info view established request framing, firmware-aware offsets and estimate-display behavior. This repository publishes independently written protocol facts, not the APK or manufacturer application source. Hardware observations corroborate B-1241.44, B-130A1.61 and B-130X1.61. The battery-info view also supplies the source-derived B-130X charging-mode output-display condition. The public blog posts establish provenance/integration, not an official wire specification.

## Cellink Neo+

[RobXYZ/cellink2mqtt](https://github.com/RobXYZ/cellink2mqtt), inspected commit `d97ab241aa92d22a00482ecdcddf28e491ad13b5`:

- [Protocol and evidence limits](https://github.com/RobXYZ/cellink2mqtt/blob/d97ab241aa92d22a00482ecdcddf28e491ad13b5/PROTOCOL.md)
- [Supported-model context](https://github.com/RobXYZ/cellink2mqtt/blob/d97ab241aa92d22a00482ecdcddf28e491ad13b5/README.md)

The upstream hardware validation is Neo 8+; its manufacturer-app model list provides a PowerCell 8 research lead. No upstream setting implementation is copied into this reference.

## Cellink Neo

Original-Neo context comes from the pinned [cellink2mqtt protocol notes](https://github.com/RobXYZ/cellink2mqtt/blob/d97ab241aa92d22a00482ecdcddf28e491ad13b5/PROTOCOL.md), which distinguish the older `kr.co.egens.cellinkbatterybtcontrol` family and `43 06` framing. The shared legacy field map is independently interpreted from the BlackVue implementation above and corroborated by Cellink Neo firmware 1.52 replies. Other Neo variants and Neo-specific settings remain unverified.

## VIOFO BP100

- [Official current app page](https://www.viofo.com/pages/viofo-app), package `com.viofo.dashcam`.
- [Manufacturer BP100/HK6 setup and display behavior](https://www.viofo.com/blogs/viofo-car-dash-camera-guide-faq-and-news/bp100-hk6-dashcam-app-setup).
- [Manufacturer BP100 manual](https://viofotech.com/download/manual/BP100/UserManual.pdf).

Targeted offline analysis used Android2.2.03, base APK SHA256 `6b0ec5a846cbe88b804fedc458ad0bebb38fbb2bee157bfe9f246f47e7a9fe2d`, privately obtained from a third-party mirror, not an official APK delivery endpoint. APK signature/hash checks establish artifact identity, not an independently proven manufacturer delivery chain. No APK or decompiled source is redistributed.

Battery transport, builders/parsers and session initialization establish C0 UUIDs, read-only GET41/01–04, XMODEM outgoing CRC and command-specific fields. The actual session's explicit incoming-CRC-disabled override corrects the earlier default-parser inference. Direct phone/Mac V39 responses independently corroborate the documented measurements. Unknown timeA/configured extension scaling/binding behavior is not silently promoted to hardware evidence. Public app/manual pages establish provenance and user-visible behavior, not an official wire specification.

## Thinkware iVolt XTRA

- [Official mobile-app compatibility guide](https://support.thinkware.com/hc/en-us/articles/360045289593-Which-Thinkware-Mobile-App-do-I-use), mapping iVolt Xtra to THINKWARE iVolt.
- [Official BAB-95 installation and app guide](https://support.thinkware.com/hc/en-us/articles/16357652595859-How-to-Install-the-iVolt-Xtra-Battery-Pack).
- [Official Play listing](https://play.google.com/store/apps/details?id=com.thinkware.ivolt), package `com.thinkware.ivolt`.

Offline review used compatible native Android app **1.1.7**, version code **19**. Base APK SHA256: `c3e87c1380f8463aa4e68d3048b58bb3cc5f59fa0a65938c077ea71ed8191461`. The privately acquired artifact came from a third-party mirror, not direct Play delivery. Hash/signature checks corroborate the reviewed artifact, not an independently proven manufacturer delivery chain. No software or decompiled code is redistributed.

Independently described facts come from the native GATT selection/notification/write paths, main receive and verification paths, DAT setters, settings GET parser and voltage/current/state/time presentation. They establish FFF1/FFF2, literal DATA/GET1, ASCII framing/checksum and the source-derived groups documented on the [iVolt page](ivolt-xtra.md). The native DAT branch is not universally checksum-gated, unlike the recommended strict client. Hardware evidence corroborates GATT/CONT, DATA-only startup without GET1, DAT1-3 charging and loaded discharge, positive temperature, ordinary currents and charging-mode unavailable output current. This evidence is strict production-parser acceptance, including response checksum validation, not independent raw-packet replay: raw replies were not retained. Firmware/model identity, calibration, full/protection, negative temperature, FFFF, special 9900 and other revisions remain unverified. Official guides describe product/app and user-facing behavior, not ATT command semantics. Public vectors are newly constructed from these facts; password/settings GET responses are intentionally excluded.

This is an unofficial protocol reference. Public examples are synthetic; manufacturer software and private device captures are not redistributed.
