# Acceptance matrix: what each result actually proves

Updated **2026-11-17**. This table is a device/build-specific index, not a universal compatibility list. The machine-readable records are in [observations.json](../examples/observations.json); historical failures remain there even when a different path later succeeds.

## Results by execution boundary

| Device and path | Identity / control surface | Lock condition tested | Actual result | Evidence boundary not crossed |
| --- | --- | --- | --- | --- |
| A32 stock Root backend | Root-selected VirtualScreen 0.2.1 | Original setup | **FAIL:** package/UID attribution exception | Root availability is not app-backend compatibility |
| A32 stock Shizuku | ADB shell UID 2000, serving MCP | Panel off, no secure keyguard | Settings observation, tap and type pass; first self-check 18/19 retained | Secure PIN/pattern and general parallel-use not proven |
| A32 separate root-hosted controller | Root bootstrap, runtime UID 1000 | Panel off; secure=false | Coordinate/semantic input, Unicode, 90-second helper idle and owned-worker timeout cleanup pass | Not stock Root-backend repair or secure-lock proof |
| Pad older native probe | Non-root shell UID 2000, separate native diagnostic | Physical OFF, secure keyguard | Probe tap/type/readback and separate TikTok Studio capture pass | Not serving-helper RPC or AI E2E |
| Pad locked app self-check | Mika 0.1.44 app UI calls its existing serving Binder; separate host only holds the UI | Physical OFF, locked and secure at sampled checkpoints | **12/12 in 42 seconds**; input, screen reading, local browser, sandbox and own-focus checks pass | Not model/provider E2E, overnight idle or continuous focus trace |
| Pad Telegram Saved Messages | Non-root standalone host using installed Mika native code, plus UI automation | Physical OFF, locked and secure at sampled checkpoints | One explicitly authorized self-message, exact draft readback, sent-item state and cleared editor | Not Mika serving-RPC for Telegram, a model task, or proof of another recipient reading |
| Pixel older power-override route | VirtualScreen + shell Shizuku, serving MCP | Physical OFF, secure lock | Semantic click/set-text pass; coordinate tap **FAIL despite accepted RPC** | Pixels/nodes available do not establish interactive coordinate input |
| Pixel parallel WhatsApp | Serving MCP plus explicit task relocation | User actively using the unlocked physical device | Bounded read/compose/send and return-to-background pass | Not locked WhatsApp or two actors controlling the same task |
| Pixel VirtualDevice route | Non-root shell UID 2000, custom CDM/VDM controller | Cold create during secure lock; physical OFF | Coordinate tap, native swipe, Unicode, Calculator preview and **308.7-second** no-helper-traffic idle followed by input pass | Not stock-MCP integration, arbitrary apps, reboot or overnight recovery |

Details: [A32 root](a32-root-android13.md), [Pad Android 16](xiaomi-pad-mini-android16.md), [Pixel Android 17](pixel-android17.md), [wireless recovery](wireless-debugging.md).

## Four different clocks

Do not combine these into an uptime claim:

- **42 seconds:** the total duration reported by the locked Pad app self-check.
- **15 seconds:** the changing-frame/tree observation inside that self-check, with active checks, not a no-traffic idle.
- **90 seconds:** the separate A32 root-hosted helper idle check.
- **308.7 seconds:** the Pixel custom-controller interval without helper calls, followed by verified input. Physical state was sampled, not continuously recorded.

The earlier Pixel idle attempt that encountered physical ON with global interactive false was rejected by the guard and was not counted as a pass. Xiaomi's separate roughly five-second helper recovery was tested awake, with wireless debugging still enabled; it is not a fifth long-idle result.

## Lock state is not a single boolean

Record physical display state, virtual display state, power/display group, global interactivity, keyguard visibility and whether a secure credential is configured separately. `deviceSecure=true` alone does not show that a device is currently locked. `OFF` alone does not show that it has a secure keyguard. A cached image is not evidence that the display can still process input.

These sessions did not test operation before the first unlock after a reboot. Android distinguishes Direct Boot storage availability from a later screen lock: credential-encrypted storage becomes available after user unlock and normally remains available through subsequent screen locking until restart. Do not present these results as a PIN bypass or a Direct Boot guarantee. [Android Direct Boot contract](https://developer.android.com/privacy-and-security/direct-boot).

## Proof levels

1. **Source evidence:** a method, flag, guard or role exists in pinned source.
2. **Local test:** syntax, build, parser or cleanup logic passes offline tests.
3. **Installed runtime:** the intended app/helper is running with a verified identity.
4. **Operation:** the desired state changes after a scoped action; observation is fresh.
5. **User workflow:** the requested app action completes at the actual destination.
6. **Lifecycle:** task state, owned resources and configuration are restored or deliberately retained as requested.

Each level is separate. The Telegram result reaches a bounded user workflow without proving model autonomy. A source-copy rollback reaches a local test boundary without undoing a sent message. The repository's documentation tests are not device tests and do not contact a phone.

## Required evidence for a new case

- Date, tested family/build/API and versions; root bootstrap and actual runtime UID separately.
- Execution path: app serving RPC, native standalone host, semantic action, coordinate injection or model/provider workflow.
- Initial task/display ownership and the owner's requested action; exact device/profile selection kept privately.
- Lock/power observations before and after input, with sampling limitations stated.
- Expected and observed state delta. For messaging: destination, exact draft, one send attempt and resulting UI state, without publishing conversation contents.
- Resource/role/task cleanup and any failed attempt, uncertainty or recovery step.
- An explicit `not_tested` list, plus a stable case ID in the public JSON record.
