# Samsung A32 / Android 13: a root-hosted screen-off controller

[Guide](../README.en.md) · [Identity and solution choices](solutions.md) · [Results](observed-results.md)

Observed 2026-11-17. This adds a **root-authorized bootstrap with a system-UID helper**, not a repair of the installed application's Root button. It does not replace the earlier successful Shizuku test or erase the original Root-backend failure.

The requested boundary was **physical screen off**, not PIN/pattern-secured keyguard. All results below are sanitized, author-reported observations. This update publishes architecture and findings, not the private controller, captured logs or an APK.

## What changed, and what did not

| Layer | Tested identity or behavior |
| --- | --- |
| Device | Samsung A32, Android 13 / API 33, existing Magisk 31.1 |
| Bootstrap | Existing authorized `su`, initial UID 0 |
| Worker | GID and UID changed to **1000** before constructing the display engine or system context; supplementary group selected as 1000 through the tested Magisk command |
| Attribution | System context package `android`, virtual display owner UID 1000 |
| Display engine | Loaded from the unchanged installed VirtualScreen v0.2.1 APK |
| Control transport | A separate host controller and private process stdio; **not** the app's serving MCP |
| UI operations | Display-bound capture/input plus system-UID UiAutomation semantic operations |
| Shizuku | Not used for this controller's operations; ADB shell remained the transport and read-only diagnostic channel |
| Device changes | Separate helper DEX files only; no framework patch, root installation, APK replacement, Magisk policy edit, keyguard change or SELinux change |

A runtime UID1000 helper is **not UID0**, and it is not an ordinary non-root app. Starting this route required existing root authorization. The process is not `system_server`; changing Unix IDs does not itself change its SELinux domain. SELinux remained **Enforcing**. Do not reproduce this by globally relaxing policy or granting unrelated privileges.

## Why direct UID0 failed

The original installed Root backend failed with:

```text
SecurityException: packageName must match the calling uid
```

A fresh UID0-only diagnostic reproduced that failure. Android 13's display-service implementation validates the supplied package against the calling UID without a general UID0 exemption. A system context's package `android` does not become a UID0 package simply because its caller is root. Android 14's implementation adds a root exemption; that source difference is not proof that every OEM build behaves identically. [Android 13 DMS](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-13.0.0_r1/services/core/java/com/android/server/display/DisplayManagerService.java), [Android 14 DMS](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-14.0.0_r1/services/core/java/com/android/server/display/DisplayManagerService.java).

The tested change aligned the worker with the system context **before** creating framework/context singletons. Conceptually:

```java
// Architecture excerpt only, not a complete runnable controller.
if (android.os.Process.myUid() != 0) {
    throw new SecurityException("ROOT_BOOTSTRAP_REQUIRED");
}
android.system.Os.setgid(1000);
android.system.Os.setuid(1000);
// Only now construct the reviewed engine/context and create an owned display.
```

The tested launcher also selected group 1000 using that Magisk release's `-g` / `-G` options. Validate the actual UID, GID, groups, permissions and SELinux behavior on the target device. Do not label a `su`-started UID2000 worker as this route.

Changing only these lines in the upstream app is **not** a complete app patch: its root live-registration path also expects UID0. The experiment used a separate controller and did not weaken or rewrite that provider's checks. The stock Root backend remains a recorded failure on this device.

## Verified results

| Test | Result | Boundary |
| --- | --- | --- |
| UID0-only display creation | Expected failure with the same package/UID exception | Negative baseline, not a successful root session |
| Root bootstrap -> UID1000 | Created, launched a probe on, captured and closed an owned virtual display | Separate root-hosted controller |
| Fresh accessibility nodes and semantic click | PASS; counter changed and was read back | Built-in probe only |
| Coordinate tap | PASS; counter changed from 0 to 1 | Fresh target/focused-window checks on the owned display |
| Unicode set-text | PASS; Vietnamese and Chinese text matched fresh node readback | Semantic action, not legacy clipboard/shell text injection |
| No helper RPC for 90 seconds | PASS; state remained readable and another click changed the counter | Bounded idle, not overnight/deep-idle or reboot proof |
| Owned-worker failure injection | SIGSTOP of the newly created test worker caused a response timeout; cleanup completed in about 9.7 seconds | Identity-checked cleanup of that worker only, not automatic service recovery |
| Rollback on a disposable source copy | Removing the UID transition reproduced the UID0 attribution failure | Working helper was left changed; this was not a phone-wide rollback |
| Final cleanup | No owned worker or probe task remained; original panel/lock/debugging settings matched the baseline | Helper DEX files retained for explicit reuse; original APK/data unchanged |

