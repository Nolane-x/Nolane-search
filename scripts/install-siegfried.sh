#!/usr/bin/env bash
set -euo pipefail

: "\${RUNNER_TEMP:?RUNNER_TEMP must be set by GitHub Actions}"

VERSION="1.11.9"
BASE="https://github.com/richardlehane/siegfried/releases/download/v\${VERSION}"
WORK="$RUNNER_TEMP/nolane-siegfried-\${VERSION}"
BIN_ZIP="$WORK/siegfried-linux64-static.zip"
DATA_ZIP="$WORK/siegfried-data.zip"
BIN_DIR="$WORK/bin"
HOME_DIR="$WORK/home"

mkdir -p "$WORK" "$BIN_DIR" "$HOME_DIR"

curl -fsSL --retry 3 --connect-timeout 20 --max-time 180 \
  "$BASE/siegfried_1-11-9_linux64_static.zip" -o "$BIN_ZIP"
printf '%s  %s\n' \
  'c8cb3ec3c536863bd477cea7cd1b1213843b4bcad7e9d64bcea4d131e2bb9a01' "$BIN_ZIP" \
  | sha256sum --check --status

curl -fsSL --retry 3 --connect-timeout 20 --max-time 180 \
  "$BASE/data_1-11-9.zip" -o "$DATA_ZIP"
printf '%s  %s\n' \
  '1a284a57d102996ab99e393dc40e7e213039ab44e1573c55fa9d9935840515cf' "$DATA_ZIP" \
  | sha256sum --check --status

unzip -q "$BIN_ZIP" -d "$BIN_DIR"
unzip -q "$DATA_ZIP" -d "$HOME_DIR"

SF_BIN="$(find "$BIN_DIR" -type f -name sf -print -quit)"
SF_SIG="$(find "$HOME_DIR" -type f -name default.sig -print -quit)"
test -n "$SF_BIN"
test -n "$SF_SIG"
chmod 0755 "$SF_BIN"

"$SF_BIN" -sig "$SF_SIG" -version | grep -F "siegfried \${VERSION}" >/dev/null

{
  printf 'NOLANE_SIEGFRIED_BINARY=%s\n' "$SF_BIN"
  printf 'NOLANE_SIEGFRIED_SIG=%s\n' "$SF_SIG"
} >> "$GITHUB_ENV"

echo "Installed pinned Siegfried \${VERSION} and PRONOM signature database after SHA-256 verification."
