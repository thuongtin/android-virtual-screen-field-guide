# Public-guide publication hygiene

[Guide](../README.en.md)

The original experiments used private devices and accounts. Public documentation describes techniques and outcomes; it is not permission to publish the devices' contents.

## Included

- Device families, Android/OEM versions and non-unique product model names.
- Public package names, tested application versions and primary-source links.
- Sanitized pass/fail summaries and explicit limitations.
- Placeholder-based commands and conceptual diagrams.

## Excluded

- Actual ADB serials, mDNS identities, IP addresses, SSIDs/BSSIDs and network trust stores.
- Bearer tokens, MCP session/lease identifiers, pairing codes, API keys and generated helper handoff material.
- Root-manager databases, app private data, saved sessions and credential extraction recipes.
- Raw screenshots, account names, avatars, private feed content, messages and contact lists.
- APKs, dex/classes, screen recordings, device dumps and raw log archives.
- Personal local filesystem paths or private environment configuration.

Screenshots in a private support session are not automatically approved for public distribution. This repository intentionally contains **no real-device screenshots**. When creating your own report, use a synthetic test page or obtain separate publication approval for the specific content.

## Before a commit

1. Review the exact file list and staged diff, not only `.gitignore`.
2. Search text for credentials, personal identifiers, absolute private paths and accidental logs.
3. Ensure examples use placeholders and source citations point to public upstream material.
4. Confirm result tables preserve failed and untested cases.
5. Check that a code-copy rollback or native diagnostic is not being labeled as device rollback or app/AI E2E.

Ignore rules are a convenience, not a secret scanner or an access-control boundary. If you discover an actual credential in history, handle it as a credential incident rather than merely adding an ignore pattern.

## Saved Messages and self-check publication

A self-chat is still private. It may contain passwords, pairing links, account identifiers or other notes unrelated to a test. For the Telegram case, retain only the requested test-message state, destination control, empty-composer check and lock/task restoration summary. Temporary full captures and unrelated node text were removed after verification. Do not publish the actual message body, existing notes, chat lists, screenshots, deep links or access codes to prove a generic input capability.

The public case records use a generic test-message description. The observed `Sent`/`Seen` label is described as Telegram's self-chat UI state, not a remote person's acknowledgement. Draft preparation is not permission to send; an explicit send request covers that one verified action, not other chats or retries of uncertain delivery.

Use per-run private directories with restrictive permissions for raw captures and receipts. Minimize retained evidence after checking the result. Keep identifiers, serials, paths and authentication material out of public fixtures, commit messages, review text and screenshots. Runtime receipts needed for recovery stay private; public documentation receives only redacted state transitions.
