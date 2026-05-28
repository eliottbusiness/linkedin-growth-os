# WF03 — Publication Automatique

## Objectif

Publier automatiquement du contenu LinkedIn depuis un calendrier externe (Notion, Google Sheets, fichier CSV). Chaque post est analysé et optimisé avant publication.

**Credits estimés:** 1-2 par post

---

## Architecture

```
LOAD_QUEUE → VERIFY_PAGE_ACCESS → PUBLISH_POST → COLLECT_ANALYTICS
   (gratuit)         (1 crédit)        (1 crédit)      (1 crédit)
```

---

## Étape 1 — LOAD_QUEUE

Charger le calendrier de publication depuis une source externe.

**Sources supportées:**
- Google Sheets (colonnes: text, scheduledAt, imageUrl, status)
- Notion database
- CSV file
- API externe

```python
def load_content_queue(source="google-sheets"):
    """
    Charge les posts en attente de publication.
    Status: pending, published, failed
    """
    if source == "google-sheets":
        return load_from_google_sheets()
    elif source == "notion":
        return load_from_notion()
    elif source == "csv":
        return load_from_csv("content_calendar.csv")
    
def load_from_google_sheets():
    """Charge depuis Google Sheets."""
    # Utiliser MCP Composio google-sheets
    # Sheet: content_calendar_{client_id}
    import subprocess
    result = subprocess.run([
        "composio", "exec", "google-sheets", "read",
        "--spreadsheet", f"content_calendar",
        "--range", "A:D"
    ], capture_output=True, text=True)
    
    posts = []
    lines = result.stdout.strip().split("\n")[1:]  # Skip header
    for line in lines:
        parts = line.split(",")
        if len(parts) >= 3:
            posts.append({
                "text": parts[0],
                "scheduledAt": parts[1] if len(parts) > 1 else None,
                "imageUrl": parts[2] if len(parts) > 2 else None,
                "status": parts[3] if len(parts) > 3 else "pending"
            })
    return [p for p in posts if p["status"] == "pending"]
```

---

## Étape 2 — VERIFY_PAGE_ACCESS

Vérifier que le plugin a accès à la Page Entreprise LinkedIn.

### Endpoint
```
POST https://api.bereach.ai/me/linkedin/company-pages/permissions
```

### Request Body
```json
{
  "universalName": "techcorp"
}
```

### Response
```json
{
  "roles": ["administrator", "content_admin"],
  "companyPageUrn": "urn:li:organization:123456",
  "hasPostPermission": true
}
```

### Vérification avant chaque publication
```python
def verify_page_access(universal_name):
    result = call_bereach("/me/linkedin/company-pages/permissions", {
        "universalName": universal_name
    })
    
    if not result.get("hasPostPermission"):
        raise PermissionError(f"Pas de droits de publication pour {universal_name}")
    
    return result
```

---

## Étape 3 — PUBLISH_POST

Publier le post LinkedIn (instantané ou programmé).

### Endpoint
```
POST https://api.bereach.ai/publish/linkedin/post
```

### Request Body (Publication instantanée)
```json
{
  "text": "3 signaux qui montrent que votre prospect est prêt à acheter 🤝\n\n1. Il consulte régulièrement vos contenus\n2. Il recommande votre solution à son réseau\n3. Il pose des questions techniques sur le pricing\n\nCes signaux sont invisibles si vous n'avez pas d'outil de tracking.\n\nVous utilisez quoi pour les détecter ? 👇",
  "mode": "instant",
  "imageUrl": null
}
```

### Request Body (Programmé)
```json
{
  "text": "Le même contenu...",
  "mode": "scheduled",
  "scheduledAt": "2026-06-01T09:00:00Z",
  "imageUrl": "https://cdn.example.com/image.jpg"
}
```

| Champ | Type | Description |
|-------|------|-------------|
| `text` | string | Contenu du post (max 3000 caractères) |
| `mode` | string | `instant` ou `scheduled` |
| `scheduledAt` | string | Timestamp ISO 8601 (si mode=scheduled) |
| `imageUrl` | string | URL de l'image (optionnel, max 9 images) |

### Response
```json
{
  "success": true,
  "postUrl": "https://www.linkedin.com/posts/activity_xyz789",
  "postUrn": "urn:li:activity:1234567890"
}
```

### Formatage du post
```python
def format_post_text(raw_text, max_len=2900):
    """Formate le texte pour LinkedIn."""
    # Tronquer si trop long
    if len(raw_text) > max_len:
        raw_text = raw_text[:max_len-3] + "..."
    
    # Ajouter des line breaks pour la lisibilité
    lines = raw_text.split("\n")
    formatted = "\n\n".join(lines)
    
    return formatted
```

---

## Étape 4 — COLLECT_ANALYTICS

Collecter les métriques du post après 24-48h.

### Endpoint
```
POST https://api.bereach.ai/analytics/linkedin/post
```

### Request Body
```json
{
  "postUrl": "https://www.linkedin.com/posts/activity_xyz789"
}
```

### Response
```json
{
  "postUrl": "https://www.linkedin.com/posts/activity_xyz789",
  "viewsCount": 1247,
  "likesCount": 89,
  "commentsCount": 23,
  "sharesCount": 5,
  "engagementRate": 9.4,
  "impressions": 1150
}
```

### Calcul du score de performance
```python
def calculate_viral_score(analytics):
    """
    Score de viralité basé sur l'engagement.
    >5% = viral, 2-5% = bon, <2% = faible
    """
    rate = analytics.get("engagementRate", 0)
    
    if rate >= 10:
        return "viral", "À reposter ou amplifier"
    elif rate >= 5:
        return "good", "Bon engagement"
    elif rate >= 2:
        return "average", "En dessous de la moyenne"
    else:
        return "low", "À améliorer — tester nouveaux hooks"
```

---

## Publication programmée — Cron Setup

```python
# scripts/schedule_posts.py — À exécuter chaque heure
SCHEDULE_INTERVAL_HOURS = 1

def check_and_publish():
    """Vérifie les posts programmés et les publie à l'heure."""
    pending = load_content_queue()
    now = datetime.utcnow()
    
    for post in pending:
        if post.get("mode") == "scheduled":
            scheduled = datetime.fromisoformat(post["scheduledAt"])
            
            # Publier si dans la fenêtre +/- 5 min
            if abs((now - scheduled).total_seconds()) < 300:
                result = publish_post(post)
                
                if result["success"]:
                    mark_as_published(post["id"])
                    log_analytics(post["id"])
                else:
                    mark_as_failed(post["id"], result.get("error"))

# Ajouter au crontab:
# 0 * * * * python3 /path/to/schedule_posts.py
```

---

## Pièges

1. **Posts trop promotionnels** — LinkedIn penalise les posts purely sales. Viser 80% valeur + 20% promo.
2. **Images trop pesadas** — Compresser à <5MB, format JPG/PNG.
3. **Hashtags excessifs** — Max 3-5 hashtags, les mettre en fin de post.
4. **Scheduled posts** — Vérifier le fuseau horaire (LinkedIn utilise UTC).