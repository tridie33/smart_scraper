# config/scraper_config.py
import json
from pathlib import Path

class ScrapingConfig:
    """Gestionnaire de configuration pour le scraping"""
    
    DEFAULT_CONFIG = {
        "general": {
            "respect_robots_txt": True,
            "default_delay": 1.0,
            "max_retries": 3,
            "timeout": 30,
            "output_directory": "output"
        },
        "stealth": {
            "rotate_user_agents": True,
            "use_proxies": False,
            "random_delays": True,
            "delay_range": [1, 3]
        },
        "cleaning": {
            "remove_html_tags": True,
            "normalize_whitespace": True,
            "remove_empty_fields": True,
            "convert_prices": True
        },
        "export": {
            "default_format": "json",
            "include_metadata": True,
            "compress_large_files": True
        },
        "user_agents": [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        ]
    }
    
    def __init__(self, config_file=None):
        self.config_file = Path(config_file) if config_file else Path("config/scraper_config.json")
        self.config = self.load_config()
    
    def load_config(self):
        """Charge la configuration depuis le fichier"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                # Fusionner avec la config par défaut
                return self.merge_configs(self.DEFAULT_CONFIG, loaded_config)
            except Exception as e:
                print(f"Erreur lors du chargement de la config : {e}")
                return self.DEFAULT_CONFIG.copy()
        else:
            return self.DEFAULT_CONFIG.copy()
    
    def save_config(self):
        """Sauvegarde la configuration"""
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=2, ensure_ascii=False)
    
    def merge_configs(self, default, loaded):
        """Fusionne deux configurations"""
        result = default.copy()
        for key, value in loaded.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key].update(value)
            else:
                result[key] = value
        return result
    
    def get(self, path, default=None):
        """Récupère une valeur de configuration avec chemin pointé"""
        keys = path.split('.')
        value = self.config
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        
        return value
    
    def set(self, path, value):
        """Définit une valeur de configuration"""
        keys = path.split('.')
        config_ref = self.config
        
        for key in keys[:-1]:
            if key not in config_ref:
                config_ref[key] = {}
            config_ref = config_ref[key]
        
        config_ref[keys[-1]] = value

# Exemple d'utilisation avec le script principal
def load_scraping_config():
    """Charge la configuration pour le scraping"""
    return ScrapingConfig()

# Exemple de fichier de configuration JSON à créer
EXAMPLE_CONFIG = {
    "general": {
        "respect_robots_txt": False,  # Ignorer robots.txt par défaut
        "default_delay": 2.0,
        "max_retries": 5
    },
    "stealth": {
        "rotate_user_agents": True,
        "random_delays": True,
        "delay_range": [2, 5]
    },
    "site_specific": {
        "ecommerce": {
            "delay": 1.5,
            "clean_prices": True
        },
        "news": {
            "delay": 0.5,
            "extract_dates": True
        }
    }
}