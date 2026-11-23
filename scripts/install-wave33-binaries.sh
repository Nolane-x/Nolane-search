#!/usr/bin/env bash
set -euo pipefail

: "$RUNNER_TEMP"
: "$GITHUB_PATH"
: "$NOLANE_WAVE33_TOOL_IDS"

TOOL_IDS="$NOLANE_WAVE33_TOOL_IDS"
WORK="$RUNNER_TEMP/nolane-wave33"
BIN="$WORK/bin"
mkdir -p "$BIN"

contains_tool() {
  [[ " $TOOL_IDS " == *" $1 "* ]]
}

install_opa() {
  local file="$WORK/opa_linux_amd64_static"
  curl -fsSL --retry 3 --connect-timeout 20 --max-time 240 \
    "https://github.com/open-policy-agent/opa/releases/download/v1.22.4/opa_linux_amd64_static" \
    -o "$file"
  printf '%s  %s\n' '35e3b352e715e80624ead6c89930d8585f6f7d94cdc409eb2a9fe36620dcccba' "$file" | sha256sum --check --status
  chmod 0755 "$file"
  mv "$file" "$BIN/opa"
  "$BIN/opa" version | grep -F "Version: 1.22.4" >/dev/null
}

install_kubeconform() {
  local archive="$WORK/kubeconform-linux-amd64.tar.gz"
  curl -fsSL --retry 3 --connect-timeout 20 --max-time 180 \
    "https://github.com/yannh/kubeconform/releases/download/v0.8.0/kubeconform-linux-amd64.tar.gz" \
    -o "$archive"
  printf '%s  %s\n' '9bc2bffbf71f261128533edaf912153948b7ff238f9a531ae6d34466ec287883' "$archive" | sha256sum --check --status
  mkdir -p "$WORK/kubeconform"
  tar -xzf "$archive" -C "$WORK/kubeconform" kubeconform
  chmod 0755 "$WORK/kubeconform/kubeconform"
  mv "$WORK/kubeconform/kubeconform" "$BIN/kubeconform"
  "$BIN/kubeconform" -v | grep -F "v0.8.0" >/dev/null
}

install_cosign() {
  local file="$WORK/cosign-linux-amd64"
  curl -fsSL --retry 3 --connect-timeout 20 --max-time 300 \
    "https://github.com/sigstore/cosign/releases/download/v3.1.4/cosign-linux-amd64" \
    -o "$file"
  printf '%s  %s\n' '424e2c97d0b45fd7a6b608a87f090f35633f4c23ece5f092d48bba11aaf4bbfa' "$file" | sha256sum --check --status
  chmod 0755 "$file"
  mv "$file" "$BIN/cosign"
  "$BIN/cosign" version | grep -F "3.1.4" >/dev/null
}

if contains_tool "rego-policy-check"; then
  install_opa
fi
if contains_tool "k8s-schema-validate"; then
  install_kubeconform
fi
if contains_tool "cosign-verify-blob"; then
  install_cosign
fi

printf '%s\n' "$BIN" >> "$GITHUB_PATH"
echo "Installed only the pinned Wave 33 command-line tools selected by this job."
