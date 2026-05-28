# WF05 — Competitor Intent Hijacking Engine

## Objectif

Récupérer automatiquement les prospects qui interagissent avec les publications de vos concurrents (likent, commentent). Ces personnes ont démontré un intérêt pour des solutions similaires = сигнал achat.

**Credits estimés:** 5-8 par campagne concurrent

---

## Architecture

```
SEARCH_COMPETITOR_POSTS → COLLECT_LIKES → COLLECT_COMMENTS → ENRICH_PROFILES → AI_INTENT_DETECTION
    (1 crédit)               (1 crédit)        (1 crédit)          (1 crédit)         (gratuit)
```

---

## Étape 1 — SEARCH_COMPETITOR_POSTS

Trouver les posts récents des concurrents.

### Endpoint
```
POST https://api.bereach.ai/search/linkedin/posts
```

### Request Body
```json
{
  "keywords": ["notion", "hubspot", "salesforce", "pipedrive"],
  "count": 10
}
```

### Response
```json
{
  "posts": [
    {
      "postUrl": "https://www.linkedin.com/posts/hubspot-france/new-features",
      "text": "Découvrez nos dernières mises à jour CRM...",
      "authorName": "HubSpot France",
      "authorUrl": "https://www.linkedin.com/company/hubspot",
      "postedAt": "2026-05-20T10:00:00Z",
      "likesCount": 245,
      "commentsCount": 34
    }
  ]
}
```

### Configuration concurrentielle
```python
COMPETITORS = {
    "hubspot": {
        "keywords": ["hubspot", "crm hubspot"],
        "company_url": "https://www.linkedin.com/company/hubspot"
    },
    "salesforce": {
        "keywords": ["salesforce", "crm salesforce"],
        "company_url": "https://www.linkedin.com/company/salesforce"
    },
    "pipedrive": {
        "keywords": ["pipedrive", "crm pipedrive"],
        "company_url": "https://www.linkedin.com/company/pipedrive"
    }
}
```

---

## Étape 2 — COLLECT_LIKES

Récupérer les personnes qui ont liké les posts concurrents.

### Endpoint
```
POST https://api.bereach.ai/collect/linkedin/likes
```

### Request Body
```json
{
  "postUrl": "https://www.linkedin.com/posts/hubspot-france/new-features"
}
```

### Response
```json
{
  "profiles": [
    {
      "profileUrl": "https://www.linkedin.com/in/marc-dubois/",
      "likedAt": "2026-05-21T08:15:00Z"
    },
    {
      "profileUrl": "https://www.linkedin.com/in/caroline-martin/",
      "likedAt": "2026-05-21T09:30:00Z"
    }
  ]
}
```

### Limites
- Retourne max 100 profiles par post
- Prioriser les posts avec >50 likes (signaux plus frais)

---

## Étape 3 — COLLECT_COMMENTS

Récupérer les personne qui ont commenté.

### Endpoint
```
POST https://api.bereach.ai/collect/linkedin/comments
```

### Request Body
```json
{
  "postUrl": "https://www.linkedin.com/posts/hubspot-france/new-features",
  "count": 20
}
```

### Response
```json
{
  "profiles": [
    {
      "profileUrl": "https://www.linkedin.com/in/thomas-robert/",
      "commentText": "Intéressant ! Vous proposez quoi pour les PME ?",
      "commentUrn": "urn:li:comment:(activity:xyz,789)",
      "postedAt": "2026-05-21T10:00:00Z"
    }
  ]
}
```

---

## Étape 4 — ENRICH_PROFILES

Enrichir les profils collectés (likes + comments).

### Endpoint
```
POST https://api.bereach.ai/visit/linkedin/profile
```

### Request Body
```json
{
  "profile": "https://www.linkedin.com/in/marc-dubois/"
}
```

### Response
```json
{
  "id": "mdc123",
  "firstName": "Marc",
  "lastName": "Dubois",
  "headline": "DRH @GroupeAlternatif",
  "email": "m.dubois@groupealternatif.com",
  "summary": "15 ans en RH...",
  "positions": [
    {
      "company": "GroupeAlternatif",
      "companyUrl": "https://www.linkedin.com/company/groupe-alternatif",
      "title": "Directeur RH",
      "current": true
    }
  ]
}
```

