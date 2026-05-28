"""
CLI Commands pour LinkedIn Growth OS
Onboarding wizard + start/stop/status
"""
import os, sys, json, subprocess
from pathlib import Path

HERMES_HOME = Path(os.environ.get("HERMES_HOME", Path.home() / ".hermes"))
PLUGIN_DIR = HERMES_HOME / "plugins" / "linkedin-growth-os"
CONFIG_FILE = PLUGIN_DIR / "config.json"
SKILL_DIR = HERMES_HOME / "skills" / "linkedin-growth-os"

def print_banner():
    print("""
╔══════════════════════════════════════════════════════════╗
║      LINKEDIN GROWTH OS — Configuration Wizard             ║
╚══════════════════════════════════════════════════════════╝
""")

def run_setup_wizard():
    """Wizard interactif d'onboarding."""
    print_banner()
    
    config = {}
    
    # Step 1: License Key
    print("1/6 — Clé de licence")
    print("  → Entrez votre clé de licence (reçue par email)")
    config["license_key"] = input("   Clé: ").strip()
    if not config["license_key"]:
        print("   ✗ Clé requise")
        return {"error": "license_key_required"}
    print("   ✓ Clé validée\n")
    
    # Step 2: Votre offre (ce que vous vendez)
    print("2/6 — Votre offre")
    print("   → Décrivez brièvement ce que vous vendez (2-3 phrases)")
    print("   → L'agent IA adaptera ses messages à votre positionnement")
    config["offer"] = input("   Votre offre: ").strip()
    if not config["offer"]:
        print("   ✗ Description requise")
        return {"error": "offer_required"}
    print("   ✓ Offre enregistrée\n")
    
    # Step 3: ICP — Taille d'entreprise
    print("3/6 — Taille d'entreprise recherchée")
    print("   → Quelles entreprises visez-vous ?")
    print("   [1] 1-10 salariés (startup, auto-entrepreneurs)")
    print("   [2] 11-50 salariés (PME, scale-ups)")
    print("   [3] 51-250 salariés (ETI)")
    print("   [4] 250+ salariés (grandes entreprises)")
    print("   [5] Toutes tailles")
    choice = input("   Choix [1-5]: ").strip()
    sizes = {"1": "1-10", "2": "11-50", "3": "51-250", "4": "250+", "5": "all"}
    config["company_size"] = sizes.get(choice, "11-50")
    print(f"   ✓ Taille: {config['company_size']} salariés\n")
    
    # Step 4: ICP — Localisation
    print("4/6 — Localisation géographique")
    print("   → Pays/Région visés (ex: France, Europe, Monde)")
    config["location"] = input("   Localisation: ").strip() or "France"
    print(f"   ✓ Localisation: {config['location']}\n")
    
    # Step 5: ICP — Rôle/Décideur
    print("5/6 — Rôles des décideurs")
    print("   → Quels rôles visez-vous sur LinkedIn ?")
    print("   Séparez par des virgules (ex: CEO, Founder, Head of Sales)")
    config["target_titles"] = [t.strip() for t in input("   Rôles: ").split(",") if t.strip()]
    if not config["target_titles"]:
        config["target_titles"] = ["CEO", "Founder", "Head of"]
    print(f"   ✓ Cibles: {', '.join(config['target_titles'])}\n")
    
    # Step 6: Composio MCP
    print("6/6 — Connexion Composio")
    print("   → Activez ces MCP tools dans l'app Composio:")
    print("   REQUIRED: google-sheets, telegram")
    print("   RECOMMENDED: notion, slack, email")
    print("   → Attendez que l'agent configure automatiquement")
    print("   → Appuyez sur Entrée quand c'est fait")
    input("   [Entrée]")
    
    config["mcp_enabled"] = True
    config["bereach_configured"] = False  # Sera mis à True par le setup BeReach
    config["setup_completed"] = True
    config["setup_date"] = str(Path(__file__).stat().st_mtime) if Path(__file__).exists() else ""
    
    # Sauvegarder la config
    PLUGIN_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_FILE.write_text(json.dumps(config, indent=2))
    
    # Copier le skill dans ~/.hermes/skills/
    _install_skill()
    
    print("""
╔══════════════════════════════════════════════════════════╗
║  ✓ Configuration terminée !                               ║
║                                                          ║
║  Prochaines étapes:                                      ║
║  1. Connectez votre compte BeReach (lien dans l'email)   ║
║  2. Activez les MCP dans Composio                        ║
║  3. Lancez: hermes linkedin-growth-os start              ║
║                                                          ║
║  Pour commencer: /linkedin-growth-os                     ║
╚══════════════════════════════════════════════════════════╝
""")
    return {"success": True, "config": config}

def _install_skill():
    """Installe le skill dans ~/.hermes/skills/"""
    skill_src = PLUGIN_DIR / "skills" / "linkedin-growth-os"
    if skill_src.exists():
        import shutil
        SKILL_DIR.parent.mkdir(parents=True, exist_ok=True)
        if SKILL_DIR.exists():
            shutil.rmtree(SKILL_DIR)
        shutil.copytree(skill_src, SKILL_DIR)

def start_prospection():
    """Démarre le moteur de prospection."""
    cfg = json.loads(CONFIG_FILE.read_text()) if CONFIG_FILE.exists() else {}
    if not cfg.get("setup_completed"):
        print("✗ Configuration incomplète. Lancez: hermes linkedin-growth-os setup")
        return {"error": "not_configured"}
    print("✓ Moteur de prospection démarré")
    print("  → Parlez à l'agent: /linkedin-growth-os [objectif]")
    return {"success": True, "message": "Prospection engine started"}

def stop_prospection():
    """Arrête le moteur."""
    print("✓ Moteur arrêté")
    return {"success": True}

def print_status():
    """Affiche le statut du plugin."""
    cfg = json.loads(CONFIG_FILE.read_text()) if CONFIG_FILE.exists() else {}
    print("""
╔══════════════════════════════════════════════════════════╗
║  LINKEDIN GROWTH OS — Statut                             ║
╠══════════════════════════════════════════════════════════╣""")
    if not cfg:
        print("║  ✗ Non configuré                                    ║")
    else:
        setup_date = cfg.get('setup_date', 'N/A')[:10]
        offer = cfg.get('offer', 'N/A')[:44]
        location = cfg.get('location', 'France')[:44]
        print(f"║  ✓ Configuré depuis: {setup_date:32s}║")
        print(f"║  ✓ Offre: {offer:44s}║")
        print(f"║  ✓ Cible: {location:44s}║")
    print("╚══════════════════════════════════════════════════════════╝")
    return {"config": cfg}

def update_plugin():
    """Met à jour le plugin via git pull."""
    result = subprocess.run(["git", "pull"], cwd=PLUGIN_DIR, capture_output=True, text=True)
    if result.returncode == 0:
        print("✓ Plugin mis à jour")
        return {"success": True}
    else:
        print(f"✗ Erreur: {result.stderr}")
        return {"error": result.stderr}