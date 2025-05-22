import sys
import time
from pathlib import Path

# Imports de vos modules
from scraper.e_commerce_scraper import EcommerceScraper
from scraper.bource_scraper import BourseScraper
from scraper.news_scraper import NewsScraper
from utils.exporter import export_data
from utils.cleaner import DataCleaner
from utils.robot_check import is_scraping_allowed

class ScrapingManager:
    """Gestionnaire principal pour le scraping avec options avancées"""
    
    def __init__(self):
        self.scrapers = {
            "ecommerce": EcommerceScraper,
            "bourse": BourseScraper,
            "news": NewsScraper
        }
        self.formats_supportes = ["csv", "json", "xlsx", "pdf"]
    
    def choisir_scraper(self, type_site, url):
        """Factory pattern pour créer le bon scraper"""
        if type_site not in self.scrapers:
            raise ValueError(f"Type de site '{type_site}' non reconnu. Types disponibles : {list(self.scrapers.keys())}")
        
        # Détecter des sites spécifiques pour utiliser des scrapers optimisés
        if type_site == "bourse":
            if "yahoo" in url.lower():
                from scraper.bource_scraper import YahooFinanceScraper
                return YahooFinanceScraper(url)
            elif "bloomberg" in url.lower():
                from scraper.bource_scraper import BloombergScraper
                return BloombergScraper(url)
            elif "marketwatch" in url.lower():
                from scraper.bource_scraper import MarketwatchScraper
                return MarketwatchScraper(url)
        
        return self.scrapers[type_site](url)
    
    def verifier_robots_txt(self, url, force=False):
        """Vérifie robots.txt avec option de forçage"""
        if force:
            print("⚠️ Vérification robots.txt ignorée (mode forcé)")
            return True
            
        try:
            if not is_scraping_allowed(url):
                print("🚫 Le scraping de ce site n'est pas autorisé selon robots.txt")
                
                choix = input("Voulez-vous continuer quand même ? (y/N): ").strip().lower()
                if choix in ['y', 'yes', 'oui', 'o']:
                    print("⚠️ Scraping en mode non-conforme à robots.txt")
                    return True
                else:
                    return False
            else:
                print("✅ Scraping autorisé par robots.txt")
                return True
                
        except Exception as e:
            print(f"⚠️ Impossible de vérifier robots.txt ({e}). Continuation...")
            return True
    
    def scraper_avec_options(self, scraper, options=None):
        """Lance le scraping avec des options avancées"""
        if options is None:
            options = {}
        
        print("🚀 Début du scraping...")
        start_time = time.time()
        
        try:
            # Options de scraping avancées
            if options.get('stealth_mode', False):
                print("🥷 Mode furtif activé")
                scraper.enable_stealth_mode()
            
            if options.get('delay', 0) > 0:
                print(f"⏱️ Délai entre requêtes : {options['delay']}s")
                scraper.set_delay(options['delay'])
            
            if options.get('user_agent'):
                print(f"🔧 User-Agent personnalisé : {options['user_agent'][:50]}...")
                scraper.set_user_agent(options['user_agent'])
            
            # Lancement du scraping
            data = scraper.scrape()
            
            elapsed_time = time.time() - start_time
            print(f"✅ Scraping terminé en {elapsed_time:.2f}s")
            
            return data
            
        except Exception as e:
            print(f"❌ Erreur lors du scraping : {e}")
            return None
    
    def nettoyer_donnees(self, data, site_type, options_nettoyage=None):
        """Nettoie les données avec options personnalisables"""
        if not data:
            return data
        
        print("🧹 Nettoyage des données...")
        
        try:
            cleaner = DataCleaner(site_type=site_type)
            
            if options_nettoyage:
                cleaner.configure(options_nettoyage)
            
            cleaned_data = cleaner.clean(data)
            print(f"✅ {len(cleaned_data)} éléments nettoyés")
            
            return cleaned_data
            
        except Exception as e:
            print(f"⚠️ Erreur lors du nettoyage : {e}")
            return data  # Retourner les données brutes en cas d'erreur
    
    def exporter_donnees(self, data, filename, format_choisi, options_export=None):
        """Exporte les données avec gestion d'erreurs améliorée"""
        if not data:
            print("❌ Aucune donnée à exporter")
            return False
        
        if format_choisi not in self.formats_supportes:
            print(f"❌ Format '{format_choisi}' non supporté. Formats disponibles : {self.formats_supportes}")
            return False
        
        try:
            # Créer le dossier de sortie si nécessaire
            output_dir = Path("output")
            output_dir.mkdir(exist_ok=True)
            
            filepath = output_dir / f"{filename}.{format_choisi}"
            
            export_data(data, str(filepath.stem), format_choisi, options_export)
            
            print(f"✅ Données exportées : {filepath}")
            print(f"📊 {len(data)} éléments exportés")
            
            return True
            
        except Exception as e:
            print(f"❌ Erreur lors de l'export : {e}")
            return False

