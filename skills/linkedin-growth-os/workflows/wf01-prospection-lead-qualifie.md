# WF01 — Prospection Lead Qualifié

## Objectif

Identifier, enrichir et scorer automatiquement des prospects LinkedIn selon un ICP précis (Ideal Customer Profile). Ce workflow est le point d'entrée principal de LinkedIn Growth OS.

**Credits estimés:** 4-6 par prospect

---

## Architecture

```
SEARCH_PEOPLE → LOCAL_FILTER → VISIT_PROFILE → VISIT_COMPANY → COLLECT_POSTS → INTENT_SCORING
    (1 crédit)    (gratuit)     (1 crédit)      (1 crédit)      (1 crédit)      (gratuit)
```

---

## Étape 1 — SEARCH_PEOPLE

Recherche des prospects selon les critères ICP.

### Endpoint
```
POST https://api.bereach.ai/search/linkedin/people
```

### Headers
```
Authorization: Bearer {BEREACH_API_KEY}
Content-Type: application/json
```

### Request Body
```json
{
  "keywords": ["SDR", "Head of Sales", "Growth"],
  "location": ["France"],
  "connectionDegree": "F",
  "count": 50,
  "start": 0
}
```

| Champ | Type | Description |
|-------|------|-------------|
| `keywords` | array[string] | Mots-clés de recherche (poste, industrie) |
| `location` | array[string] | Pays/régions (ISO ou nom) |
| `connectionDegree` | string | `F` (1st), `S` (2nd), `O` (3rd+) connections |
| `count` | int | Nombre de résultats (max 50) |
| `start` | int | Offset de pagination |

### Response
```json
{
  "items": [
    {
      "id": "abc123",
      "profileUrl": "https://www.linkedin.com/in/jean-martin/",
      "headline": "Head of Sales @TechCorp",
      "location": "Paris Area, France",
      "firstConnection": true,
      "memberDistance": "F"
    }
  ],
  "total": 245,
  "hasMore": true
}
```

### Limite
- 50 results per request
- Use pagination with `start: 50, 100, ...`

---

## Étape 2 — LOCAL_FILTER (Gratuit)

Filtre local selon l'ICP du client (lu depuis `config.json`).

**Critères de filtrage:**
- Taille d'entreprise (`company_size`)
- Localisation (`location`)
- Rôles cibles (`target_titles`)
- Déduplication (éviter les doublons)

```python
def filter_prospect(item, config):
    """Filtre un prospect selon l'ICP."""
    # Vérifier taille entreprise via headline si disponible
    headline = item.get("headline", "").lower()
    
    # Vérifier localisation
    location = item.get("location", "").lower()
    target_loc = config.get("location", "france").lower()
    if target_loc not in location:
        return False
    
    # Vérifier titre/rôle
    titles = [t.lower() for t in config.get("target_titles", [])]
    if titles and not any(t in headline for t in titles):
        return False
    
    return True
```

---

## Étape 3 — VISIT_PROFILE

Enrichissement du profil avec données complètes.

### Endpoint
```
POST https://api.bereach.ai/visit/linkedin/profile
```

### Request Body
```json
{
  "profile": "https://www.linkedin.com/in/jean-martin/",
  "includePosts": true,
  "includeAbout": true
}
```

### Response
```json
{
  "id": "abc123",
  "firstName": "Jean",
  "lastName": "Martin",
  "headline": "Head of Sales @TechCorp",
  "summary": "10 ans d'expérience en vente B2B...",
  "email": "j.martin@techcorp.com",
  "phone": "+33 6 XX XX XX XX",
  "positions": [
    {
      "company": "TechCorp",
      "companyUrl": "https://www.linkedin.com/company/techcorp",
      "title": "Head of Sales",
      "startDate": "2021-03",
      "current": true
    }
  ],
  "connectionsCount": 489,
  "profileUrl": "https://www.linkedin.com/in/jean-martin/"
}
```

### Piège
**Company URL** —有时返回 `companyUrl` as a dict `{"url": "..."}` or as a string. Toujours faire:
```python
company_url = r.get("companyUrl", r.get("company", {}).get("url", ""))
if isinstance(company_url, dict):
    company_url = company_url.get("url", "")
```

---

## Étape 4 — VISIT_COMPANY

Enrichissement de l'entreprise.

### Endpoint
```
POST https://api.bereach.ai/visit/linkedin/company
```

### Request Body
```json
{
  "companyUrl": "https://www.linkedin.com/company/techcorp"
}
```

### Response
```json
{
  "name": "TechCorp",
  "headquarter": "Paris, France",
  "employeeCount": "51-200",
  "industry": "Technology",
  "founded": "2018",
  "description": "Startup B2B SaaS..."
}
```

---

## Étape 5 — COLLECT_POSTS

Collecte des posts récents du prospect (45 derniers jours).

### Endpoint
```
POST https://api.bereach.ai/collect/linkedin/posts
```

### Request Body
```json
{
  "profileUrl": "https://www.linkedin.com/in/jean-martin/",
  "count": 10,
  "returnReposts": false
}
```

