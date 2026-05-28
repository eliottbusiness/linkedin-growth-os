# WF06 — Hiring Signal Detector

## Objectif

Détecter les entreprises qui recrutent activement (signal fort de croissance = budget disponible pour de nouveaux outils). Exploite les offres d'emploi LinkedIn pour identifier des opportunités commerciales.

**Credits estimés:** 4-7 par entreprise ciblée

---

## Architecture

```
SEARCH_JOBS → VISIT_COMPANY → FIND_DECISION_MAKERS → ENRICH_DECISION_MAKER
   (1 crédit)      (1 crédit)         (1 crédit)           (1 crédit)
```

---

## Étape 1 — SEARCH_JOBS

Rechercher les offres d'emploi récentes dans un secteur.

### Endpoint
```
POST https://api.bereach.ai/search/linkedin/jobs
```

### Request Body
```json
{
  "keywords": ["SDR", "Business Developer", "Account Executive", "Head of Sales"],
  "location": ["France"],
  "count": 20
}
```

### Response
```json
{
  "jobs": [
    {
      "jobUrl": "https://www.linkedin.com/jobs/view/sdr-head-of-sales-at-techcorp-123",
      "title": "Head of Sales",
      "companyName": "TechCorp",
      "companyUrl": "https://www.linkedin.com/company/techcorp",
      "location": "Paris, France",
      "postedAt": "2026-05-15T00:00:00Z",
      "applicantsCount": 24,
      "workplaceType": "Hybrid"
    }
  ]
}
```

### Filtres de qualification
```python
HIRING_SIGNALS = {
    "high_priority": ["head of", "director", "vp", "chief", "founder"],
    "growth_signals": ["scale", "growth", " Series A", "Series B", " Series C"],
    "volume": 3  # Minimum de postes ouverts pour signal fort
}

def qualify_hiring_signal(jobs_by_company):
    """
    Retourne les entreprises avec un signal de recrutement fort.
    """
    results = []
    
    for company_name, jobs in jobs_by_company.items():
        # Ignorer si < 3 postes ouverts
        if len(jobs) < HIRING_SIGNALS["volume"]:
            continue
        
        # Vérifier les rôles à haute priorité
        high_priority_jobs = [
            j for j in jobs 
            if any(kw in j["title"].lower() 
                  for kw in HIRING_SIGNALS["high_priority"])
        ]
        
        # Vérifier les signaux de croissance
        growth_keywords = HIRING_SIGNALS["growth_signals"]
        
        results.append({
            "company": company_name,
            "jobs": jobs,
            "high_priority_count": len(high_priority_jobs),
            "total_jobs": len(jobs),
            "signal": "high" if len(high_priority_jobs) >= 2 else "medium",
            "reason": f"{len(jobs)} postes ouverts, {len(high_priority_jobs)} rôles clés"
        })
    
    return sorted(results, key=lambda x: x["high_priority_count"], reverse=True)
```

---

## Étape 2 — VISIT_COMPANY

Enrichir l'entreprise qui recrute.

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
  "founded": "2020",
  "description": "SaaS B2B pour les équipes commerciales...",
  "specialities": "CRM, Sales Automation, Analytics"
}
```

### Scoring de l'opportunité
```python
def score_company_opportunity(company_data, jobs):
    """
    Score basé sur la taille et le volume de recrutement.
    """
    size = company_data.get("employeeCount", "1-10")
    
    size_map = {
        "1-10": 10, "11-50": 20, "51-200": 40,
        "201-500": 60, "501-1000": 80, "1000+": 100
    }
    size_score = size_map.get(size, 20)
    
    # Plus ils recrutent, plus le signal est fort
    hiring_score = min(len(jobs) * 10, 50)
    
    # Industrie tech = plus susceptible d'adopter des outils
    industry_bonus = 20 if "technology" in company_data.get("industry", "").lower() else 0
    
    return {
        "opportunity_score": size_score + hiring_score + industry_bonus,
        "company_size": size,
        "hiring_volume": len(jobs),
        "recommended_action": "priority_outreach" if size_score >= 40 else "standard_outreach"
    }
