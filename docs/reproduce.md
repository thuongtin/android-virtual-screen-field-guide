# Reproduction and acceptance checklist

This repository publishes a field guide and redacted results, **not the private diagnostic controllers, an installable product patch or a universal automation SDK**. Upstream app workflows can be checked through their own UI. Custom-controller results require a separately reviewed implementation; the API descriptions here are not a complete executable harness.

Start with the [acceptance matrix](acceptance-matrix.md), then select the exact route: [A32 root](a32-root-android13.md), [Pad Android16](xiaomi-pad-mini-android16.md), or [Pixel Android17](pixel-android17.md). Do not combine commands or success claims from different devices/backends.

## 1. Identify the device and user without changing anything

Read the inventory, then explicitly select the intended device. Never let a script default to the first connected phone or emulator.

```sh
adb devices -l
# Set SERIAL to the selected device from that live inventory, not a historical example.
: "${SERIAL:?Select and verify one device serial first}"
adb -s "$SERIAL" get-state
adb -s "$SERIAL" shell getprop ro.product.model
adb -s "$SERIAL" shell getprop ro.product.device
adb -s "$SERIAL" shell getprop ro.build.version.release
adb -s "$SERIAL" shell getprop ro.build.version.sdk
adb -s "$SERIAL" shell am get-current-user
adb -s "$SERIAL" shell id
adb -s "$SERIAL" shell dumpsys power
adb -s "$SERIAL" shell dumpsys window policy
adb -s "$SERIAL" shell cmd display get-displays
```

The recorded workflows used user 0. Reject another user/profile until the task explicitly covers it. Check the actual helper UID separately: `adb shell id` reports the transport shell, not the UID of an existing app or root-hosted worker.

Record physical/virtual power, keyguard showing, device locked/secure, foreground task, existing display ownership and relevant settings privately. Keep the dumps private because they can contain app/activity and device information. These read-only commands neither grant control nor prove that input will work.

## 2. Keep setup separate from an established control session

If the installed backend is already usable while locked, inspect that path first. Do not require an unlock just to make a test easier. If initial pairing, an installation prompt, an app setup page or a credential challenge really needs owner interaction, identify that step and have the owner complete it. Do not enter/guess a PIN, disable keyguard or change lock settings to obtain a pass.

For a deliberate installation or upgrade, verify the upstream release artifact and recorded hash, preserve existing app data, and specify both serial and intended user. Do not install merely because an APK is available. Installation, app launch, backend startup, control ownership and working input are separate checks.

### VirtualScreen / Shizuku

Verify the installed version and backend state. Reuse a healthy server; otherwise follow the installed upstream version's official startup procedure. Check the actual runtime identity and a harmless operation before claiming success. On the tested A32, stock Root selection failed attribution while stock shell Shizuku worked. The later root-hosted controller is a different implementation, not a repair of that stock backend.

For Pixel, the recorded policy explicitly excluded automatic wireless debugging changes and kept Shizuku Start on boot OFF. An authorized USB connection or an already authorized transport is distinct from enabling a new transport. Do not copy the Pad's recovery configuration to Pixel.

### Mika / Pad

Confirm its **own** pairing and serving-helper state. A Mac being paired is not proof that Mika is paired. Do not replace a healthy serving helper or create/unbind an extra Binder connection just to test it: the interface authenticates Mika's UID, and connection teardown can release other displays.

For the tested locked app self-check, a separate native host temporarily held the consenting user's background Mika UI; the app then called its existing serving Binder. For Telegram, a standalone host used installed native code plus UI automation. Label these routes separately.

## 3. Acquire only resources that this session owns

For a serving MCP route, read status, initialize and acquire control using the installed version's protocol before creating a display. Stop if the phone or another operator owns control. Keep the lease/session identifiers private and retain enough state to clean up only your resources.

Before creating a forward:

```sh
adb forward --list
: "${HOST_PORT:?Choose an unused local port and record ownership}"
adb -s "$SERIAL" forward --no-rebind "tcp:$HOST_PORT" tcp:8732
```

This example is for the documented VirtualScreen loopback endpoint, **not** Mika's Binder interface. Verify local listener binding, never expose it publicly, never overwrite another forward, and remove only the exact mapping created by this session. Do not print tokens into shared logs or command transcripts.

