"""
LinkedIn Growth OS — Hermes Plugin v1.0.0
Prospection B2B automatisée via BeReach API
"""
import os, json, logging
from pathlib import Path

logger = logging.getLogger(__name__)

HERMES_HOME = Path(os.environ.get("HERMES_HOME", Path.home() / ".hermes"))
PLUGIN_CONFIG = HERMES_HOME / "plugins" / "linkedin-growth-os" / "config.json"
LICENSE_SERVER_URL = "https://license.deptflow.io/validate"  # à remplacer

def validate_license(key: str) -> dict:
    """Valide la license key auprès du serveur DeptFlow."""
    import urllib.request, urllib.error
    try:
        req = urllib.request.Request(
            LICENSE_SERVER_URL,
            json.dumps({"key": key}).encode(),
            {"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read())
    except Exception as e:
        logger.warning(f"License validation failed: {e}")
        return {"valid": False, "error": str(e)}

def load_config() -> dict:
    """Charge la config du plugin ou retourne un dict vide."""
    if PLUGIN_CONFIG.exists():
        return json.loads(PLUGIN_CONFIG.read_text())
    return {}

def save_config(cfg: dict):
    """Sauvegarde la config du plugin."""
    PLUGIN_CONFIG.parent.mkdir(parents=True, exist_ok=True)
    PLUGIN_CONFIG.write_text(json.dumps(cfg, indent=2))

def register(ctx):
    """注册插件 hook — appelé par Hermes au démarrage."""
    # Register CLI commands
    ctx.register_cli_command("linkedin-growth-os", "setup", cli_setup, 
                           "Configure LinkedIn Growth OS (ICP, license, composio)")
    ctx.register_cli_command("linkedin-growth-os", "start", cli_start,
                           "Démarrer la prospection automatique")
    ctx.register_cli_command("linkedin-growth-os", "stop", cli_stop,
                           "Arrêter la prospection")
    ctx.register_cli_command("linkedin-growth-os", "status", cli_status,
                           "Statut du plugin")
    ctx.register_cli_command("linkedin-growth-os", "update", cli_update,
                           "Mettre à jour le plugin")
    
    # Lifecycle hooks
    ctx.register_hook("on_session_start", on_session_start)
    ctx.register_hook("on_session_end", on_session_end)
    
    logger.info("LinkedIn Growth OS v1.0.0 registered")

def on_session_start(ctx):
    """Hook appelé au démarrage de chaque session."""
    cfg = load_config()
    if cfg.get("license_key"):
        result = validate_license(cfg["license_key"])
        if not result.get("valid"):
            logger.warning("License invalide ou expirée")

def on_session_end(ctx):
    """Hook appelé à la fin de chaque session."""
    pass

# --- CLI Commands ---

def cli_setup(args):
    """Lance le wizard d'onboarding."""
    from .cli import run_setup_wizard
    return run_setup_wizard()

def cli_start(args):
    """Démarre le moteur de prospection."""
    from .cli import start_prospection
    return start_prospection()

def cli_stop(args):
    """Arrête le moteur de prospection."""
    from .cli import stop_prospection
    return stop_prospection()

def cli_status(args):
    """Affiche le statut actuel."""
    from .cli import print_status
    return print_status()

def cli_update(args):
    """Met à jour le plugin vers la dernière version."""
    from .cli import update_plugin
    return update_plugin()