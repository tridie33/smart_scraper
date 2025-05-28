# utils/exporter.py

import csv
import json
import pandas as pd
from fpdf import FPDF
from pathlib import Path
import os
from datetime import datetime

def export_data(data, filename, format_type, options=None):
    """
    Exporte les données dans le format spécifié
    
    Args:
        data: Liste de dictionnaires à exporter
        filename: Nom du fichier (avec ou sans extension)
        format_type: Format d'export ('csv', 'json', 'xlsx', 'pdf')
        options: Options supplémentaires (optionnel)
    """
    if not data:
        print("❌ Aucune donnée à exporter.")
        return False
    
    if options is None:
        options = {}
    
    format_type = format_type.lower()
    
    # Nettoyer le nom de fichier et ajouter l'extension si nécessaire
    filename = clean_filename(filename, format_type)
    
    # Créer le dossier parent si nécessaire
    Path(filename).parent.mkdir(parents=True, exist_ok=True)
    
    try:
        if format_type == "csv":
            return export_to_csv(data, filename, options)
        elif format_type == "json":
            return export_to_json(data, filename, options)
        elif format_type == "xlsx":
            return export_to_excel(data, filename, options)
        elif format_type == "pdf":
            return export_to_pdf(data, filename, options)
        else:
            print(f"❌ Format '{format_type}' non supporté.")
            return False
    
    except Exception as e:
        print(f"❌ Erreur lors de l'export {format_type.upper()}: {e}")
        return False

def clean_filename(filename, format_type):
    """Nettoie le nom de fichier et ajoute l'extension"""
    # Supprimer les caractères non autorisés
    filename = "".join(c for c in filename if c.isalnum() or c in (' ', '-', '_', '.'))
    
    # Ajouter l'extension si elle n'est pas présente
    if not filename.endswith(f'.{format_type}'):
        filename = f"{filename}.{format_type}"
    
    return filename

def export_to_csv(data, filename, options=None):
    """Exporte vers CSV avec options avancées"""
    if options is None:
        options = {}
    
    # Options par défaut
    delimiter = options.get('delimiter', ',')
    encoding = options.get('encoding', 'utf-8')
    include_index = options.get('include_index', False)
    
    try:
        # Obtenir toutes les clés possibles de tous les dictionnaires
        all_keys = set()
        for item in data:
            if isinstance(item, dict):
                all_keys.update(item.keys())
        
        all_keys = sorted(list(all_keys))
        
        with open(filename, 'w', newline='', encoding=encoding) as f:
            dict_writer = csv.DictWriter(f, fieldnames=all_keys, delimiter=delimiter)
            dict_writer.writeheader()
            
            for i, item in enumerate(data):
                if isinstance(item, dict):
                    # Ajouter un index si demandé
                    if include_index:
                        item['_index'] = i + 1
                    dict_writer.writerow(item)
                else:
                    # Si ce n'est pas un dict, créer une ligne simple
                    dict_writer.writerow({'data': str(item)})
        
        print(f"✅ Exporté en CSV : {filename} ({len(data)} lignes)")
        return True
        
    except Exception as e:
        print(f"❌ Erreur CSV : {e}")
        return False

def export_to_json(data, filename, options=None):
    """Exporte vers JSON avec métadonnées"""
    if options is None:
        options = {}
    
    # Options par défaut
    indent = options.get('indent', 2)
    include_metadata = options.get('include_metadata', True)
    encoding = options.get('encoding', 'utf-8')
    
    try:
        export_data_final = data
        
        # Ajouter des métadonnées si demandé
        if include_metadata:
            metadata = {
                'export_timestamp': datetime.now().isoformat(),
                'total_items': len(data),
                'format': 'json'
            }
            
            export_data_final = {
                'metadata': metadata,
                'data': data
            }
        
        with open(filename, 'w', encoding=encoding) as f:
            json.dump(export_data_final, f, ensure_ascii=False, indent=indent)
        
        print(f"✅ Exporté en JSON : {filename} ({len(data)} éléments)")
        return True
        
    except Exception as e:
        print(f"❌ Erreur JSON : {e}")
        return False

