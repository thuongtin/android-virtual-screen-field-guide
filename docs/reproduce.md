# Reproduce in small, reversible stages

[Guide](../README.en.md) · [Solutions](solutions.md) · [Failure diagnosis](troubleshooting.md)

Use a device and account you are authorized to control. This checklist is deliberately staged: do not replace a failed runtime test with a source-code observation or a successful install.

## 1. Inventory without changing the device

Select a live serial from `adb devices -l` and verify the model. Wireless mDNS names and addresses can change. Examples use placeholders; do not paste `SERIAL` literally.

```sh
adb devices -l
SERIAL='SERIAL'
adb -s "$SERIAL" shell getprop ro.product.model
adb -s "$SERIAL" shell getprop ro.build.version.release
adb -s "$SERIAL" shell getprop ro.build.version.sdk
adb -s "$SERIAL" shell getprop ro.product.cpu.abi
```

Stop if the selected model does not match your intended device. Do not fall back to an old IP or an unscoped ADB command. If it is locked, preserve that state; do not enter a credential, dismiss the keyguard or change lock settings for a test unless the device owner separately chooses to do so.

Record version/build, physical display state, keyguard state and the exact backend. Inspect these read-only outputs locally; OEM output formats differ and may contain private data:

```sh
adb -s "$SERIAL" shell dumpsys power
adb -s "$SERIAL" shell dumpsys display
adb -s "$SERIAL" shell dumpsys window policy
```

Do not publish the raw dumps. In particular, do not publish ADB key stores, app private directories or a root-manager database. [Publication hygiene](privacy.md).

## 2. Install only the official, matching build

Use the release links in [sources.md](sources.md). Verify the APK package, ABI, version and checksum before installing. These are local examples; paths are placeholders:

```sh
shasum -a 256 APP.apk
aapt dump badging APP.apk
adb -s "$SERIAL" install -r APP.apk
```

Installation is not runtime acceptance. Do not downgrade or replace an existing application's data without first understanding the effect. Preserve device/app state and unrelated work.

## 3. Choose and verify the privilege path

### Already-rooted device

A read-only `su -c id` can verify shell access to root on a device whose owner already enabled it. It does not establish that the target app has a root grant. Use the root manager's normal app-specific permission UI; do not grant every app, overwrite policy tables or publish their contents.

Try the app's supported Root backend. If it fails, record the exact error. The A32 UID/package failure was resolved for the bounded test by choosing **ADB-started Shizuku**, not by broadening root grants.

### Shizuku through ADB

Install Shizuku from the official source. Use the **ADB/computer or wireless-debugging startup route** shown by the installed version. Read its displayed command rather than hard-coding a version-specific native-library path. Run it only against `"$SERIAL"` and confirm the resulting server identity is shell.

Authorize only the intended application in Shizuku, choose that backend inside the app, and check accessibility is connected if its node-reading/input features need it. Do not overwrite other accessibility services.

### Mika helper without root

After Mika is installed and has generated its documented script, verify the file exists and run it over an already-authorized ADB connection:

```sh
adb -s "$SERIAL" shell ls -l /sdcard/Android/data/com.wangzan101.mika/files/usb-start.sh
adb -s "$SERIAL" shell sh /sdcard/Android/data/com.wangzan101.mika/files/usb-start.sh
```

Do not print or commit the script contents; generated launch material can contain private handoff data. Read back helper status in Mika and confirm a shell-owned helper process. This works over a wireless ADB transport too, but the app still describes it as computer/USB startup. It does not create Mika's own wireless pairing.

Configure the relevant OEM background settings through their normal UI: battery restrictions, notifications, autostart and Recent-app retention. Record each setting actually checked rather than assuming an exemption guarantees survival.

## 4. Check while unlocked first

Run the application's compatibility/self-check. On Mika, use its Recovery & repair / Compatibility self-check page, keep it visible and allow the test to finish. Do not simultaneously run a second UI test on the same device.

The self-check does not require a model key. Verify all required categories and keep the report. A partial prerequisite should be fixed and the test rerun; do not delete a failed category to obtain a pass.

