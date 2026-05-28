---
name: linkedin-growth-os
description: "LinkedIn B2B prospection engine — 7 workflows automatisés"
version: 1.0.0
author: DeptFlow
license: proprietary
platforms: [linux, macos]
metadata:
  hermes:
    tags: [linkedin, prospection, b2b, automation, bereach]
    category: sales
    config:
      - key: license_key
        required: true
      - key: offer
        required: true
      - key: company_size
        required: true
      - key: location
        required: true
      - key: target_titles
        required: true
---

# LinkedIn Growth OS

## Vue d'ensemble

LinkedIn Growth OS est un moteur de prospection B2B automatisée qui orchestre 7 workflows différents via l'API BeReach. L'agent lit la configuration client (`~/.hermes/plugins/linkedin-growth-os/config.json`) et exécute les workflows selon les objectifs définis.

## Configuration client

L'agent lit la config depuis:
```
~/.hermes/plugins/linkedin-growth-os/config.json
```

Champs disponibles:
- `offer`: Description de l'offre du client
- `company_size`: Taille d'entreprise recherchée (1-10, 11-50, 51-250, 250+, all)
- `location`: Localisation géographique
- `target_titles`: Rôles cibles (ex: ["CEO", "Founder", "Head of"])

## Les 7 workflows

### WF01 — Prospection Lead Qualifié
**Objectif:** Identifier et scorer des prospects selon l'ICP.
**Signaux prioritaires:** explicit_pain, seeking_solution, tool_change
**Commande:** `EXECUTE_WF01 <objectif_prospection>`

### WF02 — Outreach Multi-Touch  
**Objectif:** Transformer un prospect qualifié en conversation commerciale.
**Signaux:** pendingConnection acceptée → envoi DM personnalisé
**Commande:** `EXECUTE_WF02 <profile_url> <contexte_conversation>`

### WF03 — Publication Automatique
**Objectif:** Publier du contenu LinkedIn depuis un calendrier externe.
**Commande:** `EXECUTE_WF03 <post_text> [scheduled_at]`

### WF04 — Lead Magnet Automatique
**Objectif:** Envoyer un lead magnet aux utilisateurs qui commentent un mot-clé.
**Trigger:** Mot-clé détecté dans un commentaire
**Commande:** `EXECUTE_WF04 <post_url> <lead_magnet_url> <keywords>`

### WF05 — Competitor Intent Hijacking
**Objectif:** Récupérer les prospects qui interagissent avec les publications concurrents.
**Sources:** Posts concurrents → Likeurs + Commentateurs → Enrichissement
**Commande:** `EXECUTE_WF05 <competitor_names>`

### WF06 — Hiring Signal Detector
**Objectif:** Détecter les entreprises en recrutement actif (signal de croissance).
**Indicateurs:** Jobs publicados récemment, postes clés à recruter
**Commande:** `EXECUTE_WF06 <industry_keywords>`

### WF07 — Viral Content Intelligence
**Objectif:** Analyser les contenus viraux et reproduire les patterns gagnants.
**Métriques:** hooks, émotions, CTA, engagement rate
**Commande:** `EXECUTE_WF07 <industry_keywords>`

## Endpoints BeReach utilisés

| Endpoint | Usage | Credits |
|----------|-------|---------|
| POST /search/linkedin/people | Recherche prospects | 1 |
| POST /visit/linkedin/profile | Enrichissement profil | 1 |
| POST /visit/linkedin/company | Enrichissement entreprise | 1 |
| POST /collect/linkedin/posts | Collecte posts | 1 |
| POST /collect/linkedin/comments | Commentaires | 1 |
| POST /collect/linkedin/likes | Likeurs | 1 |
| POST /connect/linkedin/profile | Demande de connexion | 1 |
| POST /message/linkedin | Envoi DM | 1 |
| POST /analytics/linkedin/post | Analytics post | 1 |

## Format des messages LinkedIn

Les messages sont générés dynamiquement selon:
1. Le profil du prospect (poste, entreprise, activité récente)
2. L'offre du client (depuis config)
3. Le contexte de la conversation ou du post déclencheur

**Règles:**
- 3-5 phrases maximum pour les messages initiaux
- Mentionner un élément spécifique du profil du prospect
- Jamais de pitch direct — créer d'abord une relation
- Poser des questions ouvertes pour engager

## Limites de sécurité

- 30 demandes de connexion / jour
- 50 messages directs / jour
- 100 visites de profil / jour
- Plage horaire: 8h-18h (heure locale prospect)
- Jours ouvrés uniquement (Lun-Vendredi)

## CRM — Google Sheets

Les prospects sont automatiquement写入:
- Fichier: `prospects_YYYY-MM-DD.csv`
- Colonnes: Date, Prénom, Nom, Profil LinkedIn, Entreprise, Poste, Score Intent, Signal, Source, Notes

## Pièges connus

1. **Champ commentText** — L'API BeReach retourne le texte du commentaire dans `commentText`, pas `comment`.
2. **Rate limits** — Toujours vérifier `retryAfter` et espacer les actions de 2-5 minutes.
3. **Déduplication** — Ne pas recontacter un prospect refusé dans les 30 derniers jours.

## Rapport quotidien

Chaque soir (18h), l'agent envoie un rapport Telegram avec:
- Nombre de prospects contactés
- Taux de réponse
- Signaux d'intention détectés
- Prochains steps pour le lendemain

## Pour démarrer

```bash
hermes linkedin-growth-os setup    # Configuration initiale
hermes linkedin-growth-os start    # Démarrer le moteur

# Ou directement via l'agent:
/linkedin-growth-os Prospect des CEOs SaaS B2B en France avec signaux de croissance
```