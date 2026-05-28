# WF02 — Outreach Multi-Touch

## Objectif

Transformer automatiquement un prospect qualifié en conversation commerciale via une séquence de connexion + DM personnalisé. Ce workflow s'exécute après WF01 (prospection qualifiée).

**Credits estimés:** 3-5 par prospect (sans compter les retries)

---

## Architecture

```
PROFILE_WARMING → SEND_CONNECTION → POLL_ACCEPTANCE → SEND_DM
    (1 crédit)        (1 crédit)       (gratuit)         (1 crédit)
```

---

## Étape 1 — PROFILE_WARMING

Visiter le profil du prospect avant d'envoyer une demande de connexion. Cela "réchauffe" le profil et augmente le taux d'acceptation.

### Endpoint
```
POST https://api.bereach.ai/visit/linkedin/profile
```

### Request Body
```json
{
  "profile": "https://www.linkedin.com/in/jean-martin/"
}
```

### Response
```json
{
  "id": "abc123",
  "memberDistance": "F",
  "pendingConnection": false
}
```

### Pourquoi faire ça
- LinkedIn favorise les interactions mutuelles
- Réchauffer le profil avant connexion = taux d'acceptation +15-20%
- Permet de vérifier que le prospect est toujours actif

---

## Étape 2 — SEND_CONNECTION

Envoyer une demande de connexion avec message personnalisé.

### Endpoint
```
POST https://api.bereach.ai/connect/linkedin/profile
```

### Request Body
```json
{
  "profile": "https://www.linkedin.com/in/jean-martin/",
  "message": "Bonjour Jean, j'ai adoré ton post sur les défis de la prospection B2B. Je serais ravi d'échanger sur ce sujet !"
}
```

| Champ | Type | Description |
|-------|------|-------------|
| `profile` | string | URL du profil LinkedIn |
| `message` | string | Message de connexion (300 caractères max) |

### Response
```json
{
  "success": true,
  "requestId": "req_xyz789",
  "pendingConnection": true
}
```

### Piège
**Message trop long** — LinkedIn coupe à 300 caractères. Toujours tronquer:
```python
def truncate_message(msg, max_len=280):
    if len(msg) > max_len:
        return msg[:max_len-3] + "..."
    return msg
```

### Règles du message de connexion
1. **3 phrases max** — Pas de pitch, juste une raison de connexion
2. **Mentionner un élément précis** — Post, commentaire, entreprise, achievement
3. **Question ouverte** — Terminer par une question pour engager
4. **Pas de "je suis intéressé par..."** — Too pushy

**Exemples:**
```
"Bonjour [Prénom], j'ai lu avec intérêt ton retour sur [événement]. 
Comment abordes-tu [sujet] dans ton quotidien ? 
Je serais ravi d'échanger !"
```

```
"[Prénom], ton post sur [sujet] m'a vraiment fait réfléchir. 
Tu travailles sur ce sujet chez [Entreprise] ? 
Belle approche."
```

---

## Étape 3 — POLL_ACCEPTANCE

Vérifier si la demande de connexion a été acceptée.

### Endpoint
```
POST https://api.bereach.ai/chats/linkedin/find
```

### Request Body
```json
{
  "profile": "https://www.linkedin.com/in/jean-martin/"
}
```

### Response
```json
{
  "conversationUrn": "urn:li:member:sT2X3Y4Z5",
  "exists": true
}
```

### Logique de polling
```python
def poll_acceptance(profile_url, max_attempts=48, interval_hours=4):
    """
    Vérifie toutes les 4h si la connexion est acceptée.
    Timeout: 8 jours (48 x 4h = 192h)
    """
    for attempt in range(max_attempts):
        result = call_bereach("/chats/linkedin/find", {"profile": profile_url})
        
        if result.get("exists"):
            return {"accepted": True, "conversationUrn": result["conversationUrn"]}
        
        # Attendre 4h
        import time; time.sleep(4 * 3600)
    
    return {"accepted": False, "timeout": True}
```

---

## Étape 4 — SEND_DM

