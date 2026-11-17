# Pixel 10 Pro XL: Android 17, locked input and parallel use

[English guide](../README.en.md) | [Results](observed-results.md) | [Privacy](privacy.md)

Updated 2026-11-17. These are sanitized author-reported results from tests on 2026-11-16 and 2026-11-17, not a universal compatibility guarantee. No private conversation, recipient, device identity, screenshot or credential is published.

## Historical VirtualScreen setup and root/non-root boundary

- Pixel 10 Pro XL, Android 17 / API 37, non-root.
- VirtualScreen `io.github.lejw0925.virtualscreen` v0.2.1, Shizuku v13.6.0 started through authorized ADB as **shell UID 2000**, not root.
- The app's accessibility service and backend authorization were enabled through their supported setup flows. A battery-optimization exception was approved; this does not guarantee indefinite survival.
- The serving MCP endpoint was used through an owned ADB forward to the device's loopback port. No LAN endpoint or public tunnel was enabled.
- This extends the A32 and Xiaomi results without changing them. Root is not required for this tested path; an ordinary unprivileged app alone does not have shell's capabilities.

## Keep Wireless debugging under the owner's control

This Pixel workflow explicitly **does not automatically enable Wireless debugging**. Reuse a currently authorized transport. If it disappears, use authorized USB or let the owner manually reconnect; do not enable wireless recovery, pair silently, modify the ADB authorization timeout, or switch to TCP 5555.

Shizuku **Start on boot was kept OFF** through its own settings UI. The tested release's boot-receiver path can enable ADB/wireless and change the authorization timeout when its prerequisites are met. Avoiding the wireless-pairing screen alone is not enough to establish a no-auto-enable policy. This is a configuration-specific finding, not a claim that every Shizuku installation does this. See [Shizuku v13.6.0 source](https://github.com/RikkaApps/Shizuku/tree/v13.6.0).

No reboot was performed to validate persistence. Do not apply the Xiaomi/Mika recovery recommendations to Pixel without a separate decision.

## New result: securely locked coordinate control through VirtualDeviceManager

On **2026-11-17**, a separate, non-root **shell UID 2000 controller** created its display while the Pixel was already securely locked and its physical panel was OFF. It used neither Shizuku nor the serving VirtualScreen MCP endpoint. This supplements the older failed coordinate test below; it does not turn that failure into a pass or repair the stock app.

