# Observed results and evidence boundaries

> Pixel Android 17 update: see [the dedicated workflow and evidence boundaries](pixel-android17.md), including locked semantic input, parallel use, and the no-auto-wireless policy. Do not apply Xiaomi recovery settings to this Pixel workflow.

[Guide](../README.en.md) · [Sources](sources.md)

Date: **2026-11-16**. These are author-reported results from real devices. Raw screenshots, credentials, account details and identifying device/network data remain private. This document and [observations.json](../examples/observations.json) are sanitized summaries, not raw logs from which a third party can independently reproduce every assertion.

## Terminology

- **Installed:** the intended package/version/hash was checked on the selected device.
- **Runtime pass:** the requested behavior was exercised and its resulting state was read back.
- **Native diagnostic:** actual installed backend code ran in a separate diagnostic process on the actual device. This is stronger than a source-only inference, but weaker than testing the app's complete control path.
- **Not tested:** there is no supporting result. It is not a pass and not necessarily a failure.
- **Cleanup:** test displays, sessions and temporary device files were removed. This does not undo intentional configuration such as the selected working backend.

## Case A: rooted Samsung A32

### Environment

- Samsung A32, Android 13, One UI 5.1.
- Magisk 31.1 was already installed; root installation was not part of the work.
- Virtual Screen 0.2.1, arm64, versionCode 6.
- Installed APK hash matched the release's `SHA256SUMS`.
- The app already had an app-specific root grant and a loopback MCP listener. Those were not redundantly recreated.

### Root backend: failed

Both the app-level operation and a direct diagnostic invocation of the installed APK's root display entry point produced:

```text
ROOT_OPERATION_FAILED
SecurityException: packageName must match the calling uid
```

Shell `su` still returned UID 0. This established a failure in this backend/ROM interaction, not a lack of root and not proof that every Root backend fails.

### ADB-started Shizuku: worked for the bounded flow

Shizuku 13.6.0 was started by the official ADB command shown in its app. Its server ran as **shell UID 2000**, not root. Virtual Screen was authorized in Shizuku and its selected backend was changed.

Verified separately:

- MCP remained on `127.0.0.1:8732`.
- An unauthenticated request returned HTTP 401.
- Authenticated initialization and `tools/list` returned 19 tools.
- A virtual display hosted Android Settings, with readable accessibility nodes.
- The physical display's top task was unchanged in the bounded Settings test.
- A later screen-off run opened Search, injected `display`, read that exact text back and cleared it afterward.
- Physical panel state stayed `DOZE_SUSPEND`; the virtual display was `ON`.
- After cleanup, physical wakefulness returned to `Dozing`; test display and control session were closed.
- Existing root-policy entries were preserved; no unrelated app received a new root grant. The private comparison data is not published.

### Keep the initial self-check failure

The initial app compatibility check reported **18/19**, with Tap failed. The later narrowly scoped tap/type test succeeded. These are different observations. The latter is not a rerun proving all 19 checks pass.

### Screen-off is not secure-lock evidence

The Samsung reported `keyguard showing=false`; its lock was already disabled. The experiment did not enable a lock or enter a PIN/pattern. Its success says nothing definitive about a securely locked A32.

### Facebook task reuse and capture

Facebook already had a task on the physical display. The MCP launch path waited for restart confirmation; no confirmation or force-stop was performed. A direct task relocation diagnostic moved the identified existing task to the helper-owned display, captured a frame, then restored its original display and the prior launcher focus.

Calling `launch_app` again after relocation produced `DISPLAY_LAUNCH_REJECTED`; capturing the already-relocated task without that redundant call worked. This was a mixed **ADB task-management + MCP capture** flow, not pure MCP app launch. The raw private screenshot is not included.

A later UI action was stopped because its expected button/dialog was no longer present. No click was claimed from an old screenshot. This illustrates why every mutation requires a fresh observation and a verified current target.

## Case B: non-root Xiaomi Pad Mini

### Environment and setup

- Model 25079RPDCG, Android 16 / SDK 36, arm64.
- Mika 0.1.44, versionCode 45, build `2b26f3f`.
- Official release digest and installed APK hash matched.
- Documented `usb-start.sh` ran through an existing authorized wireless ADB connection.
- The normal Mika helper ran as shell. No root grant, bootloader change or device reboot was used.
- Accessibility was bound; unrelated services were retained.
- HyperOS battery mode was unrestricted, notifications were allowed, background autostart enabled, and Mika locked in Recent apps.
- Current Wi-Fi trust for ADB was verified privately; network identifiers and keys were not retained in the public package.
- No model provider or API key was configured.

### Built-in self-check while unlocked

First run: **11 pass, 1 partial, 0 fail, 0 skipped**. The partial item was notifications being blocked.

