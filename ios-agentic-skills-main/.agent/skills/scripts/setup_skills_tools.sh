#!/usr/bin/env bash
set -euo pipefail

echo "Checking required tools for .agent/skills..."

missing=()

if ! command -v rg >/dev/null 2>&1; then
  missing+=("ripgrep (rg)")
fi

if ! command -v python3 >/dev/null 2>&1; then
  missing+=("python3")
fi

if ! command -v xcodebuild >/dev/null 2>&1; then
  missing+=("Xcode Command Line Tools (xcodebuild)")
fi

if [ ${#missing[@]} -eq 0 ]; then
  echo "✅ All required tools are installed."
  exit 0
fi

echo "⚠️ Missing tools:"
for tool in "${missing[@]}"; do
  echo "  - $tool"
done

echo ""
echo "Install suggestions (macOS):"
echo "- ripgrep: brew install ripgrep"
echo "- python3: brew install python"
echo "- Xcode CLI tools: xcode-select --install"

echo ""
echo "Note: Xcode GUI tools (Accessibility Inspector, Instruments) are installed with Xcode."