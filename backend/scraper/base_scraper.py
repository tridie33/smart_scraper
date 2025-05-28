# scraper/base_scraper.py

import urllib.request
import urllib.parse
from urllib.error import URLError, HTTPError
from bs4 import BeautifulSoup
import time
import random
import requests
from fake_useragent import UserAgent

class BaseScraper:
    def __init__(self, site_url, user_agent=None):
        self.site_url = site_url
        self.base_user_agent = user_agent or 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        self.current_user_agent = self.base_user_agent
        
        # Options pour le mode furtif
        self.stealth_mode = False
        self.delay = 0
        self.session = requests.Session()
        self.ua_generator = None
        
        # Initialiser fake_useragent si disponible
        try:
            self.ua_generator = UserAgent()
        except:
            self.ua_generator = None
        
        # Headers par défaut pour paraître plus humain
        self.default_headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'fr-FR,fr;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0'
        }
    
    def enable_stealth_mode(self):
        """Active le mode furtif"""
        self.stealth_mode = True
        print("🥷 Mode furtif activé")
        
        # Utiliser une session pour maintenir les cookies
        self.session.headers.update(self.default_headers)
        
        # Ajouter un referer réaliste
        parsed_url = urllib.parse.urlparse(self.site_url)
        self.session.headers['Referer'] = f"https://www.google.com/search?q={parsed_url.netloc}"
    
    def set_delay(self, delay):
        """Définit le délai entre les requêtes"""
        self.delay = delay
        print(f"⏱️ Délai configuré : {delay}s")
    
    def set_user_agent(self, user_agent):
        """Définit un User-Agent personnalisé"""
        self.current_user_agent = user_agent
        self.session.headers['User-Agent'] = user_agent
        print(f"🔧 User-Agent configuré")
    
    def get_random_user_agent(self):
        """Génère un User-Agent aléatoire"""
        if self.ua_generator and self.stealth_mode:
            try:
                return self.ua_generator.random
            except:
                pass
        
        # Fallback avec une liste prédéfinie
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:121.0) Gecko/20100101 Firefox/121.0'
        ]
        return random.choice(user_agents)
    
    def apply_delay(self):
        """Applique un délai avant la requête"""
        if self.delay > 0:
            if self.stealth_mode:
                # Délai aléatoire en mode furtif
                actual_delay = self.delay + random.uniform(-0.5, 1.0)
                actual_delay = max(0.1, actual_delay)  # Minimum 0.1s
            else:
                actual_delay = self.delay
            
            time.sleep(actual_delay)
    
    def get_html_urllib(self):
        """Méthode originale avec urllib (fallback)"""
        try:
            headers = {'User-Agent': self.current_user_agent}
            req = urllib.request.Request(self.site_url, headers=headers)
            
            with urllib.request.urlopen(req, timeout=30) as response:
                return response.read()
                
        except HTTPError as e:
            print(f"[HTTPError] {e.code} - {e.reason}")
        except URLError as e:
            print(f"[URLError] {e.reason}")
        except Exception as e:
            print(f"[Exception] {str(e)}")
        return None
    
    def get_html_requests(self):
        """Méthode améliorée avec requests et mode furtif"""
        try:
            # Appliquer le délai
            self.apply_delay()
            
            # Headers dynamiques en mode furtif
            if self.stealth_mode:
                self.session.headers['User-Agent'] = self.get_random_user_agent()
            else:
                self.session.headers['User-Agent'] = self.current_user_agent
            
            # Faire la requête
            response = self.session.get(
                self.site_url,
                timeout=30,
                allow_redirects=True
            )
            
            response.raise_for_status()  # Lève une exception pour les codes d'erreur HTTP
            
            return response.content
            
        except requests.exceptions.HTTPError as e:
            print(f"[HTTPError] {e.response.status_code} - {e}")
        except requests.exceptions.ConnectionError as e:
            print(f"[ConnectionError] {e}")
        except requests.exceptions.Timeout as e:
            print(f"[Timeout] {e}")
        except requests.exceptions.RequestException as e:
            print(f"[RequestException] {e}")
        except Exception as e:
            print(f"[Exception] {str(e)}")
        return None
    
    def get_html(self):
        """Point d'entrée principal pour récupérer le HTML"""
        if self.stealth_mode:
            return self.get_html_requests()
        else:
            # Essayer d'abord avec requests, fallback sur urllib
            html = self.get_html_requests()
            if html is None:
                print("🔄 Tentative avec urllib...")
                html = self.get_html_urllib()
            return html
    
    def get_soup(self):
        """Récupère et parse le HTML avec BeautifulSoup"""
        html = self.get_html()
        if html:
            try:
                return BeautifulSoup(html, 'html.parser')
            except Exception as e:
                print(f"[BeautifulSoup Error] {e}")
                return None
        return None
    
    def scrape(self):
        """Méthode abstraite à implémenter dans les classes filles"""
        raise NotImplementedError("La méthode `scrape` doit être définie dans la classe fille.")
    
    def test_connection(self):
        """Teste la connexion au site"""
        print(f"🔍 Test de connexion à {self.site_url}")
        
        html = self.get_html()
        if html:
            print(f"✅ Connexion réussie ({len(html)} bytes récupérés)")
            return True
        else:
            print("❌ Échec de la connexion")
            return False
    
    def get_response_info(self):
        """Récupère des informations sur la réponse (en mode requests)"""
        if hasattr(self.session, 'cookies') and self.session.cookies:
            print(f"🍪 Cookies reçus : {len(self.session.cookies)}")
        
        # Faire une requête HEAD pour obtenir les headers
        try:
            response = self.session.head(self.site_url, timeout=10)
            print(f"📊 Status: {response.status_code}")
            print(f"📋 Headers reçus : {len(response.headers)}")
            
            # Headers intéressants
            interesting_headers = ['server', 'x-powered-by', 'cloudflare-ray-id', 'cf-ray']
            for header in interesting_headers:
                if header in response.headers:
                    print(f"   {header}: {response.headers[header]}")
                    
        except Exception as e:
            print(f"⚠️ Impossible d'obtenir les infos de réponse : {e}")

    def save_html_debug(self, filename="debug.html"):
        """Sauvegarde le HTML pour débogage"""
        html = self.get_html()
        if html:
            with open(filename, 'wb') as f:
                f.write(html)
            print(f"💾 HTML sauvegardé dans {filename}")
        else:
            print("❌ Aucun HTML à sauvegarder")