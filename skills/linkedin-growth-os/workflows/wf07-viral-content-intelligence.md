# WF07 — Viral Content Intelligence Engine

## Objectif

Analyser les contenus LinkedIn viraux dans votre secteur pour en extraire les patterns gagnants (hooks, structures, émotions, CTA). Permet de comprendre ce qui fonctionne et de reproduire ces patterns.

**Credits estimés:** 3-5 par analyse

---

## Architecture

```
SEARCH_VIRAL_POSTS → COLLECT_COMMENTS → COLLECT_LIKES → ANALYZE_PERFORMANCE → AI_PATTERN_ANALYSIS
   (1 crédit)          (1 crédit)         (1 crédit)        (1 crédit)            (gratuit)
```

---

## Étape 1 — SEARCH_VIRAL_POSTS

Trouver les posts viraux dans un secteur.

### Endpoint
```
POST https://api.bereach.ai/search/linkedin/posts
```

### Request Body
```json
{
  "keywords": ["SaaS", "B2B", "sales", "croissance", "entrepreneur"],
  "count": 20
}
```

### Response
```json
{
  "posts": [
    {
      "postUrl": "https://www.linkedin.com/posts/activity_xyz789",
      "text": "3 leçons que j'aurais aimé connaître avant de lancer mon SaaS...",
      "authorName": "Marie Laurent",
      "authorUrl": "https://www.linkedin.com/in/marie-laurent/",
      "postedAt": "2026-05-20T10:00:00Z",
      "likesCount": 1247,
      "commentsCount": 89,
      "sharesCount": 34
    }
  ]
}
```

### Filtres de viralité
```python
def filter_viral_posts(posts, min_engagement=200):
    """
    Filtre les posts viraux (engagement >= min_engagement).
    """
    viral = []
    for post in posts:
        engagement = (post.get("likesCount", 0) + 
                     post.get("commentsCount", 0) * 3 + 
                     post.get("sharesCount", 0) * 5)
        if engagement >= min_engagement:
            post["engagement"] = engagement
            viral.append(post)
    
    return sorted(viral, key=lambda x: x["engagement"], reverse=True)
```

---

## Étape 2 — COLLECT_COMMENTS

Collecter les commentaires pour analyser les réactions.

### Endpoint
```
POST https://api.bereach.ai/collect/linkedin/comments
```

### Request Body
```json
{
  "postUrl": "https://www.linkedin.com/posts/activity_xyz789",
  "count": 20
}
```

### Response
```json
{
  "profiles": [
    {
      "profileUrl": "https://www.linkedin.com/in/jean-martin/",
      "commentText": "Merci pour ces conseils précieux ! Je vais.apply de suite.",
      "commentUrn": "urn:li:comment:(activity:xyz,123456789)"
    }
  ]
}
```

### Analyse des commentaires
```python
def analyze_comments(comments):
    """
    Analyse les commentaires pour comprendre ce qui résonne.
    """
    sentiments = {"positive": 0, "neutral": 0, "question": 0}
    questions = []
    
    positive_kw = ["merci", "génial", "parfait", "excellent", "top", "bravo", "wow"]
    question_kw = ["comment", "pourquoi", "quel", "peut-on", "est-ce que", "how"]
    
    for comment in comments:
        text = comment.get("commentText", comment.get("comment", "")).lower()
        
        if any(kw in text for kw in question_kw):
            sentiments["question"] += 1
            questions.append(text[:100])
        elif any(kw in text for kw in positive_kw):
            sentiments["positive"] += 1
        else:
            sentiments["neutral"] += 1
    
    return {
        "sentiments": sentiments,
        "questions": questions[:5],  # Top 5 questions
        "total_comments": len(comments)
    }
```

---

## Étape 3 — COLLECT_LIKES

Analyser qui like (données démographiques).

### Endpoint
```
POST https://api.bereach.ai/collect/linkedin/likes
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
  "profiles": [
    {
      "profileUrl": "https://www.linkedin.com/in/jean-martin/",
      "likedAt": "2026-05-21T08:15:00Z"
    }
  ]
}
```

