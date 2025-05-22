# scraper/bource_scraper.py

from scraper.base_scraper import BaseScraper
import re
from datetime import datetime

class BourseScraper(BaseScraper):
    def __init__(self, site_url, user_agent=None):
        super().__init__(site_url, user_agent)
        
        # Sélecteurs pour différents types de contenu financier
        self.selectors = {
            # Actualités financières
            'news_containers': [
                '.market-summary .item',
                '.news-item',
                '.article-item',
                '.financial-news-item',
                '[data-testid="news-item"]',
                '.story-item',
                '.headline-item'
            ],
            'news_title': [
                'h3', 'h2', 'h4', '.title', '.headline', 
                '.news-title', '[data-testid="headline"]',
                '.article-title', '.story-title'
            ],
            'news_description': [
                'p', '.description', '.summary', '.excerpt',
                '.news-summary', '.article-summary', '.lead'
            ],
            
            # Données de marché
            'market_data': [
                '.market-data', '.quote-summary', '.stock-info',
                '.market-summary', '.financial-data', '.ticker-data'
            ],
            'stock_name': [
                '.stock-name', '.company-name', '.ticker-name',
                '[data-field="name"]', '.symbol-name'
            ],
            'stock_price': [
                '.price', '.last-price', '.current-price',
                '[data-field="price"]', '.quote-price', '.value'
            ],
            'stock_change': [
                '.change', '.price-change', '.variation',
                '[data-field="change"]', '.delta', '.move'
            ],
            'stock_percent': [
                '.percent', '.percentage', '.change-percent',
                '[data-field="percent"]', '.pct-change'
            ]
        }
    
    def extract_price(self, price_text):
        """Extrait et nettoie les prix/valeurs financières"""
        if not price_text:
            return None
        
        # Nettoyer le texte
        price_clean = price_text.strip().replace(',', '').replace(' ', '')
        
        # Extraire les nombres avec décimales
        price_match = re.search(r'[\d]+[.,]?[\d]*', price_clean)
        if price_match:
            return price_match.group().replace(',', '.')
        
        return price_clean
    
    def extract_change(self, change_text):
        """Extrait les variations de prix"""
        if not change_text:
            return None, None
        
        change_clean = change_text.strip()
        
        # Chercher les variations absolues et en pourcentage
        abs_match = re.search(r'[+-]?[\d]+[.,]?[\d]*', change_clean)
        pct_match = re.search(r'[+-]?[\d]+[.,]?[\d]*%', change_clean)
        
        abs_change = abs_match.group().replace(',', '.') if abs_match else None
        pct_change = pct_match.group() if pct_match else None
        
        return abs_change, pct_change
    
    def find_elements_by_selectors(self, soup, selectors_list):
        """Trouve des éléments en essayant plusieurs sélecteurs"""
        for selector in selectors_list:
            elements = soup.select(selector)
            if elements:
                return elements
        return []
    
    def scrape_news(self, soup):
        """Scrape les actualités financières"""
        print("📰 Recherche d'actualités financières...")
        
        news_containers = self.find_elements_by_selectors(soup, self.selectors['news_containers'])
        
        if not news_containers:
            print("⚠️ Aucun conteneur d'actualités trouvé avec les sélecteurs standards")
            # Tentative de détection automatique
            news_containers = self.auto_detect_news(soup)
        
        actualites = []
        for i, item in enumerate(news_containers):
            try:
                # Extraire le titre
                title_element = None
                for selector in self.selectors['news_title']:
                    title_element = item.select_one(selector)
                    if title_element:
                        break
                
                titre = title_element.get_text(strip=True) if title_element else f"Actualité {i+1}"
                
                # Extraire la description
                desc_element = None
                for selector in self.selectors['news_description']:
                    desc_element = item.select_one(selector)
                    if desc_element:
                        break
                
                description = desc_element.get_text(strip=True) if desc_element else ""
                
                # Extraire des métadonnées supplémentaires
                date_element = item.select_one('.date, .timestamp, time, [datetime]')
                date_str = ""
                if date_element:
                    date_str = date_element.get_text(strip=True) or date_element.get('datetime', '')
                
                link_element = item.select_one('a')
                link = ""
                if link_element:
                    link = link_element.get('href', '')
                    if link and not link.startswith('http'):
                        # URL relative, construire l'URL complète
                        from urllib.parse import urljoin
                        link = urljoin(self.site_url, link)
                
                actualite = {
                    "titre": titre,
                    "description": description,
                    "date": date_str,
                    "lien": link,
                    "index": i + 1
                }
                
                actualites.append(actualite)
                
            except Exception as e:
                print(f"⚠️ Erreur lors de l'extraction de l'actualité {i+1}: {e}")
                continue
        
        return actualites
    
    def scrape_market_data(self, soup):
        """Scrape les données de marché/cotations"""
        print("📈 Recherche de données de marché...")
        
        market_containers = self.find_elements_by_selectors(soup, self.selectors['market_data'])
        
        if not market_containers:
            # Chercher des tableaux ou listes de cotations
            market_containers = soup.select('table tr, .quote-row, .stock-row')
        
        market_data = []
        for i, item in enumerate(market_containers):
            try:
                # Nom/Symbole
                name_element = None
                for selector in self.selectors['stock_name']:
                    name_element = item.select_one(selector)
                    if name_element:
                        break
                
                nom = name_element.get_text(strip=True) if name_element else f"Valeur {i+1}"
                
                # Prix
                price_element = None
                for selector in self.selectors['stock_price']:
                    price_element = item.select_one(selector)
                    if price_element:
                        break
                
                prix_brut = price_element.get_text(strip=True) if price_element else ""
                prix = self.extract_price(prix_brut)
                
                # Variation
                change_element = None
                for selector in self.selectors['stock_change']:
                    change_element = item.select_one(selector)
                    if change_element:
                        break
                
                variation_brute = change_element.get_text(strip=True) if change_element else ""
                variation_abs, variation_pct = self.extract_change(variation_brute)
                
                # Pourcentage séparé si disponible
                percent_element = None
                for selector in self.selectors['stock_percent']:
                    percent_element = item.select_one(selector)
                    if percent_element:
                        break
                
                if percent_element and not variation_pct:
                    variation_pct = percent_element.get_text(strip=True)
                
                cotation = {
                    "nom": nom,
                    "prix": prix,
                    "prix_brut": prix_brut,
                    "variation_absolue": variation_abs,
                    "variation_pourcentage": variation_pct,
                    "variation_brute": variation_brute,
                    "index": i + 1
                }
                
                market_data.append(cotation)
                
            except Exception as e:
                print(f"⚠️ Erreur lors de l'extraction de la cotation {i+1}: {e}")
                continue
        
        return market_data
    
    def auto_detect_news(self, soup):
        """Détection automatique des actualités"""
        print("🤖 Détection automatique des actualités...")
        
        potential_news = []
        
        # Chercher des patterns courants
        patterns = [
            'div[class*="news"]',
            'article',
            'div[class*="story"]',
            'div[class*="headline"]',
            'li[class*="item"]',
            '.article, .story, .news'
        ]
        
        for pattern in patterns:
            elements = soup.select(pattern)
            if len(elements) > 1:  # Au moins 2 éléments similaires
                potential_news.extend(elements)
                print(f"   Trouvé {len(elements)} éléments avec '{pattern}'")
        
        return potential_news[:20]  # Limiter à 20 actualités
    
    def scrape(self):
        """Méthode principale de scraping"""
        soup = self.get_soup()
        if not soup:
            print("❌ Impossible de récupérer le contenu HTML")
            return []
        
        print(f"📄 HTML récupéré ({len(str(soup))} caractères)")
        
        # Essayer de détecter le type de contenu
        all_data = []
        
        # 1. Scraper les actualités
        actualites = self.scrape_news(soup)
        if actualites:
            print(f"📰 {len(actualites)} actualités trouvées")
            for actualite in actualites:
                actualite['type'] = 'actualite'
            all_data.extend(actualites)
        
        # 2. Scraper les données de marché
        market_data = self.scrape_market_data(soup)
        if market_data:
            print(f"📈 {len(market_data)} cotations trouvées")
            for cotation in market_data:
                cotation['type'] = 'cotation'
            all_data.extend(market_data)
        
        # Si aucune donnée spécifique n'est trouvée, fallback sur l'ancienne méthode
        if not all_data:
            print("🔄 Fallback sur la méthode de base...")
            all_data = self.scrape_fallback(soup)
        
        print(f"✅ {len(all_data)} éléments extraits au total")
        return all_data
    
    def scrape_fallback(self, soup):
        """Méthode de fallback (votre code original amélioré)"""
        actualites = []
        
        # Votre sélecteur original
        for row in soup.select(".market-summary .item"):
            try:
                titre_elem = row.find("h3")
                desc_elem = row.find("p")
                
                titre = titre_elem.text.strip() if titre_elem else "Titre non disponible"
                description = desc_elem.text.strip() if desc_elem else "Description non disponible"
                
                actualites.append({
                    "titre": titre, 
                    "description": description,
                    "type": "actualite"
                })
            except Exception as e:
                print(f"⚠️ Erreur fallback: {e}")
                continue
        
        return actualites
    
    def debug_structure(self):
        """Analyse la structure HTML pour le débogage"""
        soup = self.get_soup()
        if not soup:
            return
        
        print("\n🔍 ANALYSE DE LA STRUCTURE HTML FINANCIÈRE")
        print("=" * 60)
        
        # Chercher des éléments financiers typiques
        financial_keywords = ['market', 'stock', 'price', 'quote', 'news', 'finance', 'trading']
        
        print("💰 Éléments avec mots-clés financiers:")
        for keyword in financial_keywords:
            elements = soup.find_all(class_=re.compile(keyword, re.I))
            if elements:
                print(f"   .{keyword}*: {len(elements)} éléments")
        
        # Tables (souvent utilisées pour les cotations)
        tables = soup.find_all('table')
        print(f"\n📊 Tables trouvées: {len(tables)}")
        for i, table in enumerate(tables[:3], 1):
            rows = table.find_all('tr')
            print(f"   Table {i}: {len(rows)} lignes")
        
        # Liens vers des articles
        links = soup.find_all('a', href=True)
        financial_links = [link for link in links if any(kw in link.get('href', '').lower() for kw in ['news', 'article', 'story'])]
        print(f"\n🔗 Liens vers articles: {len(financial_links)}")

# Classes spécialisées pour des sites spécifiques
class YahooFinanceScraper(BourseScraper):
    def __init__(self, site_url):
        super().__init__(site_url)
        self.selectors['news_containers'] = ['[data-testid="story-item"]', '.js-content-viewer']
        self.selectors['stock_price'] = ['[data-field="regularMarketPrice"]']

class BloombergScraper(BourseScraper):
    def __init__(self, site_url):
        super().__init__(site_url)
        self.selectors['news_containers'] = ['.story-list-story', '.headline-link']

class MarketwatchScraper(BourseScraper):
    def __init__(self, site_url):
        super().__init__(site_url)
        self.selectors['news_containers'] = ['.article__headline', '.collection__element']