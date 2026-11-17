# Solutions: separate display, privilege and lifecycle

This guide records device-specific paths, not a universal Android compatibility claim:

- **VirtualScreen v0.2.1 + Shizuku v13.6.0 started through ADB as shell** worked on the tested Samsung with the physical screen off. The original Root backend failed on that same device. A later [separate root-hosted controller](a32-root-android13.md) passed with a root bootstrap and runtime system UID1000; it is not the app-level Root backend or serving MCP.
- **Mika v0.1.44 native shell service** created and controlled a separate display on a non-root Xiaomi while its physical display was off and secure keyguard was showing. That result came from a disposable process loading the installed APK's native helper code, not from Mika's serving-helper RPC or full AI workflow.

- **Pixel 10 Pro XL / Android 17, non-root, VirtualScreen + ADB Shizuku** adds a bounded parallel-use result and conditional locked semantic input. See the [Pixel workflow](pixel-android17.md); locked coordinate input failed and wireless auto-enablement is explicitly excluded.

Versions, primary references and provenance are in [sources.md](sources.md). References here are pinned where the upstream project permits it. No root installation, bootloader change or keyguard dismissal is part of this procedure.

## 1. Understand the four identities

| Identity | What it means | What it does not establish |
| --- | --- | --- |
| Ordinary app UID | An installed application has its own sandbox and platform permissions. A public-API app can render its own virtual-display content; MediaProjection provides user-consented capture. | Installing an app or granting accessibility does not turn its process into shell or root, grant arbitrary trusted-display flags or authorize arbitrary cross-app input. |
| ADB shell, UID 2000 | A system-defined identity available through an authorized ADB connection. Shizuku started with ADB and Mika's limited helper use this identity for supported system operations. | Shell is not UID 0 and is subject to permissions, package attribution, SELinux, Android version and OEM behavior. |
| Root, UID 0 | A distinct execution identity made available by an existing root environment. Some applications implement a Root backend or use root only to start a less-privileged helper. | Root availability does not mean every Binder API call succeeds or has valid package/UID attribution. A root-started helper need not continue running as root. |
| System UID 1000 after root bootstrap | The later A32 controller used root authorization to start a worker matching its system-context package attribution. | Runtime UID1000 is not UID0 or an ordinary app. It is not `system_server`; SELinux and API/version behavior still matter. This does not fix the original app's root registration path. |

Shizuku's **Start via root** and **Start via wireless debugging / computer ADB** are different startup choices. For the original Samsung Shizuku case below, choose the **ADB startup route**, then confirm that Shizuku reports shell operation. A rooted device can still use ADB-started Shizuku. Do not silently substitute root startup because root is available. [Official Shizuku setup](https://shizuku.rikka.app/guide/setup/).

If root operation is explicitly required on the tested A32, use the [separate root-hosted architecture and its boundaries](a32-root-android13.md); do not silently substitute the Shizuku path.

