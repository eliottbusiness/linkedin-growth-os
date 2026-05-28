# WF04 — Lead Magnet Automatique

## Objectetif

Envoyer automatiquement un lead magnet (guide, checklist, template...) aux utilisateurs LinkedIn qui commentent un mot-clé spécifique sur un post. C'est le workflow d'inbound le plus puissant.

**Credits estimés:** 2-3 par lead récupéré

---

## Architecture

```
MONITOR_COMMENTS → KEYWORD_DETECTION → VISIT_COMMENTER → SEND_CONNECTION → BOOST_COMMENT
    (1 crédit)          (gratuit)          (1 crédit)           (1 crédit)         (1 crédit)
```

---

## Étape 1 — MONITOR_COMMENTS

Collecter les commentaires d'un post cible.

### Endpoint
```
POST https://api.bereach.ai/collect/linkedin/comments
```

### Request Body
```json
{
  "postUrl": "https://www.linkedin.com/posts/techcorp-xyz/lead-magnet-post",
  "count": 20
}
```

### Response
```json
{
  "profiles": [
    {
      "profileUrl": "https://www.linkedin.com/in/sophie-leclerc/",
      "commentText": "Super analyse ! Je cherche justement un outil pour automatiser ma prospection.",
      "commentUrn": "urn:li:comment:(activity:xyz,123456789)",
      "postedAt": "2026-05-25T14:30:00Z"
    }
  ],
  "total": 15
}
```

### Piège
**Champ `commentText`** — L'API retourne le texte dans `commentText`, pas `comment` ni `text`.
```python
# ❌ WRONG
text = comment.get("comment", comment.get("text", ""))

# ✅ CORRECT
text = comment.get("commentText", comment.get("comment", ""))
```

---

## Étape 2 — KEYWORD_DETECTION (Gratuit)

Détecter si un commentaire contient un mot-clé déclencheur.

### Mots-clés déclencheurs (FR)
```
["je cherche", "je veux", "j'ai besoin", "conseil", "aide", "outil", 
 "comment faire", "recommander", "automatiser", "prospection", "lead"]
```

### Mots-clés déclencheurs (EN)
```
["looking for", "need", "help", "tool", "recommend", "automate", 
 "prospecting", "lead generation", "advice", "how to"]
```

```python
TRIGGER_KEYWORDS = [
    "je cherche", "je veux", "j'ai besoin", "conseil", "aide",
    "outil", "automatiser", "prospection", "lead", "recommander"
]

def detect_trigger(comment_text):
    """Retourne True si le commentaire contient un mot-clé déclencheur."""
    text = comment_text.lower()
    return any(kw in text for kw in TRIGGER_KEYWORDS)

def extract_want_statement(comment_text):
    """Extrait la phrase qui montre le besoin."""
    text = comment_text.lower()
    for kw in ["je cherche", "je veux", "j'ai besoin", "looking for", "need"]:
        idx = text.find(kw)
        if idx != -1:
            # Retourner les 100 caractères autour du mot-clé
            start = max(0, idx - 20)
            end = min(len(text), idx + 80)
            return comment_text[start:end]
    return None
```

---

## Étape 3 — VISIT_COMMENTER

Enrichir le profil du comentariste.

### Endpoint
```
POST https://api.bereach.ai/visit/linkedin/profile
```

### Request Body
```json
{
  "profile": "https://www.linkedin.com/in/sophie-leclerc/"
}
```

### Response
```json
{
  "id": "sph123",
  "firstName": "Sophie",
  "lastName": "Leclerc",
  "headline": "Responsable Commerciale @ScaleUp SAS",
  "summary": "10 ans d'expérience en vente...",
  "email": "s.leclerc@scaleup.com",
  "positions": [
    {
      "company": "ScaleUp SAS",
      "companyUrl": "https://www.linkedin.com/company/scaleup",
      "title": "Responsable Commerciale"
    }
  ]
}
```

### Logique de filtrage
```python
def filter_lead(profile_data, config):
    """Vérifie que le comentariste est un lead qualifié."""
    headline = profile_data.get("headline", "").lower()
    
    # Skip si c'est un concurrent (vend de la prospection)
    competitors = ["prospect", "lead gen", "agency", "consultant", "agent ia"]
    if any(c in headline for c in competitors):
        return False, "concurrent"
    
    # Skip si pas de poste (student, unemployed)
    if not profile_data.get("positions"):
        return False, "no_position"
    
    return True, "qualified"
```