Envoyer un message direct personnalisé une fois la connexion acceptée.

### Endpoint
```
POST https://api.bereach.ai/message/linkedin
```

### Request Body
```json
{
  "conversationUrn": "urn:li:member:sT2X3Y4Z5",
  "message": "Bonjour Jean, ravi de nous être connectés ! J'ai remarqué que tu travailles sur la mise en place d'un process commercial solide chez TechCorp. C'est un sujet que je maîtrise bien — j'aide justement des entreprises comme la tienne à accélérer leur croissance. Tu aurais 15 min cette semaine pour qu'on en parle ?"
}
```

| Champ | Type | Description |
|-------|------|-------------|
| `conversationUrn` | string | URN de la conversation (depuis POLL_ACCEPTANCE) |
| `message` | string | Message personnalisé |

### Response
```json
{
  "success": true,
  "messageId": "msg_abc123"
}
```

---

## Message DM — Règles de rédaction

### Structure gagnante (AIDA adapté B2B)
1. **Attention** — Hook basé sur un élément du profil/post
2. **Intérêt** — Montrer qu'on comprend sa situation
3. **Désir** — Expliquer la transformation possible
4. **Action** — CTA précis (call, demo, échange)

### Exemple complet
```
Jean,

J'ai vu ton post sur les challenges de closing en ce moment — très juste.

Beaucoup de nos clients SaaS B2B rencontrent le même écueil: un bon pipeline mais des deals qui trainent.

On a conçu une approche qui réduit le cycle de vente de 30% en automatisant la prospection sur les signaux d'achat réels.

Tu serais open à qu'on échange 15 min pour voir si ça pourrait s'appliquer à TechCorp ?

[Votre nom]
```

### Règles absolues
- ❌ Pas de pitch dans le premier DM
- ❌ Pas de "je vous propose un rendez-vous"
- ✅ Mentionner quelque chose de spécifique au prospect
- ✅ Montrer qu'on comprend son contexte
- ✅ CTA轻轻 (15 min) pas agressif

---

## Séquence Multi-Touch complète

```python
def run_wf02(prospect_url, offer_context, max_wait_days=8):
    """
    WF02 — Outreach Multi-Touch
    1. Warm profile
    2. Send connection
    3. Poll acceptance (every 4h, max 8 days)
    4. Send DM on acceptance
    """
    # Étape 1: Warm
    call_bereach("/visit/linkedin/profile", {"profile": prospect_url})
    import time; time.sleep(60)
    
    # Étape 2: Connect
    connect_result = call_bereach("/connect/linkedin/profile", {
        "profile": prospect_url,
        "message": generate_connect_message(prospect_url, offer_context)
    })
    
    if not connect_result.get("success"):
        return {"error": "connection_failed"}
    
    # Étape 3: Poll (schedule for later)
    # En pratique: cron job qui vérifie toutes les 4h
    # Si accepted → trigger DM
    
    return {
        "status": "pending_acceptance",
        "check_again_in": "4h"
    }

def on_connection_accepted(prospect_url, conversation_urn, offer_context):
    """Callback quand la connexion est acceptée."""
    # Étape 4: Send DM
    dm_result = call_bereach("/message/linkedin", {
        "conversationUrn": conversation_urn,
        "message": generate_dm_message(prospect_url, offer_context)
    })
    
    return dm_result
```

---

## Limites LinkedIn (sans Sales Nav)

| Action | Limite/jour |
|--------|-------------|
| Demandes de connexion | 30 |
| Messages InMail | N/A (nécessite Sales Nav) |
| Messages à ses connections | Illimité |

---

## Pièges

1. **Trop de demandes simultanées** — LinkedIn peut limiter votre compte. Espacer les demandes de 30-60 min.
2. **Message de connexion = premier contact** — Il doit être parfait (cf. règles ci-dessus).
3. **DM sans connexion acceptée** — Impossible via BeReach. Il faut attendre l'acceptation.
4. **Seuil de 5,000 connexions** — Si vous atteignez 5,000 connections, les demandes sont bridées.