Mika documents a separate nuance: its root startup starts the same limited helper used by wireless or computer startup. Its optional root-command capability is a separate setting and is not required for this experiment. [Pinned Mika setup](https://github.com/wangzan101/Mika/blob/2b26f3f80937a320581dab66f16e6a7fda1799ce/docs/setup-guide.en.md#rooted-phone-start-it-with-root).

## 2. Choose the path by the required boundary

| Need | Candidate | Required evidence before calling it working |
| --- | --- | --- |
| MCP agent controls a separate display | VirtualScreen + ADB-started Shizuku | Installed server handshake, tool discovery, session/display creation, fresh observation and a bounded input verified on that display |
| Root-required A32 screen-off control | Root bootstrap -> system UID1000, separate controller | Root/runtime identity, live input readback, physical-panel state, bounded idle and identity-checked cleanup; not stock MCP or secure lock |
| Non-root native display mechanism | Mika shell helper | Helper startup and identity, display creation, changing frame/tree and bounded input on a disposable test page |
| Full Mika AI task | Mika app with its intended helper connection and model configuration | App-level RPC plus an actual completed task. Native-helper tests alone do not satisfy this row |
| Ordinary consented screen sharing | MediaProjection | System consent and projection lifecycle; this is not a substitute for independent display input or locked-background execution |

None of these paths guarantees protected-content capture, all apps launching on secondary displays, autonomous recovery or compatibility with every ROM. Test the actual boundary you need.

## 3. VirtualScreen with ADB-started Shizuku

### Setup and local transport

1. Install the matching v0.2.1 APK from the upstream release and check its published checksum. Upstream requires Android 13 or later.
2. Start Shizuku through its official ADB route, not its root-start button for this case. Authorize VirtualScreen in Shizuku.
3. In VirtualScreen's permissions/backend screen, select **Shizuku / Stellar** and verify the live backend status. The tested service was Shizuku, not Stellar.
4. Enable VirtualScreen's own accessibility service if needed for node observation and Unicode editing. Preserve every other enabled accessibility service. Use the app's settings and authorization UI rather than overwriting the complete secure-setting list or broadly granting unrelated permissions.
5. Enable its MCP server and retain authentication. Keep LAN access and public tunnels disabled for this setup. Forward the loopback port from an explicitly selected device:

```sh
adb -s SERIAL shell id
adb -s SERIAL forward --no-rebind tcp:8732 tcp:8732
# Configure the MCP client for http://127.0.0.1:8732/mcp.
# Supply authentication privately through the supported client configuration.
```

`SERIAL` is a placeholder, including for a wireless ADB endpoint. `--no-rebind` rejects an occupied binding without replacing another session's forward. If host port 8732 is occupied, choose another free port or use `tcp:0`, then retain ADB's allocated host port for the client and cleanup. No token extraction or publication is needed. [Pinned MCP reference](https://github.com/lejw0925/android-virtual-screen/blob/b1d8e0ba8b1fe81e453c73c70af3d6eaddeb1e7a/docs/MCP.md).

### Verify the MCP boundary

Use `initialize`, `notifications/initialized`, then `tools/list`; use the installed server's schemas rather than guessing parameters. v0.2.1 documents 19 tools. Obtain control/session state as required by those schemas, launch a harmless test page or Settings on the created display, observe it, and submit a single bounded tap or text edit using the fresh observation. Re-observe to verify the change. On an uncertain response, inspect the request receipt before repeating any input. Do not target main-display Home or Power as a shortcut. The exact authentication and protocol headers belong to the client's negotiated session. [Pinned MCP protocol and constraints](https://github.com/lejw0925/android-virtual-screen/blob/b1d8e0ba8b1fe81e453c73c70af3d6eaddeb1e7a/docs/MCP.md).

### Samsung result and failure interpretation

Tested: Samsung A32, Android 13 / One UI 5.1, Magisk 31.1 already present, VirtualScreen 0.2.1, Shizuku 13.6.0.

| Test | Observed result | Interpretation |
| --- | --- | --- |
| VirtualScreen Root backend | `SecurityException`: `packageName must match the calling uid` | This backend failed on this setup. The error points to package/UID attribution; its exact upstream defect was not isolated here. |
| Shizuku started through ADB as shell | Loopback MCP exposed 19 tools; Settings launch, tree, tap and type passed | This is an actual installed-app/MCP result, not only a source hypothesis. |
| Physical display off, `DOZE_SUSPEND` | The bounded Settings workflow passed | Screen-off behavior passed for this setup. Keyguard was false, so secure-lock behavior remains untested. |
| First app self-check | 18/19, Tap failed | Retain the initial failure. Later explicit bounded tap/type tests passed but do not retroactively change this self-check. |

A `packageName must match the calling uid` error is not a reason to grant all root requests or globally alter system permissions. First compare the selected backend, actual service identity and exact exception. The demonstrated workaround here is the ADB-started Shizuku backend, not a claim that root is intrinsically incapable of virtual displays. Mika's source independently shows why shell-attributed contexts matter: it explicitly constructs a DisplayManager with its shell context rather than a mismatched system context. That source is explanatory evidence, not proof of VirtualScreen's precise failing call. [Mika ShellService source](https://github.com/wangzan101/Mika/blob/2b26f3f80937a320581dab66f16e6a7fda1799ce/app/src/main/java/com/wangzan101/mika/cap/phone/shell/ShellService.kt).

## 4. Mika without root

### Intended app setup versus manual helper startup

Mika's v0.1.44 setup guide describes Android 12+ for app control, with Android 14+ recommended. Installation on Android 11 does not establish app-control compatibility. Its intended wireless path pairs **Mika itself** with Android wireless debugging, then connects its built-in helper. This is separate from a workstation pairing its own ADB client. [Pinned setup guide](https://github.com/wangzan101/Mika/blob/2b26f3f80937a320581dab66f16e6a7fda1799ce/docs/setup-guide.en.md).

The guide also documents this manual startup path after opening Mika to prepare its startup file:

```sh
adb -s SERIAL shell id
adb -s SERIAL shell sh /sdcard/Android/data/com.wangzan101.mika/files/usb-start.sh
```

The script's name does not constrain its transport: upstream explicitly permits another existing channel that executes as ADB shell. An already authorized wireless ADB connection can therefore run the same command. This **does not prove Mika completed its own wireless pairing**, stored its own usable pairing identity or can reconnect after reboot. Do not print or inspect private pairing material or the startup file's one-time code. Confirm the app's **Phone control** status after startup, then run its compatibility self-check. [Documented computer/helper startup](https://github.com/wangzan101/Mika/blob/2b26f3f80937a320581dab66f16e6a7fda1799ce/docs/setup-guide.en.md#another-way-start-it-from-a-computer-usb-cable).

For a workstation's own wireless connection, use Android's documented pairing and connection steps. The pairing endpoint and the normal debugging endpoint are distinct roles; use the values currently displayed by Android rather than assuming they share a port. Keep codes and endpoint identities out of the public report. [Official ADB guide](https://developer.android.com/tools/adb#connect-to-a-device-over-wi-fi).

### What the native implementation explains

In the pinned `ShellService`:

- The service is designed to run as shell UID 2000, owns virtual displays and releases them with its process lifecycle.
- `createDisplay` first attempts trusted display flags. On eligible permission failures it retries without trust-dependent flags, so a created display is not proof that own focus or an independent display group is available.
- For trusted displays on Android 13+, `displayFlags` requests an own display group and `ALWAYS_UNLOCKED`; Android 14+ also requests own focus and disabled top-focus stealing. These are hidden/version-sensitive platform features. `ALWAYS_UNLOCKED` here describes the separate display's policy, not dismissal of the physical display's secure keyguard.
- A fallback display can share focus with the main display. Confirm focus behavior before input rather than interpreting successful creation as non-interference.

[Exact ShellService implementation](https://github.com/wangzan101/Mika/blob/2b26f3f80937a320581dab66f16e6a7fda1799ce/app/src/main/java/com/wangzan101/mika/cap/phone/shell/ShellService.kt).

`DisplayAwake` addresses a different issue: an own display group has its own inactivity timer, and injected input alone may not keep its composition active. It schedules per-display user activity every four seconds where supported, excludes the default display group, cancels on release and stops trying if the interface fails. This is not a blanket guarantee of CPU wakefulness, network availability or indefinite background service survival. [Exact DisplayAwake implementation](https://github.com/wangzan101/Mika/blob/2b26f3f80937a320581dab66f16e6a7fda1799ce/app/src/main/java/com/wangzan101/mika/cap/phone/shell/DisplayAwake.kt).

### Xiaomi result: keep the boundaries separate

Tested: Xiaomi Pad Mini model 25079RPDCG, Android 16, non-root, Mika 0.1.44, installed build identified as `2b26f3f`.

| Boundary | Observed result | Not established |
| --- | --- | --- |
| Built-in self-check while unlocked | 12 pass, 0 partial, 0 fail, 41 seconds | Secure-lock operation, reboot recovery or a full AI task |
| Disposable standalone shell process loading `ShellService` from installed APK; physical state `Asleep`, display `OFF`, secure keyguard `showing=true` | Create, read, tap and type passed on the virtual display | Serving-helper RPC, Mika app orchestration or full AI end-to-end completion |
| Same native-helper code, actual TikTok Studio 44.6.3 while secure keyguard showed | App launch and 1880 x 3008 capture passed | Any interaction with TikTok Studio, account action or all-app compatibility |
| Wireless ADB dropped; user re-enabled it | Helper was absent afterward | Automatic helper recovery |
| Documented `usb-start.sh` run manually in the initial session | Helper restored | Recovery without manual intervention or after reboot; no reboot test was performed |
| Follow-up after Mika own pairing, Awake/unlocked, wireless debugging on, deliberate helper-only termination | Replacement helper observed in about 5 seconds without rescue; Mika self-check after recovery 12/12 in 41 seconds | Wireless-off/locked, long-idle, roaming or reboot recovery; full AI task |

The standalone helper experiment is a diagnostic of installed native code. Do not describe it as an RPC call to the running helper or as a completed Mika AI task. A production integration needs its own app-level validation after native compatibility is established.

## 5. Screen off, keyguard and protected content are independent

Record at least these separate observations: physical display power state, overall wakefulness, keyguard showing/secure state, virtual display ID/state/group, helper lifecycle and input target. A screen-off result with no keyguard does not establish secure-lock behavior. A secure keyguard remaining visible while a separate display works does not mean the keyguard was dismissed or its protected contents captured.

Ordinary MediaProjection is a consented capture API with session and stop semantics, not equivalent to privileged shell-owned secondary-display control. Follow its consent, foreground-service and `onStop` requirements when using that API. [Android MediaProjection guide](https://developer.android.com/media/grow/media-projection).

`FLAG_SECURE` is a window protection flag. Android documents that secure windows are blanked on non-secure virtual displays and that creation of a secure virtual display requires a permission reserved for system components. Neither root availability nor an ordinary successful app capture establishes protected-window or DRM capture. Do not modify protection policies to turn a failed capture into a pass. [Window FLAG_SECURE](https://developer.android.com/reference/android/view/WindowManager.LayoutParams#FLAG_SECURE), [secure virtual displays](https://developer.android.com/reference/android/hardware/display/DisplayManager#VIRTUAL_DISPLAY_FLAG_SECURE).

## 6. Failure diagnosis without disturbing another session

| Symptom | Targeted next check | Interpretation/action |
| --- | --- | --- |
| Root display creation throws UID/package error | Selected backend, live process identity and exact exception | Use the demonstrated ADB-started Shizuku route on the Samsung; preserve the original failure record. |
| Display creates but frame freezes after inactivity | Virtual display state/group, keep-awake availability, helper liveness | A separate group's timer may explain it; do not assume another tap or keeping the main screen on proves the fix. |
| Tap changes the wrong screen or text lands elsewhere | Display ID, current task, focused window and fresh observation | Stop input, re-observe and restore prior focus if this test changed it. Shared-focus fallback needs its own test. |
| App launch returns to an already running instance | Existing task/display inventory and launch mode | Android task reuse may be involved. Do not force-stop or restart an app to manufacture a pass. |
| Helper absent after transport loss | App status and helper liveness, then authorized ADB identity | On the observed Xiaomi, manual documented startup restored it. Do not report this initial incident as automatic recovery; a later awake helper-only test passed after own pairing. |
| Secure or DRM region is blank | Whether the app uses protected windows/output | Record the limitation; another ordinary app's capture does not contradict it. |

For an app already running on another display, first save task IDs, display assignment and main-display focus. If the platform exposes task relocation and the owner explicitly chooses a disposable test, inspect that device's command help and move only the identified task, then verify both displays and restore the original task location/focus. This is a conditional diagnostic, not a general portable recipe: task launch modes, resizeability, OEM policy and API availability differ. The separate [Facebook capture experiment](observed-results.md#facebook-task-reuse-and-capture) did verify task relocation and restoration on the A32, using direct ADB task management plus MCP capture rather than pure MCP launch. That specific result is not a portability guarantee.

## 7. Cleanup, recovery and acceptance

- Release only displays/sessions created by the test through the owning app or helper's lifecycle. End the disposable native test process rather than killing an unrelated serving helper.
- Restore any task placement/focus changed by an agreed diagnostic. Preserve unrelated accessibility services, root grants and other ADB forwards.
- Remove only this test's host forward after releasing its session:

```sh
adb -s SERIAL forward --remove tcp:8732
```

Use the actual host port if a different one was allocated. Do not stop the global ADB server to clean up one experiment.

- Recheck the physical screen/keyguard and app state without entering or automating a PIN/password. Keep experiment evidence redacted and device-scoped.
- Treat app/helper updates, helper death, wireless reconnection, idle periods and reboot as separate acceptance tests. Upstream documents restart behavior for each startup path, but this field guide's Xiaomi reboot behavior is **not tested**.

A useful final report states version/build, backend and identity, physical and virtual display states, exact tested boundary, initial failures, later bounded successes and untested lifecycle cases. Do not compress these into “works locked” or “fully supported.”

## 8. Wireless-debugging recovery follow-up

See [Wireless debugging: auto-off, reconnection and helper recovery](wireless-debugging.md) for Chinese/English community reports, the normal Mika pairing procedure, the bounded awake recovery result and the remaining untested boundaries.