After notifications were allowed, the app's own report stated:

```text
Result: 12 pass, 0 partial, 0 fail, 0 skipped in 41 s
```

| Check | Reported result |
|---|---|
| Device | Android 16, arm64, wireless debugging available |
| Permissions | Accessibility bound, notifications allowed, battery unrestricted |
| Helper | Running as shell, computer/USB startup mode |
| Virtual display | 1880×3008, own focus yes |
| App launch | Mika test page and Settings on Mika's display |
| Screen reading | Expected test-page elements found; frame not blank |
| Actions | Tap, ASCII, Chinese text, scroll and Back passed |
| Stays alive | Tree and frames changed for 15 seconds |
| Main screen | Top task unchanged |
| Browser | Local page read and button result verified |
| Sandbox | Echo and Python processes exited 0 |
| App copies | At least one usable secondary profile |

This was an **unlocked** self-check. It did not test a configured model or a full AI task.

### Secure-lock native diagnostic

After the user locked the tablet, physical state was `Asleep`, panel `OFF`, keyguard `showing=true`. A read-only follow-up also confirmed `secure=true` on the Xiaomi; the Samsung reported `secure=false`.

A separate shell process loaded the **installed Mika APK** and instantiated its `ShellService`. It created its own virtual display and launched the app's self-check target activity. A temporary UiAutomation connection preserved the existing accessibility services.

The diagnostic verified:

1. A virtual display was created.
2. Test-page nodes were readable.
3. A tap changed the actual counter to `Taps: 1`.
4. Injected text was read back exactly.
5. Physical wakefulness and keyguard remained `Asleep` and `showing=true`.
6. Its display was released, the temporary process exited and the normal Mika accessibility service remained bound.

An early harness initialization used the wrong thread and failed. Another initial observation read a stale counter. The harness was corrected to initialize on the main Looper, wait for layout settling and refresh accessibility nodes. No app protection, test assertion or keyguard policy was disabled to obtain the final result.

**Boundary:** this ran real native code on real hardware, but did not call the serving helper's RPC, rerun the app's self-check under lock or run an AI task through Mika. No unlock method was called.

### TikTok Studio launch and capture while locked

Using the same standalone native-code approach, TikTok Studio 44.6.3 was launched on a virtual display and a real **1880×3008 PNG** was obtained from its ImageReader surface. The top task's package was checked before saving the frame.

The image was visually inspected and showed the actual app UI, not the lock screen, a mock or a cached APK image. There were no injected app inputs, uploads, posts or account changes. Physical state remained `Asleep / OFF / showing=true`. After cleanup only the physical display remained; the serving helper was still alive.

The private image is not published, and this single app result does not establish support for protected-content capture or every app.

### Initial lifecycle failure: cause remains unresolved

Wireless ADB disappeared while the tablet was locked. After the user re-enabled wireless debugging, no Mika helper process was found. The documented startup script restored it while the device remained locked.

The timing does **not** establish that locking alone killed the helper or identify the exact cause. It does establish that the helper was absent at the later checkpoint and that this run needed manual recovery. No reboot was performed. Automatic recovery was not verified in that initial computer-started session. The follow-up below tests a different, narrower boundary after Mika gained its own pairing.

### Follow-up: own pairing and awake helper-only recovery

Mika was subsequently paired through its own setup UI, which reported **Paired** and **Connected**. The current Wi-Fi trust, `WRITE_SECURE_SETTINGS` grant and both recovery toggles already existed. Own pairing supplied the missing prerequisite, and the computer-start-only warning disappeared.

With the tablet **Awake/unlocked** and Wireless debugging **on**, a bounded test terminated only the identity-checked shell helper. A replacement helper was observed approximately **5 seconds** after the test began, with no manual startup or rescue. Mika's own post-recovery self-check passed **12/12 in 41 seconds**, exercising the actual serving helper rather than the earlier standalone native diagnostic. Baseline and immediate post-pairing self-checks also passed 12/12, in 42 and 41 seconds respectively.

This does not resolve the earlier incident's cause or verify automatic recovery with wireless debugging off, while securely locked, after long idle/roaming or after reboot. The combined locked/wireless-off test was not run. See [the wireless-debugging guide and community reports](wireless-debugging.md).

## Claims this guide deliberately does not make

- All root devices or all non-root devices support this workflow.
- ADB being connected means the app has its own wireless pairing.
- A native helper test proves app-level/AI end-to-end operation.
- Secure-lock operation was verified on Samsung.
- Every MCP tool passed because tool discovery returned 19 names.
- A screenshot proves a save/upload/post was accepted by a server.
- A code-copy rollback restores a phone's configuration or account state.
- Private raw evidence is publicly available for independent audit.