---

## Étape 4 — SEND_CONNECTION

Envoyer une demande de connexion avec le lead magnet.

### Endpoint
```
POST https://api.bereach.ai/connect/linkedin/profile
```

### Request Body
```json
{
  "profile": "https://www.linkedin.com/in/sophie-leclerc/",
  "message": "Sophie, ton commentaire sur [post] m'a convaincu de te sends directement notre Guide '5 automatisations qui ont boosté notre pipeline de 40%'. Je te l'envoie dès qu'on est connectés !"
}
```

### Génération du message
```python
def generate_lead_magnet_message(commenter_name, comment_text, lead_magnet_title):
    """Génère un message personnalisé de connexion avec lead magnet."""
    
    # Extraire le besoin du commentaire
    want = extract_want_statement(comment_text)
    
    templates = [
        f"{commenter_name}, ton commentaire sur '[topic]' m'a poussé à te sends directement notre {lead_magnet_title}. Je te l'envoie dès qu'on est connectés !",
        f"{commenter_name} — ton besoin ('{want[:50]}...') correspond exactement à ce que notre {lead_magnet_title} adresse. On se connecte pour que je te l'envoie ?",
    ]
    
    import random
    return random.choice(templates)

# Lead magnet title → à configurer par le client
LEAD_MAGNET_TITLE = "Guide: 5 automatisations qui ont boosté notre pipeline de 40%"
```

---

## Étape 5 — BOOST_COMMENT

Répondre au commentaire pour confirmer l'envoi.

### Endpoint
```
POST https://api.bereach.ai/reply/linkedin/comment
```

### Request Body
```json
{
  "commentUrn": "urn:li:comment:(activity:xyz,123456789)",
  "message": "C'est envoyé 🚀! Tu devrais recevoir le guide dans les prochaines minutes. N'hésite pas si tu as des questions après lecture !"
}
```

### Response
```json
{
  "success": true
}
```

---

## Pipeline complet

```python
def run_wf04(post_url, lead_magnet_url, keywords=None, max_leads=10):
    """
    WF04 — Lead Magnet Automatique
    """
    results = []
    keywords = keywords or TRIGGER_KEYWORDS
    
    # Étape 1: Collecter les commentaires
    comments = call_bereach("/collect/linkedin/comments", {
        "postUrl": post_url,
        "count": 20
    }).get("profiles", [])
    
    for comment in comments[:max_leads]:
        profile_url = comment["profileUrl"]
        comment_text = comment.get("commentText", comment.get("comment", ""))
        
        # Étape 2: Détecter le trigger
        if not detect_trigger_with_keywords(comment_text, keywords):
            continue
        
        # Étape 3: Enrichir le profil
        profile_data = call_bereach("/visit/linkedin/profile", {
            "profile": profile_url
        })
        
        qualified, reason = filter_lead(profile_data, {})
        if not qualified:
            continue
        
        # Étape 4: Envoyer la connexion
        connect_msg = generate_lead_magnet_message(
            profile_data["firstName"],
            comment_text,
            LEAD_MAGNET_TITLE
        )
        connect_result = call_bereach("/connect/linkedin/profile", {
            "profile": profile_url,
            "message": connect_msg
        })
        
        # Étape 5: Répondre au commentaire
        if connect_result.get("success"):
            call_bereach("/reply/linkedin/comment", {
                "commentUrn": comment["commentUrn"],
                "message": "C'est envoyé 🚀!"
            })
            
            results.append({
                "profile": profile_data,
                "comment": comment_text,
                "status": "connected"
            })
        
        import time; time.sleep(5)  # 5s entre chaque lead
    
    return results
```

---

## Pièges

1. **Spam de commentaires** — Ne répondeq pas à TOUS les commentaires, только les déclencheurs.
2. **Temps réel** — Les commentaires doivent être traités dans les 1-2h pour max impact.
3. **Lead magnet pertinent** — Le guide doit vraiment adresser le besoin exprimé.
4. **Double opt-in** — Vérifier que l'email collecting est conforme RGPD.