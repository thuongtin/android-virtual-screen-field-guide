# Android Virtual Screen Field Guide

[Tiếng Việt](README.md) · **English** · [简体中文](README.zh-CN.md) · [한국어](README.ko.md) · [日本語](README.ja.md)

Real-device field notes on controlling Android apps on a separate virtual display while the physical screen remains off. This is a **documentation and reproducibility guide**, not an Android agent, an APK distribution, or a claim that every app works under every lock state.

**Observation date: 2026-11-16.** Versions below are the tested versions, not a promise that they are the newest releases. The published findings are author-reported, sanitized observations. Private device captures and raw logs are intentionally not included, so readers should reproduce the tests rather than treat the repository as independently auditable raw evidence.

## The short answer

- **Root is neither necessary nor sufficient.** On a rooted Samsung A32, Virtual Screen's Root backend failed a package/UID check. An ADB-started Shizuku server running as **shell UID 2000** worked.
- **Non-root can work.** On a Xiaomi Pad Mini with Android 16, Mika's own unlocked-device self-check passed **12/12**. A separate diagnostic process using the installed APK's native backend also launched, read, tapped and typed on its virtual display while the physical device remained securely locked and off.
- **Screen off is not the same as secure keyguard.** The A32 tests had no secure keyguard showing. Do not generalize them to PIN/pattern-locked Samsung devices.
- **A working backend is not a complete AI-agent test.** The Xiaomi locked tests did not invoke the serving helper's RPC and did not run a complete Mika AI task. No model or API key was configured.
- **Lifecycle recovery matters.** Wireless ADB disappeared during the session. After the user re-enabled it, the Xiaomi helper was absent and required a manual restart. Automatic recovery and post-reboot operation remain unverified.

## What was actually tested

| Device / path | Software | Observed result | Evidence boundary |
|---|---|---|---|
| Samsung A32, Android 13 / One UI 5.1, rooted | Virtual Screen 0.2.1, Root backend | `ROOT_OPERATION_FAILED`: `SecurityException: packageName must match the calling uid` | This ROM/backend combination, not all root implementations |
| Same A32, ADB-started Shizuku | Shizuku 13.6.0, Virtual Screen MCP | 19 tools listed; Settings launch, tree reading, tap and typing verified while physical display stayed `DOZE_SUSPEND` | No secure keyguard showing; not all 19 tools retested |
| Same A32, app compatibility check | Virtual Screen 0.2.1 | Initial check: 18/19, with Tap failed | Later bounded tap/type success does not erase that earlier result |
| Xiaomi Pad Mini, Android 16, non-root | Mika 0.1.44, build `2b26f3f` | Built-in self-check: 12 pass, 0 partial, 0 fail, 0 skipped in 41 seconds | Unlocked-device self-check |
| Same Xiaomi, securely locked and screen off | Installed Mika APK's `ShellService`, separate temporary shell process | Virtual display, test-page nodes, tap counter and typed-text readback passed; `Asleep`, physical `OFF`, keyguard `showing=true` | Native backend diagnostic, not serving-helper RPC or app/AI E2E |
| Same Xiaomi, securely locked | Same native capture path; TikTok Studio 44.6.3 | App launched and a real 1880×3008 frame was captured; physical display remained off | Read-only launch/capture, no posting or account interaction |

For methodology and unsuccessful attempts, see [Observed results](docs/observed-results.md). The [sanitized data](examples/observations.json) is a summary, not a raw trace.

## Choose a solution

| Situation | Practical starting point | Important limitation |
|---|---|---|
| Rooted phone, existing `su` works | Try the application's supported Root backend with an app-specific grant | Root does not bypass Android package attribution, display policy or ROM behavior |
| Root path fails, USB/authorized wireless ADB is available | Run Shizuku through **ADB**, then authorize only the target app | Verify UID 2000. Starting Shizuku with root is a different execution identity |
| Non-root Android with Mika support | Install Mika and start its documented helper using the selected device's ADB connection | Mac-to-device ADB trust is not Mika's own wireless pairing |
| No root and no ADB/helper | Consider ordinary app APIs or a user-consented MediaProjection workflow | These do not grant arbitrary cross-app input or automatically provide a private background app display |
| Sensitive/protected apps or content | Test the specific app and honor its normal authentication and capture rules | Blank or blocked protected content is not a reason to defeat those rules |