## 5. Virtual Screen MCP lifecycle

Keep authentication enabled and the server loopback-only. Forward a free host port to the app's port on the selected device:

```sh
adb -s "$SERIAL" forward --no-rebind tcp:8732 tcp:8732
```

Check existing forwards first. `--no-rebind` also closes the race: it rejects a port already bound by another forward instead of replacing it. If the command fails, stop and choose a different free host port, or use `tcp:0` and record the allocated port returned by ADB. Use that exact port consistently and remove only the forward your test created. Do not remove another session's forward.

Use a client that reads a token through supported configuration without logging it. Follow the [pinned MCP protocol](https://github.com/lejw0925/android-virtual-screen/blob/v0.2.1/docs/MCP.md), rather than copying private session headers:

1. `initialize` with a supported protocol version; retain the returned MCP session ID.
2. Send `notifications/initialized`.
3. Send `tools/list` and use the returned schemas. Every tool requires a clear `purpose`.
4. `acquire_control`; retain the returned control lease privately.
5. `create_screen`; retain the actual returned display ID. For screen-off tests, consult `allow_screen_off` in that build's schema.
6. Resolve and launch the intended app component, then `observe` the actual virtual display.
7. Use a current `observation_id` and lease for input; observe again afterward to verify the result.
8. `close_screen`, `release_control`, then `DELETE` the MCP session.

Use a unique JSON-RPC request ID for each request. Reusing an ID can produce `DUPLICATE_REQUEST_OR_SESSION_LIMIT`; this is not evidence that device input failed or should be replayed.

If the app is already running on another display, observe the application's restart-confirmation flow. Do not auto-accept a destructive restart, force-stop the app or disable its guard. A task-relocation diagnostic can sometimes preserve the existing task without restarting it, but needs device-specific inventory, agreement and restoration. It is not a generic substitute for the tool's policy.

## 6. Verify actual behavior, not just return codes

Start with Settings or the application's test page, not a messaging, payment or publishing screen.

- Confirm the app's task is on the intended virtual display.
- Confirm nodes are readable and/or frames are nonblank and current.
- Tap a harmless test button and verify its counter or resulting state.
- Type a disposable string and read back the exact value; clear it afterward.
- Verify main-display focus/task and physical power state before and after.
- If node bounds or text appear stale, re-observe and refresh before another input. A successful injection return code is not the same as a verified UI action.

Do not replay uncertain mutations. A missing old button is a reason to inspect the new UI, not to tap its previous coordinates.

## 7. Test screen off and secure lock separately

Ask the owner to establish the intended lock state. Record both physical display state and keyguard state. Never infer secure locking from a black image or `Asleep` alone.

A physical panel can stay off while the virtual display is on. Device-wide wakefulness can be misleading; identify the **internal physical display** and the test's virtual display individually.

If the application requires foreground UI to start a self-check, that UI constraint does not justify dismissing keyguard. A separate native diagnostic is a different evidence category and must be labeled accordingly. This guide does not ship its experimental version-coupled harness as a general remote-control product.

## 8. Exercise lifecycle only as an explicit separate test

Transport loss, app process death, helper death, idle display composition and reboot are different failures. Do not turn off debugging, disconnect the network, kill shared processes or reboot merely to complete this checklist during another ongoing task.

When authorized to test recovery, record the triggering event, transport state, helper PID/identity, app connection state and actual recovered behavior. Do not conflate a successful reconnect with a functioning input/capture session.

## 9. Cleanup and restoration

- Close only test-created displays and release their sessions/leases.
- Restore only tasks/focus changed by the experiment and verify the readback.
- Remove only test-created device files and any host forward owned by this test.
- Leave unrelated apps, data, accessibility services, root grants and devices untouched.
- Verify physical-display/keyguard state remains as intended.
- Keep screenshots private unless their content is separately approved for publication.

A source-file rollback tested on a disposable copy proves that file can be restored. It does not restore device settings, account mutations or service configuration. Document those operations separately instead of presenting one rollback as proof of all of them.
