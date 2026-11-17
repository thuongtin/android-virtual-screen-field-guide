# Xiaomi Pad Mini: locked serving-helper and app-action results

[Observed results](observed-results.md) · [Machine-readable cases](../examples/observations.json) · [Sources](sources.md)

Updated **2026-11-17**. These are author-reported, bounded experiments on a non-root Xiaomi Pad Mini, Android 16 / API 36, with the installed **Mika 0.1.44**, build `2b26f3f`. The public repository documents methods and sanitized outcomes. It does **not** ship the private harness, a production controller or an SDK.

## Outcome first: three different execution boundaries

| Experiment | Execution path | Verified result | Do not infer |
| --- | --- | --- | --- |
| Initial locked diagnostic, 2026-11-16 | Disposable shell process instantiated `ShellService` from the installed Mika APK | Separate display, readable test-page nodes, counter increment and text readback while physical screen was OFF and secure keyguard showed | Serving-helper RPC or app self-check under lock |
| Locked Compatibility self-check, 2026-11-17 | Mika's actual app UI called its **existing serving helper Binder**; separate UI host only presented/observed/clicked Mika | **12 pass, 0 partial, 0 fail, 0 skipped in 42 seconds** | Model-AI workflow, long idle, reboot or every app |
| Telegram Saved Messages, 2026-11-17 | Standalone installed-Mika native display host plus temporary UiAutomation | One requested test message sent to the user's **own Saved Messages**, read back as `Sent` / `Seen`, then empty composer | Mika serving RPC, AI execution, delivery to another person or a second recipient |

