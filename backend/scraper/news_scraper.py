from scraper.base_scraper import BaseScraper

class NewsScraper(BaseScraper):
    def scrape(self):
        soup = self.get_soup()
        news = []
        for item in soup.find_all("a"):
            titre = item.get_text().strip()
            lien = item.get("href")
            if lien and titre:
                news.append({"titre": titre, "lien": lien})
        return news
