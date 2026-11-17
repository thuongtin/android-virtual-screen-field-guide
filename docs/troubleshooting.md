# Diagnose the failing boundary

> A32 root update (2026-11-17): [root-bootstrap / system-UID controller](a32-root-android13.md). This is a separate screen-off path, not a stock Root-backend or secure-keyguard fix.

> Pixel Android 17 update: see [the dedicated workflow and evidence boundaries](pixel-android17.md), including locked semantic input, parallel use, and the no-auto-wireless policy. Do not apply Xiaomi recovery settings to this Pixel workflow.

[Guide](../README.en.md) · [Reproduction](reproduce.md) · [Observed results](observed-results.md)

| Symptom | What to inspect | What not to conclude |
|---|---|---|
| Root works in shell, but display creation fails | Exact error, selected backend, calling UID/package, ROM/API | That root is missing, or that a wider grant fixes attribution |
| `packageName must match the calling uid` | Supported backend implementation and attribution; try the documented ADB-started Shizuku path on the tested Samsung | That root disables Binder checks |
| Shizuku runs but app has no access | Startup identity, app-specific Shizuku permission, backend selection | That installation alone authorized the app |
| Helper absent after wireless transport returns | Process identity, app status, documented startup method | That locking alone caused the failure or pairing the Mac paired the app |
| Display exists but screenshot is blank | Intended display ID, app task, current frames, secure-window status and display lifecycle | That a source-level method or a nonzero display ID proves visible content |
| Virtual frame freezes | Display state/group, compositor updates, helper liveness and idle timing | That a tap return code proves the screen updated |
| Tap returns success but UI does not change | Fresh nodes, layout settlement, bounds, display/task ownership and actual state delta | That the action was performed, or that it should be blindly repeated |
| Unicode typing differs from ASCII | Input method, accessibility connection and the tool's supported text path | That successful ASCII input covers every input method |
| Main screen changes unexpectedly | Shared-focus fallback, wrong display/task, task reuse, windowing mode | That every created virtual display has independent focus |
| Main wakefulness says `Awake` | Internal display's power state versus the virtual display | That the physical panel is necessarily lit |
| App already has a task elsewhere | Current task/display, pending restart request, unsaved work | That opening it authorizes force-stop or restart |
| `DISPLAY_LAUNCH_REJECTED` after task relocation | Whether the existing task is already correctly displayed and can be observed | That relaunch is needed to capture a valid existing frame |
| MCP request rejected as duplicate | Per-request JSON-RPC IDs and session health | That a prior input was not delivered |
| `LEASE_REQUIRED` / `CONTROL_BUSY` | Current controller, lease validity, any phone-side preview takeover | That it is appropriate to disable ownership arbitration |
| Old UI prompt no longer exists | A fresh observation of the current app | That a requested Save/confirm was already performed |
| OEM background exemptions enabled, helper still dies | Actual process and transport chronology | That exemptions guarantee indefinite service life |

## Wireless debugging turns off

Separate the switch, transport, authorization and helper states. See [Chinese/English community reports and the Mika follow-up](wireless-debugging.md) before treating authorization timeout, battery settings or legacy TCP as interchangeable fixes. The follow-up verified awake helper-only recovery with wireless debugging still enabled, not locked wireless-off or reboot recovery.

## A focused failure report

Use a redacted template like this, without a device serial or account identifier:

```text
Date/build:
Device family and Android/OEM version:
App/backend versions:
Backend identity: app / shell / root
Startup path: app UI / ADB / own wireless pairing / other
Physical display state:
Secure keyguard state:
Virtual display state and test-local ID:
App-level path or standalone native diagnostic:
Operation and expected state delta:
Actual output/state delta:
Cleanup verified:
Untested boundary:
```

State whether outputs came from source inspection, the actual installed app, an app self-check, a disposable native test, or a complete user workflow. A report that says only “works” or “does not work” hides the most useful distinction.

## Stop rather than guess

Stop further input when the target display/app changes unexpectedly, the device is no longer identifiable, an input result is uncertain, a permission or restart decision appears, or a protected surface refuses capture. Inspect the relevant boundary and keep partial results. Do not repair a missing prerequisite by changing unrelated device security, account or network settings.

## Newer locked-device findings

| Symptom | What to inspect | Bounded response | What not to infer or do |
| --- | --- | --- | --- |
| Pixel coordinates accepted but no visible change | Actual display group, virtual power state, fresh counter/readback | Compare the historical power-override route with the separately tested [CDM/VDM path](pixel-android17.md) | Do not repeatedly tap or call an accepted RPC a success |
| `moveRootTaskToDisplayOnTopOrBottom` missing on Pad | API level and method inventory before task mutation | Use the source-backed Android16 task restoration described in [Pad details](xiaomi-pad-mini-android16.md) | Do not move a task until its background restoration path is known |
| Accessibility window exists but root is null | Current package/task/focus, fresh image and whether a mutation was already delivered | In the Telegram case, a display-local tap on the observed composer restored nodes; same-connection editor refresh verified the draft | Bounded observation failure is not permission to repeat Send or replay text blindly |
| Process disappears during cleanup | Exact owned PID/UID/start-time identity and `/proc` absence | Treat verified process disappearance as absence, then continue owned-resource cleanup | Do not kill a reused PID or skip persistent association/role cleanup |
| A closed display leaves an APP_STREAMING role | Baseline role/association inventory and exact ownership receipt | Remove only the owned association and verify original role holders | Do not remove another session's role/association or reset allocator counters |
| App self-check passes but agent task has not run | Whether a model/provider was configured and an actual requested workflow completed | Label the result app/helper compatibility, not autonomous AI | No API key/model setup or external request was tested by the Pad self-check |

### Messaging with uncertain delivery

Stop input and inspect the conversation if the Send result is uncertain. Do not retry merely because a command timed out. Confirm destination and draft before Send, issue one action, then look for the exact new message and a cleared composer. Saved Messages `Sent`/`Seen` is a self-chat UI status, not evidence that another person read a message. Return the task to the agreed background state afterward; task cleanup does not undo a sent message.

### Cleanup failures are not all equivalent

If a source rollback succeeds, report only source restoration. If restoring a task fails, keep ownership records and do not close its display hoping that Android will place it correctly. On the Pad, the tested transaction grouped background reorder with unhide; an unhide-only fallback is intentionally excluded. If a role or another session's ownership is ambiguous, preserve it and report the unresolved state rather than broadly resetting system settings.