### Enrichir un échantillon de likers
```python
def analyze_likers_demographics(likers, sample_size=10):
    """
    Enrichit un échantillon de likers pour comprendre le public.
    """
    industries = []
    job_levels = []
    
    for liker in likers[:sample_size]:
        profile = call_bereach("/visit/linkedin/profile", {
            "profile": liker["profileUrl"]
        })
        
        headline = profile.get("headline", "")
        summary = profile.get("summary", "")
        
        # Extraire l'industrie
        if "tech" in headline.lower():
            industries.append("tech")
        elif "finance" in headline.lower():
            industries.append("finance")
        
        # Extraire le niveau
        if any(kw in headline for kw in ["ceo", "founder", "director", "vp"]):
            job_levels.append("senior")
        elif any(kw in headline for kw in ["manager", "lead"]):
            job_levels.append("mid")
        else:
            job_levels.append("junior")
    
    return {
        "top_industries": Counter(industries).most_common(3),
        "job_level_distribution": Counter(job_levels),
        "sample_size": sample_size
    }
```

---

## Étape 4 — ANALYZE_PERFORMANCE

Collecter les métriques complètes du post.

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
  "viewsCount": 45000,
  "likesCount": 1247,
  "commentsCount": 89,
  "sharesCount": 34,
  "engagementRate": 3.0,
  "impressions": 42000,
  "clickCount": 890
}
```

### Calcul du score de viralité
```python
def calculate_viral_score(analytics, post_text):
    """
    Score global de viralité avec bonus pour les patterns identifiés.
    """
    base_score = analytics.get("engagementRate", 0) * 10
    
    # Bonus pour les shares (amplification organique)
    shares_bonus = min(analytics.get("sharesCount", 0) * 2, 20)
    
    # Bonus pour la longueur du post (contenu approfondi)
    length = len(post_text)
    if 500 < length < 1500:
        length_bonus = 10  # Posts de longueur moyenne performent bien
    elif length > 2000:
        length_bonus = 5
    else:
        length_bonus = 0
    
    # Malus si trop de liens (LinkedIn penalise)
    links_bonus = -5 if post_text.count("http") > 2 else 0
    
    return min(base_score + shares_bonus + length_bonus + links_bonus, 100)
```

---

## Étape 5 — AI_PATTERN_ANALYSIS (Gratuit)

Analyser les patterns de contenu qui performent.

```python
PATTERNS = {
    "hooks": {
        "number_list": r"^\d+ ",
        "question": r"^[A-Z][^\?]*\?",
        "controversial": r"(attention|pire|erreur|méfie|mistake|warning)",
        "story": r"(j'ai|on a|ils ont|when I|we)",
    },
    "emotions": {
        "pride": ["fier", "réussi", "achieved", "proud"],
        "fear": ["attention", "pire", "danger", "risque", "warning"],
        "curiosity": ["savais-tu", "tu ne sais peut-être", "secret", "surprenant"],
        "hope": ["bientôt", "prochaine", "future", " upcoming"],
    },
    "cta": ["comment", "partage", "discutons", "appel", "démo", "télécharge"]
}

def analyze_content_patterns(post_text):
    """
    Extrait les patterns de contenu d'un post viral.
    """
    results = {
        "hook_type": None,
        "emotions_detected": [],
        "has_cta": False,
        "structure_type": None,
        "post_length": len(post_text),
        "has_numbers": bool(PATTERNS["hooks"]["number_list"].match(post_text[:10])),
        "has_emoji": "emoji" if any(c in post_text for c in "🔥💡🚀✅⚠️") else "none"
    }
    
    # Identifier le hook
    for hook_type, pattern in PATTERNS["hooks"].items():
        if re.match(pattern, post_text[:50]):
            results["hook_type"] = hook_type
            break
    
    # Identifier les émotions
    text_lower = post_text.lower()
    for emotion, keywords in PATTERNS["emotions"].items():
        if any(kw in text_lower for kw in keywords):
            results["emotions_detected"].append(emotion)
    
    # CTA
    if any(cta in text_lower for cta in PATTERNS["cta"]):
        results["has_cta"] = True
    
    # Structure
    if re.match(r"^\d+\.", post_text):
        results["structure_type"] = "numbered_list"
    elif "•" in post_text or "-" in post_text:
        results["structure_type"] = "bullet_points"
    elif "\n\n" in post_text:
        results["structure_type"] = "paragraphs"
    
    return results

