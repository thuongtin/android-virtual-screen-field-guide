# Contributing evidence and documentation

This is an evidence-based field guide, not the private device-controller source repository. Do not commit APKs, DEX files, raw captures, token files, local handoffs or device/account identifiers.

## Local checks

Run from the repository root with Python 3.10 or newer:

```sh
python3 -m unittest discover -s tests -v
python3 -m json.tool examples/observations.json > /dev/null
git diff --check
```

These checks do not call ADB, contact a model or operate a device. CI runs the same offline checks. External link availability is a separate review; local file and Markdown-anchor links are checked by the suite.

## Adding or changing a result

1. Establish evidence on the actual surface requested: source, build, installed runtime, app self-check, real workflow and lifecycle are different levels.
2. Add a stable, unique case ID in `examples/observations.json`. Include the observed date, versions, execution boundary, lock/power state, actual result, cleanup and `not_tested` fields where applicable.
3. Preserve historical failures. A different backend succeeding is not a correction of an earlier failure unless the same path was retested.
4. Update the dedicated device guide, `docs/observed-results.md`, `docs/acceptance-matrix.md` and all five README summaries. Deeper guides are currently in English; label links accordingly where useful.
5. Review root/runtime identity, serving-versus-standalone boundaries, state sampling and time intervals. Never call a source build or offline test a live device pass.
6. Cite upstream primary sources using a tested release or commit where available. Label moving branches and community device reports rather than treating them as platform contracts.
7. Run the checks and review the exact staged diff for private content before a public commit. User authorization to publish a technical guide is not authorization to publish private conversation contents.

## Review questions

- Did the UI/action state actually change, or did only an RPC return success?
- Was secure locking tested, or only display power-off?
- Did the app call its real serving helper, or did a separate process instantiate native code?
- Does `Seen` refer to an actual other recipient, or only an own-account/self-chat status?
- Is the stated interval active test duration, no-traffic idle, or recovery time?
- Were tasks restored before display teardown and persistent roles restored separately?
- Does a reported rollback restore source, device state, or an external action? Do not conflate them.
- Are failures and unknowns retained, including sampling versus continuous tracing?

## Public-data hygiene

Use generic labels instead of serials, private IPs, account/contact names, task/display IDs copied from an actual session or exact message bodies. Do not add live pairing links, authentication material or screenshots containing unrelated notes. Retain only sanitized state transitions in public case records. See [privacy guidance](docs/privacy.md).

CI and tests can catch patterns and contradictions, but they do not replace a human review of screenshots, prose and links. Do not weaken tests to hide missing evidence; correct the claim or collect the appropriate evidence first.