For the Pixel custom VDM route, additionally snapshot association/role state. Creating an APP_STREAMING association grants a persistent role; display teardown alone is incomplete cleanup. Keep the owned association identity and original role holders in a private receipt.

## 4. Decide what to do with an existing app task before launching

Inspect current tasks, their display, package, user, visibility and focus. Launching an activity on a virtual display may reuse an existing task on the physical display. A virtual display is not a separate account or app-data sandbox.

- If the user is using that app/task, stop and agree on separation instead of force-stopping, restarting or silently pulling it away.
- A background task can be moved only within the owner's requested/approved operation. Verify its identity immediately before movement and keep a restoration receipt.
- Preflight the restore API before the first move. The Pixel bottom-placement method was absent on the tested Pad API36.
- Reject pinned, always-on-top or otherwise organizer-managed cases unless their behavior has been separately established.
- On Pad, the tested return path hid the task, moved it to display0, then grouped bottom reorder with unhide in one WCT. No unhide-only fallback, broad reset, removeTask or app restart was used. See the [exact sequence and limits](xiaomi-pad-mini-android16.md).

A root/privileged identity does not make an unknown restoration path acceptable.

## 5. Observe, act once, verify a real state change

Before input, verify the owned virtual display is live, the intended task/package has focus, and the physical state still matches the agreed test condition. Restrict input/capture to the virtual display. Stop input if the target changes; do not redirect a failed action to display0.

Use fresh image or node evidence to locate a control. A stale node, old coordinate, empty accessibility root or accepted injection response is insufficient. First establish a harmless state delta such as a probe counter or a local test field. Keep standalone diagnostics, app self-checks and real user workflows distinct.

For messaging:

1. Confirm the actual destination, not just a similar list-row name.
2. Prepare the exact approved draft and read it back from the editor.
3. Confirm the current Send control, destination and draft immediately before the action.
4. Send only when explicitly requested, **once**.
5. Read back the new message, UI status and empty composer. If delivery is uncertain, inspect before any retry; never infer failure solely from a timeout.

The observed Telegram `Sent`/`Seen` label was in the owner's Saved Messages, not evidence of a different recipient's acknowledgement. Preserve the intended message when cleaning up test resources.

## 6. Test only the requested lock/idle/recovery condition

Power-off, keyguard showing, device locked and device secure are different fields. Use the owner's existing lock configuration. An A32 screen-off result with secure=false is not secure-lock evidence. A displayed screenshot may be cached; require a fresh state change after input.

Keep active self-check duration, no-helper-traffic idle and injected-failure recovery separate. The Pad self-check ran for 42 seconds and included 15 seconds of changing frames/tree; that is not the Pixel's 308.7-second no-traffic idle test or a wireless-off recovery test. Do not reboot, disable debugging, kill a serving helper, switch networks or alter authorization timeout merely to extend a success claim.

No before-first-unlock-after-reboot result is claimed. See [lock-state definitions](acceptance-matrix.md#lock-state-is-not-a-single-boolean).

## 7. Restore tasks before closing displays

Use this order, adapted to the specific backend:

1. Finish or stop the owned action, preserving its actual outcome. A sent message remains sent.
2. Restore any moved user task to the agreed background location **before** closing its display. Read back display, visibility and physical foreground.
3. Reset a per-display override only if this session created it and has its receipt.
4. Close only owned displays; release only the session's lease/control.
5. Remove only owned forwards/temporary processes/files. Check PID, UID and start-time identity before signalling a process, and handle verified process disappearance without targeting a reused PID.
6. For VDM, remove only the exact owned association and restore original role-holder state. Do not reset monotonic allocator counters or remove someone else's association.
7. Re-read settings, helper identity, task/display state and app integrity where that was part of the test.

If task restoration fails, preserve ownership evidence and do not close the display in the hope that the platform will return the task correctly. Source-copy rollback and device restoration are separate records; neither recalls a message or undoes a payment.

## 8. Publish only the minimum necessary evidence

Use a sanitized record with a case ID, date/build, runtime identity, test surface, observed state delta, cleanup and untested boundary. Keep private receipts and unrelated account/chat material out of the repository. In the Telegram test, full temporary screenshots and unrelated notes were removed after verification; only the requested message/control/state checks were retained privately.

Run the [documentation checks](../CONTRIBUTING.md) before publishing. The tests are offline documentation checks, not a replacement for repeating a device experiment or proof of a future device build.
