#!/usr/bin/env bash

set -e

echo "Installing Dictatr..."

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

mkdir -p "$HOME/.local/bin"

cat > "$HOME/.local/bin/dictatr" << EOF
#!/usr/bin/env bash
exec "$PROJECT_ROOT/scripts/run.sh" "\$@"
EOF

chmod +x "$HOME/.local/bin/dictatr"

echo
echo "Installed successfully!"
echo

if [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then
    echo "WARNING: ~/.local/bin is not in your PATH."
    echo "Add this to your ~/.bashrc or ~/.zshrc:"
    echo
    echo 'export PATH="$HOME/.local/bin:$PATH"'
    echo
fi

echo "Run:"
echo
echo "    dictatr"