The decisive route, reported by the [MoonClicker author on Pixel 7a/API 37](https://github.com/kuomartin/MoonClicker/issues/124#issuecomment-6128968658) and then tested separately on this Pixel 10 Pro XL, was:

1. Create an owned CompanionDeviceManager association for `com.android.shell` with profile `android.app.role.COMPANION_DEVICE_APP_STREAMING`.
2. Create a `VirtualDevice` from that association, using `VirtualDeviceParams.LOCK_STATE_ALWAYS_UNLOCKED` **for the virtual device only**. The physical keyguard and PIN configuration remain unchanged.
3. Create a trusted virtual display **without `OWN_DISPLAY_GROUP`**. On this tested build, the linked-device path gave it an independent group greater than zero, rather than the problematic primary-group path.
4. Reject input unless the owned display is ON, the requested package matches the session, its virtual window has focus, and the physical device remains locked, secure and OFF. Use display-local coordinate bounds, not default-display input.
5. Verify fresh nodes and uncached images after input. An acknowledged injection alone is insufficient.

This is build-sensitive platform behavior. The original [technical research](https://github.com/kuomartin/MoonClicker/blob/main/docs/research/vd-display-group-android17.md) also distinguishes display state from power-group wakefulness. Do not change global desktop flags, power policy, keyguard or framework protections to force a pass.

### What actually passed

| Check | Observed result |
| --- | --- |
| Cold create while locked | Independent virtual group, virtual ON; physical OFF, deviceLocked/deviceSecure true, global interactive false |
| Coordinate tap | Fresh probe counter changed 0 to 1 |
| Unicode semantic text | Vietnamese and Chinese text read back exactly |
| Native coordinate swipe | Visible probe list changed from its initial items to later items |
| Real app | Google Calculator displayed 7×8 and preview 56; test expression cleared back to blank, no equals/history write |
| Idle without helper traffic | After **308.7 seconds**, virtual ON; a coordinate tap changed counter 1 to 2 while physical OFF and securely locked |
| Negative guards | Wrong-package and out-of-bounds requests rejected; session remained usable |
| Recreate and cleanup | Owned association/role removed, then a fresh locked session created and closed successfully |

Physical state was sampled before/after operations, not continuously traced. The idle interval used saved event-file timestamps. An earlier idle attempt saw physical ON with interactive false; the strict guard rejected input and the prototype closed. It was **not** counted as an idle pass. The reason for that panel-state transition was not established.

### Lifecycle and privilege restoration

An APP_STREAMING association grants a **persistent companion role** to shell. Closing the virtual display alone does not restore this side effect. Record existing associations/role holders before mutation, keep an ownership receipt, close the owned device, remove only the exact owned association and verify that existing entries/roles remain intact. Association allocation counters are monotonic and were not reset.

The custom controller binds package/display identity, validates helper PID, UID and process start time before signals, and handles a process exiting between identity checks. The latter race was reproduced during cleanup, fixed, then recovered through the receipt; the final create/state/close cycle exited successfully. Thirteen local controller tests passed. These private-controller tests are separate from this public documentation repository's tests. Forced-stop/KILL escalation and network-loss recovery were not live-tested.

Final device checks found the original association entries, role holders and ADB settings unchanged, with owned displays, worker, forward and temporary DEX removed. No root, automatic wireless activation, global wake call, app restart, message send or keyguard change was used. The observed transport was existing wireless ADB; a reported USB attachment did not establish USB transport.

**Delivery boundary:** a standalone controller proof, not a distributed app patch, serving-MCP integration or model-autonomous AI task. Long/overnight idle, reboot, roaming, IME/Back, protected-content capture and arbitrary apps remain unverified. Source and raw private captures are not redistributed here.

## Historical VirtualScreen results by boundary

| Boundary | Observed result | Important limit |
| --- | --- | --- |
| Unlocked serving MCP | Live nodes/capture, coordinate counter tap and text input passed on a probe | Not all apps or gestures |
| Locked, stock virtual display | Virtual display followed the physical display OFF; black/pending capture or unavailable nodes | Requested own-group flags did not establish an independent power group on this device |
| Locked, experimental per-display power override | Serving MCP semantic click and semantic set-text passed on a probe; physical display OFF, secure device/keyguard locked before and after | Conditional workaround, not a stock-app fix; not a locked WhatsApp test |
| Locked coordinate tap through the older power-override route | RPC acknowledged the call, but the counter did not change: **FAIL** | An acknowledgement is not input-effect proof |
| Capture after power-policy reset | An old frame could be returned while fresh nodes were unavailable | A screenshot alone can be stale |
| Human/agent parallel use while unlocked | User-approved background WhatsApp task was moved to a virtual display; live conversation reading and a separately authorized message send worked | Same app data/account, not an isolated messaging instance |
| Delivery and cleanup | Fresh UI showed Delivered; WhatsApp returned to display 0 as not visible; owned display, lease and forward were removed | Delivered is not Read; cleanup does not retract a sent message |
| Main-display continuity | TikTok remained the physical foreground at sampled checks, with user-driven activity changes in its task | No continuous frame-level proof against every transient focus change |

For the historical VirtualScreen route, long idle, roaming, reboot recovery, arbitrary third-party apps while locked, and both parties simultaneously operating the same app/task remain **untested**. The separate 2026-11-17 controller result above covers a bounded 308.7-second idle and Calculator, not those broader guarantees. A model-autonomous AI workflow was not evaluated.

## Conditional locked-screen power workaround

The logical virtual display was observed in power group 0, despite requested own-group flags. The Android 17 group allocator and mapper offer an explanation consistent with this result, but the device's exact feature-flag combination was not verified. Do not infer a universal Android 17 regression from one build.

The tested shell helper called the hidden/version-sensitive Binder method:

```java
// Conceptual API signature, not a standalone or portable Java program.
IDisplayManager.requestDisplayPower(ownedVirtualDisplayId, Display.STATE_ON);
```

`MANAGE_DISPLAYS` is required; it was already available to shell on the tested build. No new permission, root, global wake/userActivity operation or keyguard change was used. This is not a method on the ordinary `DisplayManager` API. The platform may reapply policy later.

A reproduction must first acquire the session lease and validate current nonzero virtual-display identity, type, owner and session ownership. Record an override receipt **before** the call so an interruption can still be cleaned up. Never use it on display 0 or claim another session's display. Compare physical power/lock and debugging settings before and after. Use fresh semantic nodes to verify a real effect, not just a cached image or RPC success.

For an override owned by the current test, the tested reset command was:

```sh
adb -s SERIAL shell cmd display power-reset OWNED_VIRTUAL_DISPLAY_ID
```

Reset only the recorded override; then close the owned display. Do not fabricate ownership metadata or reset an unrelated display. A process-local power workaround does not promise restart recovery.

Primary source at Android framework commit `94b4c163b7dfe5ce3607f7bb8456f9573f7de57d`: [IDisplayManager](https://android.googlesource.com/platform/frameworks/base/+/94b4c163b7dfe5ce3607f7bb8456f9573f7de57d/core/java/android/hardware/display/IDisplayManager.aidl), [LogicalDisplayMapper](https://android.googlesource.com/platform/frameworks/base/+/94b4c163b7dfe5ce3607f7bb8456f9573f7de57d/services/core/java/com/android/server/display/LogicalDisplayMapper.java), [DisplayGroupAllocator](https://android.googlesource.com/platform/frameworks/base/+/94b4c163b7dfe5ce3607f7bb8456f9573f7de57d/services/core/java/com/android/server/display/DisplayGroupAllocator.java).

## Moving an existing background task without restarting the app

Launching an app on another display can reuse its existing task. Do not silently restart/force-stop it or move a task the owner is currently using. Respect any MCP restart-approval flow. A separately approved background-task relocation is not permission for a restart.

On this build, the hidden Binder API below allowed the approved task to be moved and then returned to the **bottom**, not the foreground, of the physical display:

```java
// Conceptual platform API, requires INTERNAL_SYSTEM_WINDOW on this build.
// Resolve and validate live IDs; do not copy IDs from an earlier session.
atm.moveRootTaskToDisplayOnTopOrBottom(taskId, ownedVirtualDisplayId, true);
// Before closing the virtual display, restore the approved task as background.
atm.moveRootTaskToDisplayOnTopOrBottom(taskId, 0, false);
```

The shell caller had the required permission in the tested session. A real helper must verify the package/root task, expected source display and physical `visible=false` before moving out; refuse mismatches. Check virtual target/package and physical foreground before every input. If the owner switches to the target app or takes over control, stop and re-observe. Do not force the owner back to a previously observed app.

**Do not replace the restore call with a command that defaults to `onTop=true`.** Restore the task before closing its display, otherwise cleanup can alter the user's task lifecycle. Restoration does not reverse content edits or external actions.

The framework still adjusts focus after reparenting. `onTop=false` is not a universal guarantee of zero transient focus changes; the evidence here is sampled foreground checks and the observed session outcome. This is a tested, version-sensitive route, not a general no-disruption promise for every app.

Primary source: [IActivityTaskManager](https://android.googlesource.com/platform/frameworks/base/+/94b4c163b7dfe5ce3607f7bb8456f9573f7de57d/core/java/android/app/IActivityTaskManager.aidl), [ActivityTaskManagerService](https://android.googlesource.com/platform/frameworks/base/+/94b4c163b7dfe5ce3607f7bb8456f9573f7de57d/services/core/java/com/android/server/wm/ActivityTaskManagerService.java), [RootWindowContainer](https://android.googlesource.com/platform/frameworks/base/+/94b4c163b7dfe5ce3607f7bb8456f9573f7de57d/services/core/java/com/android/server/wm/RootWindowContainer.java), [Task](https://android.googlesource.com/platform/frameworks/base/+/94b4c163b7dfe5ce3607f7bb8456f9573f7de57d/services/core/java/com/android/server/wm/Task.java).

## Historical serving-MCP session checklist for Codex, Claude or another operator

1. Enumerate devices, verify model and choose an explicit serial. Recheck all process, task, display and session IDs; old examples and temporary helpers may be stale.
2. Reuse the authorized transport without changing wireless settings. Inspect an existing forward before creating a new one with `--no-rebind`.
3. Verify the backend and controller, acquire a lease and create only an owned display. Do not take over a phone-controlled session.
4. Inspect the requested app's existing task. If relocating a background task, obtain approval for that task and record its restoration route first.
5. Observe fresh virtual nodes before input. Validate recipient and exact content before a separately authorized send; drafting is not permission to send. If delivery is uncertain, read the result instead of retrying blindly.
6. Verify the actual UI effect, physical foreground and relevant power/lock state. Report failed or untested boundaries separately.
7. Restore relocated tasks to background before closing the display; reset only owned overrides, release control and remove only the session's forward. Leave app data and unrelated settings intact.

This public checklist is intentionally not a copy of a private agent configuration. No automatic send script, real recipient, task ID, local credential path or private capture is distributed.