All three used real installed code and real device UI, but they are not interchangeable evidence. The earlier unlocked 12/12 result in 41 seconds, initial notification partial, manual helper recovery and later awake-only paired-helper recovery remain recorded in [observed results](observed-results.md#case-b-non-root-xiaomi-pad-mini).

## 1. Environment and permission boundary

- Android 16 / API 36, arm64; no root, bootloader change or framework patch.
- Installed Mika 0.1.44 and its existing shell-UID helper were retained. No app replacement or Binder authorization change was made for the new locked tests.
- Physical state at **all sampled host responses**: panel `OFF`, `interactive=false`, `locked=true`, `secure=true`.
- The physical display's main top-task stayed the same at samples. This is **not a continuous focus/panel trace** and does not prove that no transient focus change was possible.
- Existing Mika app/helper PIDs and compared settings stayed unchanged across cleanup. The self-check run additionally verified the installed Mika APK hash. The Telegram workflow did not separately establish its target-app PID or APK hash. No reboot, lock credential entry or model/provider request was used.
- For Mika, the user separately approved temporary relocation of its identified background task. For Telegram, the user requested opening the app and sending a self-message; the operator announced the background-task movement before proceeding. That scoped app workflow is not blanket authorization to move unrelated tasks. Existing tasks were not force-stopped or relaunched.

Settings that already existed on this Pad are not generic setup instructions. In particular, this result does not authorize turning on wireless debugging or copying Xiaomi recovery settings to another device.

## 2. How the locked self-check reached the real serving helper

### The authentication path

Mika's `HelperProcess` runs as shell UID 2000 and creates `ShellService` with the installed app UID as its allowed Binder client. It hands the Binder to the app through `HelperHandoffProvider` and `HelperHub.offer()`. The handoff checks actual/reported UID and PID, APK identity, a rotating nonce and the Binder's reported process identity. The exported handoff is **not** a public “get current helper Binder” endpoint.

The app obtains `IMikaShell` through `PhoneServices` / `HelperHub`; `AndroidSelfCheck` acquires the app's shared connection and invokes the existing helper. The separate native UI host did **not** replace this Binder, extract its authentication material or call the serving Binder from an unauthorized shell client. [HelperProcess](https://github.com/wangzan101/Mika/blob/2b26f3f80937a320581dab66f16e6a7fda1799ce/app/src/main/java/com/wangzan101/mika/cap/phone/shell/HelperProcess.kt), [HelperHub](https://github.com/wangzan101/Mika/blob/2b26f3f80937a320581dab66f16e6a7fda1799ce/app/src/main/java/com/wangzan101/mika/cap/phone/shell/HelperHub.kt), [ShellService](https://github.com/wangzan101/Mika/blob/2b26f3f80937a320581dab66f16e6a7fda1799ce/app/src/main/java/com/wangzan101/mika/cap/phone/shell/ShellService.kt).

### The observed run

The UI host created its own temporary display, moved the consented background Mika task onto it, opened the actual Compatibility self-check UI and pressed Start. While the app ran the check, the host sampled physical state/captured frames without competing UiAutomation node queries. Nodes were read before and after the self-check.

The app reported:

```text
Result: 12 pass, 0 partial, 0 fail, 0 skipped in 42 s
```

The report covered display creation with own focus, Mika test-page and Settings launch, nonblank image/tree reading, tap, ASCII and Chinese text, scroll, Back, 15 seconds of changing frames/tree, unchanged main top-task, a local browser test, sandbox processes and app-copy capability. App-copy capability does not prove a new profile was created or configured.

This is stronger than the previous native-only locked diagnostic: the app's own self-check used its existing serving IPC while locked. It is still not an AI task and did not send content to a model provider. [AndroidSelfCheck](https://github.com/wangzan101/Mika/blob/2b26f3f80937a320581dab66f16e6a7fda1799ce/app/src/main/java/com/wangzan101/mika/selfcheck/AndroidSelfCheck.kt), [SelfCheckScreen](https://github.com/wangzan101/Mika/blob/2b26f3f80937a320581dab66f16e6a7fda1799ce/app/src/main/java/com/wangzan101/mika/ui/SelfCheckScreen.kt).

### Connection lifetime matters

Do not create an arbitrary extra connection and call unbind as cleanup. `BuiltinShellConnection.unbind()` calls the helper's `releaseAll()`, which can affect other helper-owned displays and resources. The completed test used the app's supported self-check lifecycle; it did not destroy/restart the serving helper. [BuiltinShellConnection](https://github.com/wangzan101/Mika/blob/2b26f3f80937a320581dab66f16e6a7fda1799ce/app/src/main/java/com/wangzan101/mika/cap/phone/shell/BuiltinShellConnection.kt), [SharedShell](https://github.com/wangzan101/Mika/blob/2b26f3f80937a320581dab66f16e6a7fda1799ce/app/src/main/java/com/wangzan101/mika/cap/phone/shell/SharedShell.kt).

## 3. Existing-task relocation and Android 16 restoration

### Preserve the failed first attempt

The first host reused the API 37 method `moveRootTaskToDisplayOnTopOrBottom`. On this API 36 device it threw `NoSuchMethodException` before task mutation. Mika remained on its original display; the temporary display was released. Compiling against an SDK did not establish runtime method availability.

The corrected Android 16 path used `moveRootTaskToDisplay` and Mika's own `keepBehind` restoration strategy. It required neither organizer takeover nor a target TaskDisplayArea token. [Pinned keepBehind implementation](https://github.com/wangzan101/Mika/blob/2b26f3f80937a320581dab66f16e6a7fda1799ce/app/src/main/java/com/wangzan101/mika/cap/phone/shell/ShellService.kt#L907).

### Bounded state machine, not a replayable command recipe

```text
BASELINE
  identify current device/user and exact background app task
  record package, task identity, display, visibility, main top-task and physical state
  preflight task token and move/restore methods; reject unsupported task types
HOST_READY
  create only the owned virtual display
MOVE_TO_OWNED_DISPLAY
  recheck task ownership/background state and the explicit relocation consent
  move only that existing task; verify its resulting display/package
OBSERVE_AND_ACT
  use fresh target observations and verify each state change
RESTORE_BACKGROUND
  WCT: setHidden(taskToken, true); apply
  moveRootTaskToDisplay(task, physicalDisplay)
  one WCT: reorder(taskToken, false) + setHidden(taskToken, false); apply
VERIFY_RESTORE
  require original display and background visibility, original main top-task
CLOSE_OWNED_RESOURCES
  release owned display only after successful task restoration
  verify no temporary workers/displays/files remain
```

WCT means `WindowContainerTransaction`. Frameworks may apply property changes before hierarchy operations in one transaction; source-level call ordering is not a continuous focus guarantee. The completed runs verified background restoration by readback. Do not silently fall back to unhide-at-top, removeTask, restart, force-stop or closing a display while the user's app task is still on it. If restoration fails, preserve ownership/state evidence and resolve that task before releasing its display. This document does not claim crash-proof lifecycle recovery.

## 4. Telegram: one action with destination and draft verification

### Scope and execution boundary

The target was the installed native Telegram variant `org.telegram.messenger.web` and the user's **own Saved Messages**. The package suffix does not mean this was browser automation. Its exact Telegram app version was not captured in this experiment, so it must not be inferred from a later installation. A standalone shell process used installed Mika native display code and a temporary UiAutomation connection. Telegram's existing background task was moved with consent and later restored. **This was not Mika app-serving RPC and not a model-AI workflow.** No message body, account identifier or private chat screenshot is published.

### Observation-driven recovery, not blind input retries

Some early accessibility reads returned `root=null` / `TARGET_PACKAGE_NOT_VISIBLE`. No Send was attempted during those failures. A display-local focus tap on the freshly observed composer restored accessible nodes; the empty editor was observed before insertion.

An early draft-helper polling patch assertion failed, and the subsequent old read attempt also failed before draft confirmation. Build execution was changed to fail fast before further runs. In the successful flow, text insertion and fresh draft readback remained on **one accessibility connection**, avoiding a reconnect that could lose the useful text/editor state.

These are retained failures and corrections, not erased by the final success. A transport/RPC acknowledgement alone was never accepted as proof of draft insertion or message delivery.

### The verified send sequence

```text
OBSERVE_DESTINATION
  require current target package and Saved Messages header
OBSERVE_EDITOR
  require a unique Message editor and its observed empty state
COMPOSE_WITHOUT_SEND
  set only the requested draft; refresh/read it on the same connection
VERIFY_BEFORE_SEND
  require Saved Messages header, exact requested draft and visible Send control
SEND_ONCE
  invoke one guarded coordinate tap on the freshly observed Send bounds
VERIFY_AFTER_SEND
  require a fresh matching message entry and Sent / Seen UI status
  require composer returned to its Message placeholder
RESTORE_AND_CLOSE
  return Telegram task to original display in background; then close owned display
```

The draft helper's result explicitly said `sent=false`; the actual Send occurred afterward through **one** guarded native tap. There was no retry of Send and no deletion to conceal a duplicate. Coordinate injection was paired with semantic destination/draft verification and post-action readback, not treated as self-proving.

The observed status was **Sent / Seen**. In the user's own Saved Messages, `Seen` is a Telegram UI state, **not proof that another person read anything**. The final composer was empty. One intentional sent message remains; source rollback and device cleanup do not recall it.

## 5. Cleanup and what rollback means

For the serving self-check:

- Mika returned to its original background task on the physical display before the UI host closed its display.
- Before/after task-ID sets matched; only the physical display remained.
- App and serving-helper PIDs, installed APK hash and compared settings/grants stayed unchanged.
- Temporary workers and owned DEX were removed. The app's self-check result was retained.

For Telegram:

- Telegram returned to its original display with `visible=false` before display release.
- Only the physical display remained; temporary native process and both temporary DEX files were removed.
- Existing Mika app/helper PIDs, compared settings and lock state stayed unchanged.
- The single requested message remained in Saved Messages.

Both experiments also tested source rollback on a disposable copy and rebuilt it successfully. **Source-copy rollback is not device restoration**, and neither operation reverses the intentional sent message. Device restoration was verified separately.

## 6. Remaining limits

- No autonomous model-AI task or provider call was tested.
- No overnight idle, reboot, roaming or locked wireless-off recovery was established by these runs.
- The 42-second report and its 15-second changing-frame check are not long-term stability evidence.
- Main-task and physical-state observations were sampled, not continuous traces.
- No claim covers arbitrary apps, protected content, multiple simultaneous actors in one app task or production harness failure recovery.
- No claim generalizes the successful Android 16 task methods to Android 17 or other OEMs.
- Private raw evidence is not shipped. Public summaries are not independently replayable logs, and this guide does not distribute the harness or secrets needed to recreate an authenticated app session.
