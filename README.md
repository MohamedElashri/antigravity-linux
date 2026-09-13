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

## Automatic Debian/Ubuntu updates

The updater installs packages from this repository's **unofficial GitHub Releases**, with systemd timers for automatic updates. It supports `antigravity` (default) and `antigravity-ide`, on `amd64` and `arm64`.

It scans published, non-prerelease releases for the requested product, chooses the highest Debian version with both a package and checksum asset, verifies SHA-256 and package metadata, and refuses equal-version installs or downgrades. Checksums detect corruption; they are supplied by the same repository and are not independent signatures. Enabling automatic installation means trusting this repository's release packages and their maintainer scripts.

From a checkout of this repository, install the updater and timer definitions:

```bash
sudo apt-get install curl jq ca-certificates
sudo install -m 0755 scripts/update-antigravity /usr/local/sbin/update-antigravity
sudo install -m 0644 systemd/antigravity-update@.service systemd/antigravity-update@.timer /etc/systemd/system/
```

Check a release without installing (downloads the package to verify its metadata and checksum):

```bash
update-antigravity --check
# Or select the separate IDE package:
update-antigravity --check antigravity-ide
```

Install/update now, then enable weekly updates:

```bash
sudo update-antigravity
sudo systemctl daemon-reload
sudo systemctl enable --now antigravity-update@antigravity.timer
```

For the IDE, use `sudo update-antigravity antigravity-ide` and enable `antigravity-update@antigravity-ide.timer`. Both timers can be enabled. The updater can also perform a first installation.

These are **system timers**, running as root so unattended apt installs need no interactive sudo prompt. Missed runs are caught up after boot, with up to one hour of randomized delay. Concurrent updater runs are skipped. Failures are logged and retried on the next scheduled run; you can also start the service manually:

```bash
systemctl list-timers 'antigravity-update@*'
journalctl -u antigravity-update@antigravity.service
sudo systemctl start antigravity-update@antigravity.service
```

Restart Antigravity after an update. The updater does not back up user profiles; keep your normal backups of settings and workspaces. GitHub API or download failures leave the installed package untouched. Dependency or installation failures are reported by apt and the service exits unsuccessfully.

Disable automatic updates with:

```bash
sudo systemctl disable --now antigravity-update@antigravity.timer
# If enabled:
sudo systemctl disable --now antigravity-update@antigravity-ide.timer
```

Updating the local updater script or service definitions requires repeating the installation commands above and running `sudo systemctl daemon-reload`.