def generate_content_recommendations(viral_posts_analysis):
    """
    Génère des recommandations de contenu basées sur l'analyse.
    """
    all_patterns = [p["pattern_analysis"] for p in viral_posts_analysis]
    
    # Trouver les patterns les plus fréquents
    hook_types = Counter(p["hook_type"] for p in all_patterns if p["hook_type"])
    emotions = Counter()
    for p in all_patterns:
        emotions.update(p["emotions_detected"])
    
    avg_length = sum(p["post_length"] for p in all_patterns) / len(all_patterns)
    
    recommendations = {
        "recommended_hook": hook_types.most_common(1)[0][0] if hook_types else "number_list",
        "top_emotions": [e[0] for e in emotions.most_common(2)],
        "optimal_length": int(avg_length),
        "include_cta": any(p["has_cta"] for p in all_patterns),
        "use_emoji": sum(1 for p in all_patterns if p["has_emoji"] != "none") / len(all_patterns) > 0.3
    }
    
    return recommendations
```

---

## Pipeline complet

```python
def run_wf07(industry_keywords, min_engagement=300, limit=10):
    """
    WF07 — Viral Content Intelligence
    """
    results = []
    
    # Étape 1: Trouver les posts viraux
    posts = call_bereach("/search/linkedin/posts", {
        "keywords": industry_keywords,
        "count": 20
    }).get("posts", [])
    
    # Filtrer par viralité
    viral_posts = filter_viral_posts(posts, min_engagement)[:limit]
    
    for post in viral_posts:
        post_url = post["postUrl"]
        
        # Étape 2: Collecter les commentaires
        comments = call_bereach("/collect/linkedin/comments", {
            "postUrl": post_url,
            "count": 20
        }).get("profiles", [])
        
        # Étape 3: Collecter les likes (uniquement si post très viral)
        likers = []
        if post.get("likesCount", 0) > 500:
            likers = call_bereach("/collect/linkedin/likes", {
                "postUrl": post_url
            }).get("profiles", [])[:20]
        
        # Étape 4: Analytics
        analytics = call_bereach("/analytics/linkedin/post", {
            "postUrl": post_url
        })
        
        # Étape 5: Pattern analysis
        pattern_analysis = analyze_content_patterns(post["text"])
        
        results.append({
            "post": post,
            "comments_analysis": analyze_comments(comments),
            "likers_demographics": analyze_likers_demographics(likers, sample_size=5) if likers else None,
            "analytics": analytics,
            "pattern_analysis": pattern_analysis,
            "viral_score": calculate_viral_score(analytics, post["text"])
        })
        
        import time; time.sleep(2)
    
    # Générer les recommandations globales
    recommendations = generate_content_recommendations(results)
    
    return {
        "analyzed_posts": results,
        "recommendations": recommendations
    }
```

---

## Output — Rapport de recommandations

```python
def generate_content_report(wf07_results):
    """
    Génère un rapport de recommandations de contenu.
    """
    recs = wf07_results["recommendations"]
    
    report = f"""
# 📊 Rapport Content Intelligence

## Patterns viraux identifiés

**Hook recommandé:** {recs['recommended_hook']}
**Émotions clés:** {', '.join(recs['top_emotions'])}
**Longueur optimale:** {recs['optimal_length']} caractères
**CTA:** {"Recommandé" if recs['include_cta'] else "Optionnel"}
**Emoji:** {"Recommandés" if recs['use_emoji'] else "Éviter"}

## Top 3 posts analysés

"""
    for i, r in enumerate(wf07_results["analyzed_posts"][:3], 1):
        report += f"""
### {i}. Score: {r['viral_score']}/100
- Hook: {r['pattern_analysis']['hook_type']}
- Emotions: {', '.join(r['pattern_analysis']['emotions_detected']) or 'Aucune détectée'}
- Engagement: {r['analytics']['engagementRate']}%
- Likes: {r['analytics']['likesCount']} | Comments: {r['analytics']['commentsCount']}
"""
    
    return report
```

---

## Pièges

1. **Posts trop anciens** — Analyser uniquement les posts < 60 jours (LinkedIn Algo change).
2. **Trop petit échantillon** — minimum 10 posts pour avoir des patterns fiables.
3. **Copier-coller** — Ne pas reproduire le contenu à l'identique. Utiliser les patterns, pas le texte.
4. **Plateformes différentes** — Un pattern qui marche sur LinkedIn peut ne pas marcher sur Twitter/X.