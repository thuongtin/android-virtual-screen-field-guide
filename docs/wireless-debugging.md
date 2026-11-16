# Wireless debugging: auto-off, reconnection and helper recovery

[Guide](../README.en.md) · [Observed results](observed-results.md) · [Troubleshooting](troubleshooting.md)

Research and field observations: **2026-11-16**. Community reports below are reports about their authors' devices, not fixes verified on every Xiaomi or Android version.

## Separate the failure before choosing a remedy

| Boundary | Evidence to collect | Different from |
| --- | --- | --- |
| Wireless debugging switch | `adb_wifi_enabled` actually changes to `0` | A host losing discovery or its connection |
| ADB transport | Device connection, port and mDNS discovery | A helper process exiting |
| Helper lifecycle | Exact process identity and app connection state | A helper process existing but not serving requests |
| Authorization | Client pairing/authorization validity | The wireless switch being off |
| Recovery | A functioning app-level test after recovery | A setting becoming `1` or a new PID alone |

In [AOSP Android 16's debugging manager](https://github.com/aosp-mirror/platform_frameworks_base/blob/android-16.0.0_r1/services/core/java/com/android/server/adb/AdbDebuggingManager.java#L640-L695), Wi-Fi disablement, disconnection and a BSSID change can disable wireless debugging. An inference worth testing is that roaming between mesh access points can matter even when the SSID looks unchanged. This has **not** been established as the cause of the Pad Mini incident.

## Chinese community reports

- **[V2EX, May 2024](https://global.v2ex.com/t/1042620):** the author reports wireless debugging turning off on non-root Lenovo Xiaoxin and Xiaomi Pad 5 tablets despite continuous power and Wi-Fi. Replies suggest disabling authorization expiry or using legacy TCP ADB. The original author does not confirm a successful fix. This is relevant symptom evidence, not a tested Pad Mini solution.
- **[TianTan discussion](https://bbs.tatans.cn/topic/62772):** a Xiaomi 10S user, describing the system as HyperOS “澎湃1.3”, reports needing to re-enable wireless debugging without a reboot. They try autostart, but the thread provides no follow-up establishing that it resolved the problem. The page exposes a relative date, not a verified absolute posting date.
- **[Shizuku issue #178, January 2022](https://github.com/RikkaApps/Shizuku/issues/178):** the MIUI 13 author confirms that restoring Shizuku's network permission fixes pairing. This is a pairing/network-access issue, not evidence that it prevents the wireless switch turning off.

## English community reports

- **[Tasker + Termux workflow](https://www.reddit.com/r/tasker/comments/1aupuvo/):** the author describes granting `WRITE_SECURE_SETTINGS`, pairing a local client, enabling wireless debugging, discovering its port and then using `adb tcpip 5555`. A Galaxy S24 Android 14 user reports success across reboots; other comments report failures, and the author's update addresses mDNS/check failures. This automates restoration/bootstrap rather than preventing every auto-off event. Do not import and run an automation without inspecting its permissions and commands.
- **[Shizuku issue #1426, September 2025](https://github.com/RikkaApps/Shizuku/issues/1426):** Xiaomi users discuss Shizuku stopping when the screen turns off. A [reported workaround](https://github.com/RikkaApps/Shizuku/issues/1426#issuecomment-3282783901) combines **USB debugging (Security settings)**, **Default USB configuration: No data transfer**, and restarting Shizuku. It does not isolate one toggle as the fix or establish that wireless debugging itself stays enabled. It was not tested here on Pad Mini Android 16.
- **[Android 11 Wi-Fi ADB discussion](https://stackoverflow.com/questions/65991502/adb-over-wi-fi-android-11-on-windows-how-to-keep-a-fixed-port-or-connect-aut):** users discuss reconnecting and changing ports; a suggested legacy TCP workflow lasts until a device reboot. This is not a fixed port for the modern paired TLS transport.

## Which suggestions solve which problem?

| Suggestion | Intended benefit | Boundary and evidence |
| --- | --- | --- |
| Always allow on this network | Authorize debugging on that network | Does not guarantee Wi-Fi stays connected or the switch stays on |
| Disable adb authorization timeout | Avoid automatic expiry of ADB authorization | Not a demonstrated cure for immediate switch-off after locking |
| Background/autostart/battery settings | Help the relevant app remain available | OEM-dependent; exemptions alone do not prove helper survival |
| Mika's own pairing and recovery | Let Mika reconnect/restart its helper when needed | Awake helper-only recovery passed below; locked wireless-off/reboot recovery did not undergo a test |
| Tasker automation | Re-enable or bootstrap ADB under defined conditions | Community successes and failures; not installed or tested in this experiment |
| Legacy `adb tcpip 5555` | Use a different ADB transport | Not the paired TLS wireless-debugging mode; keep it off untrusted/public networks and plan explicit shutdown; not enabled here |
| Existing root + a supported startup mechanism | Another way to start a helper without relying on app wireless pairing | Root is not required for the demonstrated Mika result and does not prove every backend works; no rooting or bootloader change was performed |

The [official Shizuku guide](https://shizuku.rikka.app/guide/setup/) groups background operation, USB mode and authorization timeout among remedies for random stopping. That is not a promise that one setting locks the wireless switch on permanently.

## Mika setup used on the non-root Pad Mini

The initial helper had been started with Mika's documented computer-start script over an existing wireless ADB connection. The Mac's pairing did **not** mean Mika had its own pairing. The recovery page explicitly warned that its options required wireless pairing first.

The subsequent configuration used the normal installed-app UI:

1. Open Mika's **Phone control → Pair again** setup.
2. Open Android **Wireless debugging → Pair device with pairing code** and complete Mika's pairing. Keep pairing codes private. Verify **Paired** and **Connected** in Mika, not just a connected Mac.
3. Verify the current Wi-Fi network is trusted. On a new network, enable wireless debugging manually and select **Always allow on this network** if that network is trusted. Do not publish the network identity or ADB keystore.
4. In **Recovery & repair**, verify **Restore after restart** and **Turn on Wireless debugging automatically**. On this tablet both were already enabled, and `WRITE_SECURE_SETTINGS` was already granted. Pairing supplied the missing prerequisite; the experiment did not newly grant those settings.
5. Keep USB debugging enabled and rerun Mika's own compatibility self-check.

Mika's [pinned setup guide](https://github.com/wangzan101/Mika/blob/2b26f3f80937a320581dab66f16e6a7fda1799ce/docs/setup-guide.en.md#after-setup) says wireless debugging need not remain enabled for day-to-day helper operation; it is needed when restarting the helper. Its [auto-on implementation](https://github.com/wangzan101/Mika/blob/2b26f3f80937a320581dab66f16e6a7fda1799ce/core/src/main/kotlin/com/wangzan101/mika/core/shell/WirelessDebuggingAutoOn.kt) bounds its attempts rather than writing the setting indefinitely.

## What the follow-up actually verified

Device/build: **Xiaomi Pad Mini, Android 16, non-root, Mika 0.1.44 / 2b26f3f**. These are author-reported sanitized results; private raw evidence is not published.

| Stage | Observation |
| --- | --- |
| Before own pairing | Mika self-check: 12 pass, 0 partial, 0 fail, 0 skipped, 42 seconds |
| After own pairing | Paired/Connected; recovery prerequisite warning gone; self-check 12/12, 41 seconds |
| Deliberate helper-only interruption | Identity-checked shell helper received SIGTERM; the tablet remained **Awake/unlocked**, and Wireless debugging remained **on** |
| Automatic recovery | Replacement helper observed approximately 5 seconds after the test began; no manual start or rescue |
| Functional readback | Mika's own self-check after recovery: 12 pass, 0 partial, 0 fail, 0 skipped, 41 seconds |

The post-recovery self-check exercises the actual serving helper through Mika, unlike the earlier standalone native diagnostic. No model was configured and no full AI task was tested.

**Still untested:** wireless debugging off while securely locked, prolonged idle, Wi-Fi roaming and reboot recovery. A combined locked/wireless-off test was prepared but not run because an independent USB recovery transport was not available. Do not extrapolate the awake helper-only pass to those boundaries or claim that the original lifecycle failure's cause is fixed.

For a deliberate failure-injection test, establish a working recovery channel first, verify exact helper identity immediately before any signal, record separate checkpoints and bound the observation window. A restored switch plus a new PID is only a candidate recovery until app-level behavior passes. Never signal a shared or unidentified process, revoke all clients' authorizations, or reboot as an incidental check.
