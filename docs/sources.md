# Primary sources and version assumptions

Accessed: **2026-11-16**. This is a tested-version field guide, not a claim that these are the newest releases. Repository tags were resolved through the public GitHub Git references API. Commit links below freeze source behavior; Android and Shizuku website pages are living documentation.

## Pinned projects

| Project | Examined version | Resolved commit | What it supports |
| --- | --- | --- | --- |
| android-virtual-screen | v0.2.1 | `b1d8e0ba8b1fe81e453c73c70af3d6eaddeb1e7a` | Android 13+ requirement, Root and Shizuku/Stellar backends, 19 MCP tools, loopback endpoint, observation and receipt constraints |
| Shizuku | v13.6.0 | `2650830c5b099ae0dd34fedf614d4f592ca05d65` | Release identity; official setup explains separate root and ADB startup routes |
| Mika | v0.1.44 | `2b26f3f80937a320581dab66f16e6a7fda1799ce` | Setup paths, shell service, trusted-display fallback, per-display keep-awake behavior |

### android-virtual-screen

- [Pinned README](https://github.com/lejw0925/android-virtual-screen/blob/b1d8e0ba8b1fe81e453c73c70af3d6eaddeb1e7a/README.md): release requirements, backend choices, 19 tools and architecture. Upstream historical device results are not this guide's live results.
- [Pinned MCP reference](https://github.com/lejw0925/android-virtual-screen/blob/b1d8e0ba8b1fe81e453c73c70af3d6eaddeb1e7a/docs/MCP.md): `http://127.0.0.1:8732/mcp`, ADB forwarding, authorization, protocol handshake, fresh observations, request receipts and tool schemas. Schemas returned by the installed server remain authoritative.
- [v0.2.1 release](https://github.com/lejw0925/android-virtual-screen/releases/tag/v0.2.1): version-specific APK and checksum provenance. No APK binary is redistributed here.

### Shizuku

- [v13.6.0 release](https://github.com/RikkaApps/Shizuku/releases/tag/v13.6.0) and [pinned source tree](https://github.com/RikkaApps/Shizuku/tree/2650830c5b099ae0dd34fedf614d4f592ca05d65): version identity.
- [Official setup guide](https://shizuku.rikka.app/guide/setup/): rooted startup, Android 11+ wireless debugging startup, computer/ADB startup, post-reboot restart and OEM troubleshooting. This living page is not version-pinned to the release. It explicitly warns that ADB permissions are limited; root and ADB startup are not interchangeable privilege identities.

### Mika

- [Pinned English setup guide](https://github.com/wangzan101/Mika/blob/2b26f3f80937a320581dab66f16e6a7fda1799ce/docs/setup-guide.en.md): Android requirements, app wireless pairing, documented `usb-start.sh`, startup from another existing ADB shell channel, root-started helper retaining limited permissions, recovery differences and compatibility self-check.
- [Pinned ShellService.kt](https://github.com/wangzan101/Mika/blob/2b26f3f80937a320581dab66f16e6a7fda1799ce/app/src/main/java/com/wangzan101/mika/cap/phone/shell/ShellService.kt): shell UID 2000 design; shell-context DisplayManager construction; `createDisplay`, `createVirtualDisplay`, `displayFlags`; trusted-display fallback; input, launch and display lifecycle implementation. Hidden API use and fallback are implementation details, not stable public Android contracts.
- [Pinned DisplayAwake.kt](https://github.com/wangzan101/Mika/blob/2b26f3f80937a320581dab66f16e6a7fda1799ce/app/src/main/java/com/wangzan101/mika/cap/phone/shell/DisplayAwake.kt): four-second per-display user-activity scheduling, own-display-group check, cancellation and unavailable-interface handling.

## Android platform contracts

- [Media projection guide](https://developer.android.com/media/grow/media-projection): capture consent, session/token lifecycle, foreground service requirements and `onStop` cleanup. Android 14+ single-session token rules are not evidence that a shell-owned independent display uses MediaProjection.
- [DisplayManager reference, secure virtual display flag](https://developer.android.com/reference/android/hardware/display/DisplayManager#VIRTUAL_DISPLAY_FLAG_SECURE): secure output requires `CAPTURE_SECURE_VIDEO_OUTPUT`, reserved for system components; secure windows are blanked on a non-secure virtual display.
- [WindowManager.LayoutParams, FLAG_SECURE](https://developer.android.com/reference/android/view/WindowManager.LayoutParams#FLAG_SECURE): window-level protection against screenshots and display on non-secure output. This is different from a device keyguard being secure or showing.
- [ADB guide, wireless debugging](https://developer.android.com/tools/adb#connect-to-a-device-over-wi-fi): workstation pairing and connection on Android 11+, network requirements and troubleshooting. A workstation's ADB authorization is not Mika's in-app pairing state.

## Evidence provenance and contrary evidence

Field observations in [solutions.md](solutions.md) are supplied by the experiment owner from live device work. Source reading verifies explanations and version identities, not a replay of the device experiments. Public source availability does not establish that a particular service was running, that an RPC traversed the installed app, or that a full AI workflow completed.

Important counterexamples retained in this guide:

1. A rooted Samsung failed the Root backend while Shizuku started as shell worked. Root availability alone did not ensure this implementation's display creation succeeded.
2. VirtualScreen's first self-check was 18/19 with Tap failing. Later explicit bounded tap/type success supplements rather than replaces that result.
3. Samsung screen-off success had keyguard false, so it was not a secure-lock test.
4. Xiaomi secure-lock native-helper success did not exercise the serving helper RPC or the full Mika AI workflow.
5. A lost wireless ADB connection was followed by an absent helper. Manual startup restored it; that initial session did not demonstrate automatic recovery. A later awake helper-only interruption after Mika own pairing did recover automatically and pass the app self-check; wireless-off/locked and reboot recovery remain unverified.

Do not publish raw screenshots, device serials, account identifiers, credentials, private host paths or unfiltered device dumps as evidence. Prefer a redacted version/state/outcome table with the tested boundary named explicitly.

## Community reports and recovery implementation

The [wireless-debugging guide](wireless-debugging.md) separately labels Chinese and English first-hand community reports, their contrary evidence and the newly observed awake helper-only recovery. Community posts are not platform contracts or universal compatibility proof. The guide links the pinned AOSP Android 16 debugging manager and Mika auto-on implementation for the underlying mechanism.
