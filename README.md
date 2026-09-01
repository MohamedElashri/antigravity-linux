# Antigravity Linux Packaging

This repository automatically builds and publishes `.deb` and `.rpm` packages for both **Antigravity** (Agentic version) and **Antigravity IDE** on Linux.

## How It Works

- A scheduled GitHub Action workflow runs periodically to discover new version releases via the official release APIs.
- If a new version is detected, it downloads the official Linux tarballs and uses `nfpm` to generate `.deb` and `.rpm` packages for both `x64` and `arm64` architectures.
- The built packages are automatically published as GitHub Releases in this repository.

## Installation

Go to the **Releases** page of this repository to download the latest `.deb` or `.rpm` files for your system.

For Debian/Ubuntu-based systems:
```bash
sudo apt install ./antigravity_<version>_<arch>.deb
```

For Fedora/RHEL-based systems:
```bash
sudo dnf install ./antigravity-<version>.<arch>.rpm
```

## Disclaimer

This is an unofficial community packaging. All software and trademarks belong to Google LLC. This repository only rewraps the unmodified official Linux builds for convenient package manager installation.
