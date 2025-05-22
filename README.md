# 🕷️ Smart Scraper

**Smart Scraper** est une application modulaire permettant de scraper différents types de sites web (e-commerce, sites boursiers, sites d’actualités) et d’exporter les données collectées dans plusieurs formats (CSV, JSON, XLSX, PDF).

---

## 📦 Fonctionnalités actuelles

- 🔍 Scraping basé sur le type de site choisi
- 🧼 Nettoyage des données avant export
- 🧾 Export multi-format : `CSV`, `JSON`, `XLSX`, `PDF`
- 🗃️ Architecture modulaire avec séparation des scrapers

## 📦 Fonctionnalités en cours 
  
- 🌐 Interface de base HTML/CSS (bientôt remplacée par React)

---

## 🚧 État du projet

🧪 **EN COURS DE DÉVELOPPEMENT**  
Certaines fonctionnalités sont encore en construction.  
Des améliorations continues sont prévues. Contributions bienvenues ! 🙌

---

## 💡 Améliorations prévues

- 🔐 Authentification des utilisateurs
- ⚙️ Scraping intelligent avec adaptation automatique à la structure du site
- 💻 Interface frontend en **React** avec **CSS personnalisé** (sans Tailwind)
- 📊 Affichage dynamique des données avant export
- ☁️ Hébergement en ligne (ex. : Vercel / Render / Heroku)

---

## 📁 Structure du projet

smart_scraper/
│
├── backend/
│   ├── main.py
│   ├── config/
│   ├── scraper/
│   ├── utils/
│   └── output/
│
├── frontend/
│   ├── public/
│   ├── src/
│   ├── package.json
│   └── ... (React + CSS)
│
└── README.md


---

## 🧰 Installation locale

### 🔧 Prérequis

- Python 3.9+
- Git
- pip

### 🚀 Lancer le projet

```bash
git clone https://github.com/<TON_NOM_UTILISATEUR>/smart_scraper.git
cd smart_scraper
python main.py
```

## 🤝 Contribuer
Les contributions sont les bienvenues !
Si vous avez des idées, ouvrez une issue ou proposez une pull request.