```

---

## Étape 3 — FIND_DECISION_MAKERS

Trouver les décideurs dans l'entreprise.

### Endpoint
```
POST https://api.bereach.ai/search/linkedin/people
```

### Request Body
```json
{
  "company": "TechCorp",
  "title": ["CEO", "Founder", "Head of", "Director", "VP"],
  "location": ["France"],
  "count": 10
}
```

### Response
```json
{
  "items": [
    {
      "profileUrl": "https://www.linkedin.com/in/ceo-techcorp/",
      "headline": "CEO & Co-Founder @TechCorp",
      "firstName": "Pierre",
      "lastName": "Durand",
      "memberDistance": "F"
    }
  ],
  "total": 3,
  "hasMore": false
}
```

### Titres décideurs prioritaires
```python
DECISION_MAKER_TITLES = [
    "ceo", "founder", "co-founder", "cto", "cfo", "coo",
    "head of", "director", "vp", "vice president",
    "chief", "managing director", "president"
]

def is_decision_maker(title):
    """Retourne True si le titre indique un décideur."""
    t = title.lower()
    return any(kw in t for kw in DECISION_MAKER_TITLES)
```

---

## Étape 4 — ENRICH_DECISION_MAKER

Enrichir le profil du décideur.

### Endpoint
```
POST https://api.bereach.ai/visit/linkedin/profile
```

### Request Body
```json
{
  "profile": "https://www.linkedin.com/in/ceo-techcorp/"
}
```

### Response
```json
{
  "id": "pd123",
  "firstName": "Pierre",
  "lastName": "Durand",
  "headline": "CEO & Co-Founder @TechCorp",
  "summary": "Ex-Google, serial entrepreneur...",
  "email": "pierre@techcorp.com",
  "positions": [
    {
      "company": "TechCorp",
      "companyUrl": "https://www.linkedin.com/company/techcorp",
      "title": "CEO & Co-Founder"
    }
  ]
}
```

---

## Pipeline complet

```python
def run_wf06(industry_keywords, location="France", limit=10):
    """
    WF06 — Hiring Signal Detector
    """
    results = []
    
    # Étape 1: Rechercher les offres
    jobs = call_bereach("/search/linkedin/jobs", {
        "keywords": industry_keywords,
        "location": [location],
        "count": 30
    }).get("jobs", [])
    
    # Grouper par entreprise
    from collections import defaultdict
    jobs_by_company = defaultdict(list)
    for job in jobs:
        jobs_by_company[job["companyName"]].append(job)
    
    # Étape 2: Qualifier les signaux
    companies = qualify_hiring_signal(jobs_by_company)
    
    for company_info in companies[:limit]:
        company_name = company_info["company"]
        jobs_list = company_info["jobs"]
        
        # Visiter l'entreprise
        company_data = call_bereach("/visit/linkedin/company", {
            "companyUrl": jobs_list[0]["companyUrl"]
        })
        
        # Trouver les décideurs
        decision_makers = call_bereach("/search/linkedin/people", {
            "company": company_name,
            "title": DECISION_MAKER_TITLES,
            "location": [location],
            "count": 5
        }).get("items", [])
        
        for dm in decision_makers:
            # Enrichir le décideur
            profile_data = call_bereach("/visit/linkedin/profile", {
                "profile": dm["profileUrl"]
            })
            
            # Scorer l'opportunité
            opportunity = score_company_opportunity(company_data, jobs_list)
            
            results.append({
                "company": company_data,
                "decision_maker": profile_data,
                "jobs": jobs_list,
                "opportunity": opportunity,
                "signal": company_info["signal"]
            })
        
        import time; time.sleep(3)
    
    return results
```

---

## Angle de prospection

```
Sujet: Félitations pour la croissance {Company} !

Message:
[Prenom],

J'ai vu que {Company} recrute {N} personnes en ce moment — dont {TopJob}. 
C'est un signal de croissance impressive !

Beaucoup d'entreprises en hyper-croissance nous contactent pour résoudre 
le même probleme: comment absorber cette croissance sans exploser les coûts 
commerciaux.

On a accompagné {SimilarCompany} ( même secteur, même taille ) à:
→ Doubler leur pipeline en 3 mois
→ Reduire le coût d'acquisition de 35%

Tu aurais 15 min cette semaine pour qu'on échange sur vos enjeux ?

[Votre nom]
```

---

## Pièges

1. **Jobs trop anciens** — Vérifier `postedAt` (max 30 jours).
2. **Startups trop petites** — Une entreprise de 3 personnes qui recrute un dév ne signe pas pour 197€/mois.
3. **Jobs génériques** — Les offres "Account Manager" массовый ne sont pas des signaux de croissance. Focus sur les rôles commerciaux clés.
4. **CDI vs Stage** — Privilégier les offres CDI pour les signaux budget réel.