At sampled checks, the physical panel stayed in `DOZE` / `DOZE_SUSPEND`, never `ON`. During virtual-display operation, the global `PowerManager.isInteractive()` value could become true and returned false after cleanup. **Global interactivity was therefore not a valid proxy for the physical panel's power state in this test.** This observation does not guarantee an independent focus or power group on every ROM.

Secure keyguard was not configured in the test (`device_secure=false`). There is no secure-PIN/pattern result. Android13 lacks the newer independent-focus path used on some Android14+ devices; do not turn this panel-off result into a promise of concurrent, non-interfering use of the physical screen.

## Input and lifecycle details that mattered

The upstream legacy text path returned `SHELL_IDENTITY_REQUIRED` under the system-UID worker. It was excluded from this route rather than retried as shell. The custom semantic path used UiAutomation with `FLAG_DONT_SUPPRESS_ACCESSIBILITY_SERVICES`, selected the current window on the owned nonzero display and the exact target package, required a unique node selector, and disconnected after the operation. Successful action delivery was followed by fresh node readback; acceptance alone was not treated as an effect.

The controller included these checks:

1. Explicit ADB serial, model/API and reviewed APK/helper identity; no implicit default device.
2. Session-owned display and a fixed, explicitly selected component. No arbitrary default-display capture/input.
3. Physical-panel state before operations; top-resumed activity before input; focused window as an additional coordinate/key-input check. Stop if the owner lights the physical screen or changes the target.
4. No automatic app restart, force-stop or relocation of an existing task on another display.
5. Bounded replies. If an input's outcome is uncertain, do not resend it blindly.
6. On timeout, close the channel, then check PID, UID, command line and start time before terminating only the owned worker. Verify its display disappears. PID alone is insufficient because it can be reused.
7. Restore/close only owned resources; leave existing apps, grants, unrelated forwards and settings intact.

The engine's default inactivity limit is 20 minutes. The custom semantic route refreshed engine activity through its observe path. The test did not wait through the entire 20-minute limit. No boot service, Magisk autorun module, persistent network port, wireless-debugging auto-enable or background recovery daemon was installed.

## Community reports: useful evidence, not compatibility guarantees

### Chinese-language discussions

- [MAA-Meow #112](https://github.com/Aliothmoon/MAA-Meow/issues/112), May 2026: a maintainer discusses UID0 calling-UID validation during virtual-display creation. This supports investigating identity before battery settings; it is not an A32 success report.
- [MAA-Meow #198](https://github.com/Aliothmoon/MAA-Meow/issues/198), August 2026: the same package/UID exception appears with a shell-named fake context. The maintainer recommends the app's direct root mode rather than root-started Shizuku. The report does not establish this A32/controller combination or confirm the reporter's actual UID in every attempt.
- [Appinn post #11](https://meta.appinn.net/t/topic/72983/11), July 2025: the author separates a virtual app continuing while the panel is off from mouse input failing once actually locked. The post lacks enough device/version detail to infer A32 compatibility; disabling authentication was not adopted here.
- [Sunshine's October 2026 release](https://github.com/nanaoniiiii/sunshine/releases/tag/v2026.10.24.3): an author-reported S20+ Android13 virtual-desktop screen-off result is a nearby Samsung example, not proof of A32, raw UID0 or secure-keyguard support.

### English-language issue discussions

- [scrcpy #5428](https://github.com/Genymobile/scrcpy/issues/5428#issuecomment-2453421171) documents screen-off/capture/input behavior that must be checked separately. A continuing stream does not prove input works.
- [scrcpy #6643](https://github.com/Genymobile/scrcpy/issues/6643) includes discussion of screen-off behavior and competing explanations. Doze/App Freezer attribution is not established merely by the symptom; changing battery policy is not a general fix for package/UID rejection.

The local root test, not those reports, is the evidence for this A32. A stock Root-backend fix, serving-MCP integration, arbitrary-app behavior, simultaneous physical-screen use, long idle, secure lock and reboot recovery remain separate work.
