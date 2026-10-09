# Security

Do not publish API keys, platform passwords, cookies, private customer material, operating databases, machine identifiers or signing credentials in issues or pull requests.

The community edition has no commercial activation requirement. It preserves the independent Electron-generated local API token, sandbox/context isolation, external-site allowlist and safeStorage integration. The community application uses a separate user-data namespace from the original commercial edition.

The local backend is designed for loopback use. Development without Electron may run without a local token; it is not a production multi-user service and must not be exposed directly to the internet. AI generation sends the provided prompt to the configured supported service. Provider charges and data handling apply.

Platform login and final publication remain manual actions on official creator sites. This project does not collect platform login credentials or claim unattended posting support.

For a security issue, describe the affected version and behavior without attaching secrets or private data. Do not post a working credential in a public issue.