def export_to_excel(data, filename, options=None):
    """Exporte vers Excel avec mise en forme"""
    if options is None:
        options = {}
    
    try:
        df = pd.DataFrame(data)
        
        # Options Excel
        include_index = options.get('include_index', False)
        sheet_name = options.get('sheet_name', 'Données')
        
        # Créer le fichier Excel
        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name=sheet_name, index=include_index)
            
            # Obtenir la feuille pour la mise en forme
            worksheet = writer.sheets[sheet_name]
            
            # Auto-ajuster la largeur des colonnes
            for column in worksheet.columns:
                max_length = 0
                column_letter = column[0].column_letter
                
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                
                adjusted_width = min(max_length + 2, 50)  # Max 50 caractères
                worksheet.column_dimensions[column_letter].width = adjusted_width
        
        print(f"✅ Exporté en Excel : {filename} ({len(data)} lignes)")
        return True
        
    except Exception as e:
        print(f"❌ Erreur Excel : {e}")
        return False

def export_to_pdf(data, filename, options=None):
    """Exporte vers PDF avec mise en forme améliorée"""
    if options is None:
        options = {}
    
    try:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=15)
        
        # Titre
        title = options.get('title', 'Données exportées')
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(0, 10, title.encode('latin-1', 'replace').decode('latin-1'), ln=True, align='C')
        pdf.ln(10)
        
        # Métadonnées
        pdf.set_font("Arial", size=10)
        pdf.cell(0, 5, f"Date d'export: {datetime.now().strftime('%d/%m/%Y %H:%M')}", ln=True)
        pdf.cell(0, 5, f"Nombre d'elements: {len(data)}", ln=True)
        pdf.ln(5)
        
        # Contenu
        pdf.set_font("Arial", size=10)
        
        for i, item in enumerate(data, 1):
            # Numéro de l'élément
            pdf.set_font("Arial", 'B', 10)
            pdf.cell(0, 8, f"Element {i}:", ln=True)
            
            pdf.set_font("Arial", size=9)
            
            if isinstance(item, dict):
                for key, value in item.items():
                    # Nettoyer et encoder le texte
                    key_clean = clean_text_for_pdf(str(key))
                    value_clean = clean_text_for_pdf(str(value))
                    
                    line = f"  {key_clean}: {value_clean}"
                    
                    # Couper les lignes trop longues
                    if len(line) > 80:
                        line = line[:77] + "..."
                    
                    pdf.cell(0, 5, line, ln=True)
            else:
                item_clean = clean_text_for_pdf(str(item))
                pdf.multi_cell(0, 5, f"  {item_clean}")
            
            pdf.ln(3)
            
            # Nouvelle page si nécessaire
            if pdf.get_y() > 250:
                pdf.add_page()
        
        pdf.output(filename)
        print(f"✅ Exporté en PDF : {filename} ({len(data)} éléments)")
        return True
        
    except Exception as e:
        print(f"❌ Erreur PDF : {e}")
        return False

def clean_text_for_pdf(text):
    """Nettoie le texte pour l'export PDF"""
    try:
        # Remplacer les caractères problématiques
        replacements = {
            'à': 'a', 'á': 'a', 'â': 'a', 'ã': 'a', 'ä': 'a',
            'è': 'e', 'é': 'e', 'ê': 'e', 'ë': 'e',
            'ì': 'i', 'í': 'i', 'î': 'i', 'ï': 'i',
            'ò': 'o', 'ó': 'o', 'ô': 'o', 'õ': 'o', 'ö': 'o',
            'ù': 'u', 'ú': 'u', 'û': 'u', 'ü': 'u',
            'ç': 'c', 'ñ': 'n',
            '€': 'EUR', '£': 'GBP', '$': 'USD'
        }
        
        text_clean = str(text)
        for old, new in replacements.items():
            text_clean = text_clean.replace(old, new)
        
        # Encoder en latin-1 si possible, sinon remplacer les caractères problématiques
        return text_clean.encode('latin-1', 'replace').decode('latin-1')
        
    except Exception:
        # Fallback: garder seulement les caractères ASCII
        return ''.join(char if ord(char) < 128 else '?' for char in str(text))

def get_file_info(filename):
    """Retourne des informations sur le fichier exporté"""
    if os.path.exists(filename):
        size = os.path.getsize(filename)
        size_mb = size / (1024 * 1024)
        
        return {
            'exists': True,
            'size_bytes': size,
            'size_mb': round(size_mb, 2),
            'path': os.path.abspath(filename)
        }
    else:
        return {'exists': False}

# Fonction utilitaire pour exporter rapidement
def quick_export(data, base_filename="export"):
    """Exporte rapidement dans tous les formats"""
    formats = ['json', 'csv', 'xlsx']
    results = {}
    
    for fmt in formats:
        try:
            filename = f"{base_filename}.{fmt}"
            success = export_data(data, base_filename, fmt)
            results[fmt] = success
        except Exception as e:
            print(f"❌ Erreur {fmt}: {e}")
            results[fmt] = False
    
    return results