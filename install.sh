#!/bin/bash
# LinkedIn Growth OS — Install Script
# curl -fsSL https://raw.githubusercontent.com/eliottbusiness/linkedin-growth-os/main/install.sh | bash

set -e

HERMES_HOME="${HERMES_HOME:-$HOME/.hermes}"
PLUGIN_DIR="$HERMES_HOME/plugins/linkedin-growth-os"
SKILL_DIR="$HERMES_HOME/skills/linkedin-growth-os"
REPO_URL="https://github.com/eliottbusiness/linkedin-growth-os.git"

echo "╔══════════════════════════════════════════════════════════╗"
echo "║      LINKEDIN GROWTH OS — Installation                   ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""

# Check Hermes installed
if ! command -v hermes &> /dev/null; then
    echo "✗ Hermes Agent non trouvé."
    echo "  Installez-le d'abord:"
    echo "  curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash"
    exit 1
fi

# Clone or update repo
if [ -d "$PLUGIN_DIR/.git" ]; then
    echo "→ Mise à jour du plugin..."
    git -C "$PLUGIN_DIR" pull origin main
else
    echo "→ Téléchargement du plugin..."
    mkdir -p "$(dirname $PLUGIN_DIR)"
    git clone "$REPO_URL" "$PLUGIN_DIR"
fi

# Copy skill to ~/.hermes/skills/
echo "→ Installation du skill..."
cp -r "$PLUGIN_DIR/skills/" "$SKILL_DIR"

echo ""
echo "✓ Installation terminée!"
echo ""
echo "Prochaine étape:"
echo "  hermes linkedin-growth-os setup"
echo ""