def interface_utilisateur():
    """Interface utilisateur interactive"""
    manager = ScrapingManager()
    
    print("=" * 60)
    print("🕷️  SCRAPER UNIVERSEL")
    print("=" * 60)
    
    # Configuration du scraping
    print("\n📋 CONFIGURATION")
    print(f"Types de sites : {' | '.join(manager.scrapers.keys())}")
    type_site = input("Type de site à scraper : ").strip().lower()
    
    if type_site not in manager.scrapers:
        print(f"❌ Type '{type_site}' non reconnu")
        return
    
    url = input("URL du site : ").strip()
    if not url:
        print("❌ URL requise")
        return
    
    # Options avancées
    print("\n⚙️ OPTIONS AVANCÉES (optionnel)")
    
    force_scraping = input("Ignorer robots.txt ? (y/N): ").strip().lower() in ['y', 'yes', 'oui', 'o']
    
    stealth_mode = input("Mode furtif ? (y/N): ").strip().lower() in ['y', 'yes', 'oui', 'o']
    
    try:
        delay = float(input("Délai entre requêtes (secondes, 0 par défaut): ") or "0")
    except ValueError:
        delay = 0
    
    nettoyer = input("Nettoyer les données ? (Y/n): ").strip().lower() not in ['n', 'no', 'non']
    
    # Configuration export
    print(f"\n📤 EXPORT")
    print(f"Formats disponibles : {' | '.join(manager.formats_supportes)}")
    format_choisi = input("Format de sortie : ").strip().lower()
    filename = input("Nom du fichier (sans extension) : ").strip()
    
    if not filename:
        filename = f"scraping_{type_site}_{int(time.time())}"
    
    # Vérification robots.txt
    if not manager.verifier_robots_txt(url, force=force_scraping):
        print("🛑 Scraping annulé")
        return
    
    # Configuration des options
    options_scraping = {
        'stealth_mode': stealth_mode,
        'delay': delay,
        'user_agent': None  # Peut être étendu
    }
    
    # Exécution du scraping
    print("\n" + "=" * 60)
    
    try:
        scraper = manager.choisir_scraper(type_site, url)
        data = manager.scraper_avec_options(scraper, options_scraping)
        
        if not data:
            print("❌ Aucune donnée récupérée")
            return
        
        # Nettoyage optionnel
        if nettoyer:
            data = manager.nettoyer_donnees(data, type_site)
        
        # Export
        success = manager.exporter_donnees(data, filename, format_choisi)
        
        if success:
            print("\n🎉 Scraping terminé avec succès !")
        else:
            print("\n❌ Échec de l'export")
            
    except Exception as e:
        print(f"\n💥 Erreur fatale : {e}")

def mode_commande():
    """Mode ligne de commande pour l'automatisation"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Scraper universel")
    parser.add_argument("type", choices=["ecommerce", "bourse", "news"], help="Type de site")
    parser.add_argument("url", help="URL à scraper")
    parser.add_argument("-o", "--output", default="output", help="Nom du fichier de sortie")
    parser.add_argument("-f", "--format", choices=["csv", "json", "xlsx", "pdf"], default="json", help="Format de sortie")
    parser.add_argument("--force", action="store_true", help="Ignorer robots.txt")
    parser.add_argument("--stealth", action="store_true", help="Mode furtif")
    parser.add_argument("--delay", type=float, default=0, help="Délai entre requêtes")
    parser.add_argument("--no-clean", action="store_true", help="Ne pas nettoyer les données")
    
    args = parser.parse_args()
    
    manager = ScrapingManager()
    
    # Vérification robots.txt
    if not manager.verifier_robots_txt(args.url, force=args.force):
        return
    
    # Options
    options_scraping = {
        'stealth_mode': args.stealth,
        'delay': args.delay
    }
    
    try:
        scraper = manager.choisir_scraper(args.type, args.url)
        data = manager.scraper_avec_options(scraper, options_scraping)
        
        if data and not args.no_clean:
            data = manager.nettoyer_donnees(data, args.type)
        
        if data:
            manager.exporter_donnees(data, args.output, args.format)
    
    except Exception as e:
        print(f"Erreur : {e}")
        sys.exit(1)

def main():
    """Point d'entrée principal"""
    if len(sys.argv) > 1:
        # Mode ligne de commande
        mode_commande()
    else:
        # Mode interactif
        interface_utilisateur()

if __name__ == "__main__":
    main()