### Logique de qualification
```python
def qualify_profile(profile_data, client_offer):
    """
    Vérifie si le prospectliker/commenter concurrent est qualifié.
    """
    headline = profile_data.get("headline", "").lower()
    summary = profile_data.get("summary", "").lower()
    offer = client_offer.lower()
    
    # Skip si c'est un empleado du concurrent
    competitor_names = ["hubspot", "salesforce", "pipedrive", "crm"]
    if any(c in (headline + summary) for c in competitor_names):
        return False, "employee_competitor"
    
    # Skip si pas de poste décisionnaire
    decision_keywords = ["dirigeant", "ceo", "founder", "head of", "directeur", 
                         "responsable", "manager", "vp", "chief"]
    if not any(k in headline for k in decision_keywords):
        return False, "non_decision_maker"
    
    return True, "qualified"
```

---

## Étape 5 — AI_INTENT_DETECTION (Gratuit)

Analyser les signaux d'intention dans les posts/commentaires du prospect.

```python
INTENT_SIGNALS = {
    "switching": ["changer", "switching", "migrer", "changement", "nouveau crm", "onboarding"],
    "evaluating": ["en train d'évaluer", "comparons", "test en cours", "rfp"],
    "budget_available": ["budget", "approuvé", "investissement", "q4", "fy2026"],
    "pain_explicit": ["frustré", "ne fonctionne pas", "problème", "limitation", "c'est galère"]
}

def detect_intent_signals(profile_data, posts, comments):
    """Analyse les signaux d'intention d'un prospect concurrent."""
    all_text = " ".join([
        profile_data.get("summary", ""),
        " ".join([p.get("text", "") for p in posts]),
        " ".join([c.get("commentText", c.get("comment", "")) for c in comments])
    ]).lower()
    
    detected_signals = []
    for signal, keywords in INTENT_SIGNALS.items():
        if any(kw in all_text for kw in keywords):
            detected_signals.append(signal)
    
    # Score d'intention
    score = len(detected_signals) * 25  # 25 points par signal
    if score >= 50:
        lifecycle = "hot"
    elif score >= 25:
        lifecycle = "warm"
    else:
        lifecycle = "cold"
    
    return {
        "score": min(score, 100),
        "signals": detected_signals,
        "lifecycle_stage": lifecycle
    }
```

---

## Pipeline complet

```python
def run_wf05(competitors_list, client_offer, limit_per_competitor=20):
    """
    WF05 — Competitor Intent Hijacking
    """
    all_prospects = []
    
    for competitor_name in competitors_list:
        comp = COMPETITORS.get(competitor_name)
        if not comp:
            continue
        
        # Étape 1: Trouver les posts
        posts = call_bereach("/search/linkedin/posts", {
            "keywords": comp["keywords"],
            "count": 5
        }).get("posts", [])
        
        for post in posts[:3]:  # Top 3 posts par concurrent
            post_url = post["postUrl"]
            
            # Étape 2: Collecter les likes
            likers = call_bereach("/collect/linkedin/likes", {
                "postUrl": post_url
            }).get("profiles", [])[:limit_per_competitor]
            
            # Étape 3: Collecter les commentaires
            commenters = call_bereach("/collect/linkedin/comments", {
                "postUrl": post_url,
                "count": 10
            }).get("profiles", [])[:limit_per_competitor]
            
            all_profiles = likers + commenters
            
            for p in all_profiles:
                # Étape 4: Enrichir
                profile_data = call_bereach("/visit/linkedin/profile", {
                    "profile": p["profileUrl"]
                })
                
                qualified, reason = qualify_profile(profile_data, client_offer)
                if not qualified:
                    continue
                
                # Collecter les posts du prospect
                prospect_posts = call_bereach("/collect/linkedin/posts", {
                    "profileUrl": p["profileUrl"],
                    "count": 5,
                    "returnReposts": False
                }).get("posts", [])
                
                # Étape 5: Scoring intent
                intent = detect_intent_signals(profile_data, prospect_posts, [])
                
                all_prospects.append({
                    "profile": profile_data,
                    "source": f"competitor_{competitor_name}",
                    "intent": intent,
                    "original_post": post_url
                })
                
                import time; time.sleep(3)
    
    return all_prospects
```

---

## Pièges

1. **Trop de prospects** — Un concurrent populaire peut générer 500+ likers. Filter par intent avant d'enrichir.
2. **Doublons** — Un même prospect peut liker ET commenter. Dédupliquer par profileUrl.
3. **Timing** — Plus le like/comment est récent, plus le signal est chaud.
4. **Employés concurrents** — Toujours filter les employés des concurrents.