### Response
```json
{
  "posts": [
    {
      "postUrl": "https://www.linkedin.com/posts/jean-martin-123",
      "text": "Contenu du post...",
      "postedAt": "2026-05-15T10:30:00Z",
      "likesCount": 45,
      "commentsCount": 12
    }
  ]
}
```

---

## Étape 6 — INTENT_SCORING (Gratuit)

Scoring du prospect selon les signaux d'intention.

### Signaux haute priorité (🔥)
- `explicit_pain` — Mentionne un problème précis (ex: "frustré par ma prospection")
- `seeking_solution` — Cherche activement une solution (ex: "quel outil pour...?")
- `tool_change` — Veut changer d'outil/approche

### Signaux moyenne priorité (🟡)
- `active_project` — Travaille sur un projet lié (recrutement, croissance...)
- `competitor_mention` — Mentionne un concurrent ou en change
- `hiring_signal` — Recrute (signe de croissance =Budget disponible)

### Signaux basse priorité (🟢)
- `growth_or_launch_signal` — Annonce de croissance, funding, lancement produit

### Score calculation
```python
def calculate_intent_score(posts, profile_data, company_data):
    score = 0
    signals = []
    
    post_texts = [p.get("text", "") for p in posts]
    all_text = " ".join(post_texts).lower()
    
    # Haute priorité
    if any(w in all_text for w in ["frustré", "problème", "cherche solution", "automatiser"]):
        score += 40
        signals.append("explicit_pain")
    
    # Moyenne priorité
    if any(w in all_text for w in ["recrute", "hiring", "join us", "team growth"]):
        score += 25
        signals.append("hiring_signal")
    
    # Vérifier entreprise
    employee_count = company_data.get("employeeCount", "")
    if employee_count in ["51-200", "201-500", "500+"]:
        score += 15  # Plus l'entreprise est grande, plus le prospect est qualifié
    
    return {
        "score": min(score, 100),
        "signals": signals,
        "lifecycle_stage": "hot" if score >= 60 else "warm" if score >= 30 else "cold"
    }
```

---

## CRM — Logging

Chaque prospect enrichi est écrit dans Google Sheets.

**Format CSV:** `prospects_YYYY-MM-DD.csv`
| Colonne | Description |
|---------|-------------|
| A | Date |
| B | Prénom |
| C | Nom |
| D | Profil LinkedIn |
| E | Entreprise |
| F | Poste |
| G | Score Intent (0-100) |
| H | Signaux détectés |
| I | Source (WF01) |
| J | Notes |

---

## Python Executor

```python
"""Executor WF01 — Prospection Lead Qualifié"""
import os, json, subprocess
from datetime import datetime

BEREACH_API = "https://api.bereach.ai"
TOKEN = os.environ.get("BEREACH_TOKEN", "")

def call_bereach(endpoint, payload):
    """Appel à l'API BeReach."""
    import urllib.request
    data = json.dumps(payload).encode()
    req = urllib.request.Request(
        f"{BEREACH_API}{endpoint}",
        data=data,
        headers={"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"},
        method="POST"
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read())

def run_wf01(search_keywords, location, target_titles, limit=7):
    """
    WF01 — Prospection Lead Qualifié
    Retourne les prospects scorés.
    """
    results = []
    
    # Étape 1: Search
    search_results = call_bereach("/search/linkedin/people", {
        "keywords": search_keywords,
        "location": [location],
        "connectionDegree": "F",
        "count": 30,
        "start": 0
    })
    
    for item in search_results.get("items", [])[:limit]:
        profile_url = item["profileUrl"]
        
        # Étape 2: Filter local (skip si déjà scorés)
        # ... déduplication logic ...
        
        # Étape 3: Enrich
        profile_data = call_bereach("/visit/linkedin/profile", {
            "profile": profile_url,
            "includePosts": True,
            "includeAbout": True
        })
        
        # Étape 4: Company
        company_url = profile_data.get("companyUrl", "")
        company_data = {}
        if company_url:
            company_data = call_bereach("/visit/linkedin/company", {"companyUrl": company_url})
        
        # Étape 5: Posts
        posts = call_bereach("/collect/linkedin/posts", {
            "profileUrl": profile_url,
            "count": 5,
            "returnReposts": False
        }).get("posts", [])
        
        # Étape 6: Scoring
        intent = calculate_intent_score(posts, profile_data, company_data)
        
        if intent["score"] >= 25:
            results.append({
                "profile": profile_data,
                "company": company_data,
                "posts": posts,
                "intent": intent
            })
        
        # Respecter les limites
        import time; time.sleep(2)  # 2s entre chaque prospect
    
    return results
```

---

## Pièges

1. **Keywords trop génériques** — "CEO" seul ramène 50k résultats. Préciser: "CEO SaaS B2B France"
2. **Sans Sales Navigator** — Limité aux 1st connections (`F`). Prévoir un volume plus faible.
3. **Posts en anglais** — Vérifier que le prospect publie en français ou dans la langue cible.
4. **Score 0 = à skipper** — Ne pas perdre de crédits sur un prospect sans signaux.