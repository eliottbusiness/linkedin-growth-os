# LinkedIn Growth OS

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![License](https://img.shields.io/badge/license-proprietary-red)
![Platform](https://img.shields.io/badge/platform-Linux%20%7C%20macOS-green)

**LinkedIn Growth OS** est un plugin Hermes pour la prospection B2B automatisée via l'API BeReach. Il permet d'automatiser lidentification et la qualification de prospects LinkedIn.

## Fonctionnalités

- **Prospection B2B automatisée** — Recherche et qualification de prospects via l'API BeReach
- **ICP configurable** — Définissez votre client idéal (taille, localisation, rôles)
- **Wizard d'onboarding** — Configuration guidée pas à pas
- **Intégration Composio** — Connexion google-sheets, telegram, notion, slack
- **Lifecycle hooks** — Validation automatique de license au démarrage

## Installation

```bash
curl -fsSL https://raw.githubusercontent.com/eliottbusiness/linkedin-growth-os/main/install.sh | bash
```

Ou manuellement:

```bash
git clone https://github.com/eliottbusiness/linkedin-growth-os.git ~/.hermes/plugins/linkedin-growth-os
```

## Configuration

Lancez le wizard d'onboarding:

```bash
hermes linkedin-growth-os setup
```

Le wizard vous demandera:
1. Clé de licence (reçue par email)
2. Description de votre offre
3. Taille d'entreprise visée
4. Localisation géographique
5. Rôles des décideurs (CEO, Founder, etc.)
6. Configuration Composio MCP

## Commandes CLI

| Commande | Description |
|----------|-------------|
| `hermes linkedin-growth-os setup` | Lance le wizard de configuration |
| `hermes linkedin-growth-os start` | Démarre le moteur de prospection |
| `hermes linkedin-growth-os stop` | Arrête le moteur de prospection |
| `hermes linkedin-growth-os status` | Affiche le statut du plugin |
| `hermes linkedin-growth-os update` | Met à jour le plugin |

## Utilisation

Après configuration:

```
hermes linkedin-growth-os start
# Puis dans l'agent:
/linkedin-growth-os Trouve des CEOs de startups SaaS en France
```

## Architecture

```
linkedin-growth-os/
├── plugin.yaml          # Manifeste du plugin Hermes
├── __init__.py          # Module principal (register, hooks, CLI)
├── cli.py               # Wizard interactif + commandes
├── skills/              # Skill Hermes (prompts, config)
├── install.sh           # Script d'installation
├── README.md
└── LICENSE
```

## API Keys Requises

- **License Key** — Fournie par DeptFlow
- **BeReach API Key** — Configurée automatiquement après connexion

## Support

- Documentation: https://docs.deptflow.io
- Email: support@deptflow.io
- Issues: https://github.com/eliottbusiness/linkedin-growth-os/issues

## License

Copyright (c) 2026 DeptFlow. Tous droits réservés.
L'utilisation de ce plugin est soumise à la licence propriétaire DeptFlow.