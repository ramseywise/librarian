#!/usr/bin/env bash
# Prepare a Debian/Ubuntu machine (a GitHub ubuntu runner, or a docker image) to render slide PNGs
# with LibreOffice, the Linux stand-in for macOS Quick Look. Run once per runner, as root or with sudo.
#
#   scripts/render-slides-linux.sh            # install packages + font aliases
#   make slides PILLAR=<course>/<module> PREVIEW=1     # then auto-picks LibreOffice (no qlmanage)
#   SLIDES_RENDERER=libreoffice ...                    # or force it; --renderer libreoffice on build_deck
#
# Validated 2026-11-08 on Ubuntu 24.04 against four decks (see the report in the PR): mean SSIM vs Quick
# Look 0.73-0.79, no missing images, no overflow. The deck theme names two fonts that do not exist on
# Linux: "Helvetica Neue" (body) and "Menlo" (code). Without an alias both fall back to Noto Sans, which
# is proportional, so code blocks lose their monospace look. The alias below maps them to Liberation Sans
# (Arial/Helvetica metrics) and DejaVu Sans Mono (Menlo is derived from it).
set -euo pipefail

SUDO=""
[ "$(id -u)" -eq 0 ] || SUDO="sudo"

$SUDO apt-get update
$SUDO env DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
    libreoffice-impress poppler-utils fontconfig \
    fonts-liberation fonts-dejavu fonts-noto-core fonts-noto-color-emoji fonts-noto-cjk

$SUDO mkdir -p /etc/fonts/conf.d
$SUDO tee /etc/fonts/conf.d/99-slides.conf >/dev/null <<'XML'
<?xml version="1.0"?>
<!DOCTYPE fontconfig SYSTEM "fonts.dtd">
<fontconfig>
  <alias binding="same"><family>Helvetica Neue</family><prefer><family>Liberation Sans</family></prefer></alias>
  <alias binding="same"><family>Menlo</family><prefer><family>DejaVu Sans Mono</family></prefer></alias>
</fontconfig>
XML
$SUDO fc-cache -f

echo "helvetica neue -> $(fc-match 'Helvetica Neue')"
echo "menlo          -> $(fc-match Menlo)"