Detailed instructions: [Root / non-root solutions](docs/solutions.md) · [Troubleshooting](docs/troubleshooting.md) · [Reproduction checklist](docs/reproduce.md).

## How the pieces fit

```mermaid
flowchart LR
    A[Host controller] -->|ADB-selected device| B[App or shell helper]
    A -->|ADB-forwarded loopback MCP| C[Virtual Screen app]
    C --> D[Root or Shizuku backend]
    B --> E[Android virtual display]
    D --> E
    E --> F[Target app task]
    F --> G[Pixels and accessibility nodes]
    G --> A
    H[Physical display and keyguard] -. verify separately .-> E
```

These are **different control paths**, not interchangeable names:

1. **Virtual Screen + MCP:** app-level authorization, session, control lease, current observation, action, readback and cleanup.
2. **Mika's normal app workflow:** its own helper, accessibility service and optional model configuration.
3. **Standalone native diagnostic:** a temporary shell process instantiated `ShellService` from the installed Mika APK. This established a device/backend capability; it did not establish Mika app-level orchestration or expose a production remote-control endpoint. The version-coupled experimental harness is not shipped here as a supported SDK.

## Minimal operating rules

- Select a device by a newly verified model and serial. Every ADB command must include `-s "$SERIAL"`; never rely on the default connected device.
- Keep the service on loopback. Do not expose a bearer-authenticated device controller on a public tunnel just to obtain a screenshot.
- Read tokens only through the application's supported UI/configuration. Never put them in shell history, repository files, screenshots or logs.
- ADB shell root, an app-specific `su` grant, Shizuku permission and accessibility permission are different grants. Keep unrelated grants and services intact.
- Inspect before input. Use a current observation and the correct display. If a tap's delivery is uncertain, read the state before deciding whether another action is needed.
- Do not force-stop an app just because it already has a task on another display. A draft or other transient state may be lost. Observe the tool's approval flow.
- Check **physical-display state**, virtual-display state and keyguard separately. Device-wide `Awake` can coexist with a physical panel in `DOZE_SUSPEND` because a virtual display is active.
- Close test displays, release leases/sessions, restore any deliberately moved task/focus and verify the result. Keep successful configuration separate from disposable test cleanup.

## Reproduce, then make claims

The suggested progression is:

1. Verify the selected device and the official APK's identity/hash.
2. Establish the correct backend identity and app-specific permissions.
3. Run the app's self-check while unlocked; fix the failed prerequisite and rerun affected checks.
4. Test a harmless Settings/test-page flow on a virtual display with visible output and input readback.
5. With the user explicitly controlling the lock state, repeat bounded tests while the physical screen is off. Record whether secure keyguard is actually showing.
6. Check lifecycle failures separately: transport loss, helper death and reboot recovery are different tests.
7. Publish only sanitized results, not tokens, network identifiers, account data or private screenshots.

## Documentation

- [Observed results and boundaries](docs/observed-results.md)
- [Root and non-root solutions](docs/solutions.md)
- [Reproduction and cleanup](docs/reproduce.md)
- [Failure diagnosis](docs/troubleshooting.md)
- [Publication hygiene](docs/privacy.md)
- [Primary sources](docs/sources.md)

## License and attribution

This guide and its original examples use the [MIT license](LICENSE). Upstream applications retain their own licenses. This repository does not redistribute their APKs, source trees, credentials or private captures, and is not affiliated with their maintainers. Follow the linked official projects for installation details and version-specific changes.
