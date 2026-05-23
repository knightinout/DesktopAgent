#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PKG_NAME="desktop-agent"
REVISION="${REVISION:-1}"
ARCH="${ARCH:-all}"
OUTPUT_DIR="${OUTPUT_DIR:-$ROOT_DIR/dist}"
BUILD_ROOT="${BUILD_ROOT:-$ROOT_DIR/build/deb}"

VERSION="${VERSION:-}"
if [ -z "$VERSION" ]; then
  VERSION="$(ROOT_DIR="$ROOT_DIR" python3 - <<'PY'
import os
import pathlib
import re

root = pathlib.Path(os.environ["ROOT_DIR"])
setup_path = root / "setup.py"
version = "1.0.0"
if setup_path.exists():
    text = setup_path.read_text(encoding="utf-8")
    match = re.search(r'version\s*=\s*"([^"]+)"', text)
    if match:
        version = match.group(1)
print(version)
PY
  )"
fi

STAGING_DIR="${BUILD_ROOT}/${PKG_NAME}_${VERSION}-${REVISION}_${ARCH}"
OUTPUT_FILE="${OUTPUT_DIR}/${PKG_NAME}_${VERSION}-${REVISION}_${ARCH}.deb"

rm -rf "$STAGING_DIR"
mkdir -p \
  "$STAGING_DIR/DEBIAN" \
  "$STAGING_DIR/opt/desktop-agent" \
  "$STAGING_DIR/usr/bin" \
  "$STAGING_DIR/usr/share/applications" \
  "$OUTPUT_DIR"
chmod 0755 "$STAGING_DIR/DEBIAN"

tar --exclude="./.git" \
  --exclude="./.github" \
  --exclude="./build" \
  --exclude="./dist" \
  --exclude="./venv" \
  --exclude="./__pycache__" \
  --exclude="./*.pyc" \
  --exclude="./*.deb" \
  --exclude="./.env" \
  --exclude="./.env.*" \
  -C "$ROOT_DIR" -cf - . | tar -C "$STAGING_DIR/opt/desktop-agent" -xf -

if [ -f "$ROOT_DIR/desktop-agent.desktop" ]; then
  install -m 0644 "$ROOT_DIR/desktop-agent.desktop" \
    "$STAGING_DIR/usr/share/applications/desktop-agent.desktop"
fi

cat > "$STAGING_DIR/usr/bin/desktop-agent" <<'EOF'
#!/usr/bin/env bash
set -e

APP_DIR="/opt/desktop-agent"
VENV_DIR="$APP_DIR/venv"

if [ -x "$VENV_DIR/bin/python" ]; then
  exec "$VENV_DIR/bin/python" "$APP_DIR/main.py" "$@"
fi

exec python3 "$APP_DIR/main.py" "$@"
EOF
chmod 0755 "$STAGING_DIR/usr/bin/desktop-agent"

cat > "$STAGING_DIR/DEBIAN/control" <<EOF
Package: desktop-agent
Version: ${VERSION}-${REVISION}
Section: utils
Priority: optional
Architecture: ${ARCH}
Depends: python3 (>= 3.10), python3-venv, python3-pip, python3-tk
Maintainer: Desktop Agent Contributors <noreply@github.com>
Description: AI-powered Linux desktop assistant
 Desktop Agent automates software installation and configuration using AI models.
EOF

cat > "$STAGING_DIR/DEBIAN/postinst" <<'EOF'
#!/usr/bin/env bash
set -e

APP_DIR="/opt/desktop-agent"
VENV_DIR="$APP_DIR/venv"

if [ ! -d "$VENV_DIR" ]; then
  python3 -m venv "$VENV_DIR"
fi

"$VENV_DIR/bin/pip" install --upgrade pip
"$VENV_DIR/bin/pip" install -r "$APP_DIR/requirements.txt"
EOF
chmod 0755 "$STAGING_DIR/DEBIAN/postinst"

cat > "$STAGING_DIR/DEBIAN/postrm" <<'EOF'
#!/usr/bin/env bash
set -e

if [ "${1:-}" = "purge" ]; then
  rm -rf /opt/desktop-agent
fi
EOF
chmod 0755 "$STAGING_DIR/DEBIAN/postrm"

dpkg-deb --build "$STAGING_DIR" "$OUTPUT_FILE"
echo "Built package: $OUTPUT_FILE"
