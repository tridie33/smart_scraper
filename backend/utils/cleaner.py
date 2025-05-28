import re
from bs4 import BeautifulSoup

class DataCleaner:
    def __init__(self, site_type="generic"):
        self.site_type = site_type.lower()

    def clean(self, raw_data):
        """ Nettoie une liste de dictionnaires """
        return [self.clean_item(item) for item in raw_data]

    def clean_item(self, item):
        """ Nettoie un seul élément """
        cleaned_item = {}

        for key, value in item.items():
            if isinstance(value, str):
                cleaned_value = self._clean_text(value)
            else:
                cleaned_value = value

            cleaned_item[key] = cleaned_value

        # Appliquer nettoyage spécifique au site
        if self.site_type == "ecommerce":
            cleaned_item = self._clean_ecommerce(cleaned_item)
        elif self.site_type == "boursier":
            cleaned_item = self._clean_bourse(cleaned_item)
        elif self.site_type == "wikipedia":
            cleaned_item = self._clean_wikipedia(cleaned_item)

        return cleaned_item

    def _clean_text(self, text):
        # Supprimer HTML, espaces, sauts de ligne, etc.
        text = BeautifulSoup(text, "html.parser").get_text()
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

    def _clean_ecommerce(self, item):
        if "price" in item:
            item["price"] = re.sub(r"[^\d.,]", "", item["price"])
        return item

    def _clean_bourse(self, item):
        if "variation" in item:
            item["variation"] = item["variation"].replace("%", "").strip()
        return item

    def _clean_wikipedia(self, item):
        for k in item:
            item[k] = re.sub(r"\[\d+\]", "", item[k])  # Supprime les références [1], [2], etc.
        return item
