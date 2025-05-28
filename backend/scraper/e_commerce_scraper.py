# scraper/e_commerce_scraper.py

from scraper.base_scraper import BaseScraper
import re

class EcommerceScraper(BaseScraper):
    def __init__(self, site_url, user_agent=None):
        super().__init__(site_url, user_agent)
        
        # Sélecteurs CSS communs pour différents sites e-commerce
        self.selectors = {
            'products': [
                'div.product',
                '.product-item',
                '.product-card',
                '[data-testid="product"]',
                '.item-container',
                '.product-container'
            ],
            'name': [
                'h2', 'h3', '.product-name', '.product-title', 
                '.item-name', '[data-testid="product-name"]',
                '.title', '.name'
            ],
            'price': [
                'span.price', '.product-price', '.price-current',
                '.item-price', '[data-testid="price"]', '.cost',
                '.amount', '.value'
            ]
        }
    
    def extract_price(self, price_text):
        """Extrait et nettoie le prix"""
        if not price_text:
            return None
        
        # Nettoyer le texte
        price_clean = price_text.strip()
        
        # Extraire les chiffres et symboles monétaires
        price_match = re.search(r'[\d\s.,]+[€$£¥]|[€$£¥][\d\s.,]+', price_clean)
        if price_match:
            return price_match.group().strip()
        
        # Fallback: extraire juste les chiffres
        numbers = re.findall(r'[\d.,]+', price_clean)
        if numbers:
            return numbers[0]
        
        return price_clean
    
    def find_elements_by_selectors(self, soup, selectors_list):
        """Trouve des éléments en essayant plusieurs sélecteurs"""
        for selector in selectors_list:
            elements = soup.select(selector)
            if elements:
                return elements
        return []
    
    def scrape(self):
        """Scrape les produits e-commerce"""
        soup = self.get_soup()
        if not soup:
            print("❌ Impossible de récupérer le contenu HTML")
            return []
        
        print(f"📄 HTML récupéré ({len(str(soup))} caractères)")
        
        # Chercher les produits avec différents sélecteurs
        products_containers = self.find_elements_by_selectors(soup, self.selectors['products'])
        
        if not products_containers:
            print("⚠️ Aucun conteneur de produit trouvé avec les sélecteurs standards")
            print("🔍 Essai de détection automatique...")
            
            # Tentative de détection automatique
            products_containers = self.auto_detect_products(soup)
        
        if not products_containers:
            print("❌ Aucun produit détecté")
            return []
        
        print(f"🛍️ {len(products_containers)} produits détectés")
        
        produits = []
        for i, item in enumerate(products_containers):
            try:
                # Extraire le nom
                nom_element = None
                for selector in self.selectors['name']:
                    nom_element = item.select_one(selector)
                    if nom_element:
                        break
                
                nom = nom_element.get_text(strip=True) if nom_element else f"Produit {i+1}"
                
                # Extraire le prix
                prix_element = None
                for selector in self.selectors['price']:
                    prix_element = item.select_one(selector)
                    if prix_element:
                        break
                
                prix_brut = prix_element.get_text(strip=True) if prix_element else "Prix non disponible"
                prix = self.extract_price(prix_brut)
                
                # Informations supplémentaires optionnelles
                description = ""
                desc_element = item.select_one('.description, .product-description, .summary')
                if desc_element:
                    description = desc_element.get_text(strip=True)[:200]  # Limiter à 200 chars
                
                image_url = ""
                img_element = item.select_one('img')
                if img_element:
                    image_url = img_element.get('src', '') or img_element.get('data-src', '')
                
                produit = {
                    "nom": nom,
                    "prix": prix,
                    "prix_brut": prix_brut,
                    "description": description,
                    "image_url": image_url,
                    "index": i + 1
                }
                
                produits.append(produit)
                
            except Exception as e:
                print(f"⚠️ Erreur lors de l'extraction du produit {i+1}: {e}")
                continue
        
        print(f"✅ {len(produits)} produits extraits avec succès")
        return produits
    
    def auto_detect_products(self, soup):
        """Tentative de détection automatique des produits"""
        print("🤖 Détection automatique des conteneurs de produits...")
        
        # Chercher des divs avec beaucoup d'éléments similaires
        potential_containers = []
        
        # Chercher des patterns courants
        common_patterns = [
            'div[class*="product"]',
            'div[class*="item"]',
            'article',
            'li[class*="product"]',
            'div[data-*="product"]'
        ]
        
        for pattern in common_patterns:
            elements = soup.select(pattern)
            if len(elements) > 2:  # Au moins 3 éléments similaires
                potential_containers.extend(elements)
                print(f"   Trouvé {len(elements)} éléments avec '{pattern}'")
        
        return potential_containers[:50]  # Limiter à 50 produits max
    
    def debug_structure(self):
        """Analyse la structure HTML pour aider au débogage"""
        soup = self.get_soup()
        if not soup:
            return
        
        print("\n🔍 ANALYSE DE LA STRUCTURE HTML")
        print("=" * 50)
        
        # Classes les plus communes
        all_classes = []
        for element in soup.find_all(class_=True):
            all_classes.extend(element.get('class'))
        
        from collections import Counter
        common_classes = Counter(all_classes).most_common(10)
        
        print("📊 Classes CSS les plus courantes:")
        for class_name, count in common_classes:
            print(f"   .{class_name}: {count} occurrences")
        
        # Tags avec des IDs
        ids = [elem.get('id') for elem in soup.find_all(id=True)]
        print(f"\n🏷️ Éléments avec ID: {len(ids)}")
        for id_name in ids[:10]:  # Afficher les 10 premiers
            print(f"   #{id_name}")
        
        # Structure générale
        print(f"\n📋 Structure générale:")
        print(f"   Divs: {len(soup.find_all('div'))}")
        print(f"   Articles: {len(soup.find_all('article'))}")
        print(f"   Sections: {len(soup.find_all('section'))}")
        print(f"   Listes (ul/ol): {len(soup.find_all(['ul', 'ol']))}")
        print(f"   Images: {len(soup.find_all('img'))}")
        print(f"   Liens: {len(soup.find_all('a'))}")

# Version spécialisée pour des sites spécifiques
class AmazonScraper(EcommerceScraper):
    def __init__(self, site_url):
        super().__init__(site_url)
        self.selectors = {
            'products': ['[data-component-type="s-search-result"]', '.s-result-item'],
            'name': ['h2 a span', '.a-size-base-plus'],
            'price': ['.a-price-whole', '.a-price .a-offscreen']
        }

class EbayScraper(EcommerceScraper):
    def __init__(self, site_url):
        super().__init__(site_url)
        self.selectors = {
            'products': ['.s-item', '.lvresult'],
            'name': ['.s-item__title', '.lvtitle'],
            'price': ['.s-item__price', '.amt']
        }