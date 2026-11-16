# Diagnose the failing boundary

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
