# config.py
import os

# --- Caminhos Base ---
# Pega o caminho do diretório onde o script está sendo executado
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# --- Caminhos dos Dados ---
INFO_CSV_PATH = os.path.join(BASE_DIR, 'info.csv')
IMAGES_DIR = os.path.join(BASE_DIR, 'images')
LOGS_DIR = os.path.join(BASE_DIR, 'eyetracker_logs')
# NOVOS CAMINHOS ADICIONADOS
SALIENCY_MAPS_DIR = os.path.join(BASE_DIR, 'saliency_maps')
SCANPATHS_DIR = os.path.join(BASE_DIR, 'scanpaths')

# --- Configurações do Modelo ---
# Para análise de imagem e texto, 'gemini-pro-vision' é o recomendado.
MODELO_GENERATIVO = 'gemini-2.5-flash'

# --- Configurações de Saída ---
OUTPUT_DIR = os.path.join(BASE_DIR, 'reports')
OUTPUT_CSV_PATH = os.path.join(OUTPUT_DIR, 'relatorio_analise_modelos.csv')
# NOVO CAMINHO PARA OS PDFs
PDF_REPORTS_DIR = os.path.join(OUTPUT_DIR, 'pdf') 
# NOVO CAMINHO PARA AS VISUALIZAÇÕES
OUTPUT_VIS_DIR = os.path.join(OUTPUT_DIR, 'visualizations')