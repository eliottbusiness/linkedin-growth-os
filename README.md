# LinkedIn Growth OS

> Prospection B2B automatisée sur LinkedIn — Plugin Hermes

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![License](https://img.shields.io/badge/license-proprietary-red)
![Platform](https://img.shields.io/badge/platform-Linux%20%7C%20macOS-green)

---

## Installation (1 commande)

```bash
curl -fsSL https://raw.githubusercontent.com/eliottbusiness/linkedin-growth-os/main/install.sh | bash
```

> Si le lien ci-dessus ne fonctionne pas, utilisez le **miroir de backup** :
> ```bash
> curl -fsSL https://gist.githubusercontent.com/eliottbusiness/4779ee4c1b977fc51cd66e6b35988735/raw/install.sh | bash
> ```

---

## Setup initial

```bash
hermes linkedin-growth-os setup
```

Le wizard interactif vous guidera pour :
1. 📋 Saisir votre clé de licence
2. 💼 Définir votre offre (ce que vous vendez)
3. 🎯 Configurer votre ICP (taille entreprise, localisation, rôles cibles)
4. 🔗 Activer les MCP Composio (Google Sheets, Telegram)

---

## Démarrage

```bash
# Lancer la prospection automatique
hermes linkedin-growth-os start

# Ou parler directement à l'agent
/linkedin-growth-os Prospect des CEOs SaaS B2B en France
```

---

## Les 7 workflows

| ID | Workflow | Objectif |
|----|----------|----------|
| **WF01** | Prospection Lead Qualifié | Identifier et scorer des prospects selon l'ICP |
| **WF02** | Outreach Multi-Touch | Transformer un prospect en conversation commerciale |
| **WF03** | Publication Automatique | Publier du contenu LinkedIn depuis un calendrier |
| **WF04** | Lead Magnet Automatique | Envoyer un lead magnet aux comentaristes déclencheurs |
| **WF05** | Competitor Intent Hijacking | Capter les prospects qui interagissent avec vos concurrents |
| **WF06** | Hiring Signal Detector | Détecter les entreprises en recrutement actif |
| **WF07** | Viral Content Intelligence | Analyser les patterns de contenu viral |

---

## Architecture

```
linkedin-growth-os/
├── plugin.yaml                    ← Manifest du plugin Hermes
├── __init__.py                    ← Hooks de registre
├── cli.py                         ← Wizard setup + commands CLI
├── install.sh                     ← Script d'installation
├── README.md
├── LICENSE
└── skills/linkedin-growth-os/
    ├── SKILL.md                   ← Entry point de l'agent
    └── workflows/
        ├── wf01-wf07.md           ← Détail de chaque workflow
```

---

## Prérequis

- **Hermes Agent** installé ([Installation](https://hermes-agent.nousresearch.com/docs))
- **Compte BeReach** avec clés API
- **MCP Composio** configuré avec : `google-sheets`, `telegram`

---

## Configuration MCP Composio

Dans l'app Composio, activez ces outils :

| Tool | Required | Usage |
|------|----------|-------|
| `google-sheets` | ✅ Oui | Écriture des prospects contactés |
| `telegram` | ✅ Oui | Rapports quotidiens |
| `notion` | Optionnel | CRM alternatif |
| `slack` | Optionnel | Notifications Slack |

---

## Endpoint BeReach utilisés

| Endpoint | Action |
|----------|--------|
| `POST /search/linkedin/people` | Recherche prospects |
| `POST /search/linkedin/posts` | Recherche posts |
| `POST /visit/linkedin/profile` | Enrichissement profil |
| `POST /visit/linkedin/company` | Enrichissement entreprise |
| `POST /collect/linkedin/posts` | Collecte posts |
| `POST /collect/linkedin/comments` | Collecte commentaires |
| `POST /collect/linkedin/likes` | Collecte likeurs |
| `POST /connect/linkedin/profile` | Demande de connexion |
| `POST /message/linkedin` | Envoi DM |
| `POST /analytics/linkedin/post` | Analytics post |

---

## Limites de sécurité

| Action | Limite / jour |
|--------|---------------|
| Demandes de connexion | 30 |
| Messages directs | 50 |
| Visites de profil | 100 |

> Ces limites protègent votre compte LinkedIn. Le plugin respecte automatiquement ces seuils.

---

## Support

Contactez votre consultant DeptFlow ou ouvrez un message LinkedIn.

---

**DeptFlow** — © 2026 | [deptflow.io](https://deptflow.io)