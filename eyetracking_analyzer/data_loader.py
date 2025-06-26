# eyetracking_analyzer/data_loader.py
# eyetracking_analyzer/data_loader.py
import os
import pandas as pd
from config import INFO_CSV_PATH, IMAGES_DIR, LOGS_DIR, SALIENCY_MAPS_DIR, SCANPATHS_DIR

def buscar_dados_participante(participante=None, media_name=None, tipo_de_midia=None, duration='7s'):
    """
    Busca e filtra os dados, agora incluindo o caminho para a imagem overlay_heatmap.
    """
    # ... (o início da função permanece o mesmo) ...
    print("--- INICIANDO BUSCA E FILTRAGEM DE DADOS ---")
    try:
        df_info = pd.read_csv(INFO_CSV_PATH, sep=';')
    except FileNotFoundError:
        print(f"ERRO: Arquivo de informações '{INFO_CSV_PATH}' não encontrado.")
        return []

    if media_name:
        df_info = df_info[df_info['Image Name'] == media_name]
    if tipo_de_midia:
        df_info = df_info[df_info['Category'].str.contains(tipo_de_midia, case=False, na=False)]

    if df_info.empty:
        print("Nenhuma imagem encontrada em info.csv com os filtros aplicados.")
        return []
    
    print(f"Encontradas {len(df_info)} imagens correspondentes em info.csv.")
    
    dados_finais = []
    for _, row in df_info.iterrows():
        img_name = row['Image Name']
        block = str(row['Block']).zfill(2)
        category = row['Category']
        img_path = os.path.join(IMAGES_DIR, img_name)

        if not os.path.exists(img_path):
            print(f"AVISO: Imagem '{img_path}' não encontrada. Pulando.")
            continue

        log_files_a_procurar = []
        if participante:
            log_filename = f"{block}_kh0{str(participante).zfill(2)}_fixations.csv"
            log_files_a_procurar.append(os.path.join(LOGS_DIR, log_filename))
        else:
            for file in os.listdir(LOGS_DIR):
                if file.startswith(f"{block}_") and file.endswith("_fixations.csv"):
                    log_files_a_procurar.append(os.path.join(LOGS_DIR, file))

        for log_path in log_files_a_procurar:
            if not os.path.exists(log_path):
                print(f"AVISO: Arquivo de log '{log_path}' não encontrado. Pulando.")
                continue
            
            try:
                df_log = pd.read_csv(log_path)
                id_participante_log = os.path.basename(log_path).split('_')[1].replace('kh0', '')
                log_data_imagem = df_log[df_log['MEDIA_NAME'] == img_name]
                if not log_data_imagem.empty:
                    print(f"  - Dados encontrados para participante '{id_participante_log}' e imagem '{img_name}'.")
                    
                    # --- LÓGICA ADICIONADA PARA ENCONTRAR OS CAMINHOS DAS IMAGENS ---
                    scanpath_path = os.path.join(SCANPATHS_DIR, f"paths_{duration}", img_name.split(".")[0], f"{id_participante_log}.png")
                    heatmap_path = os.path.join(SALIENCY_MAPS_DIR, f"heatmaps_{duration}", img_name)
                    fixmap_path = os.path.join(SALIENCY_MAPS_DIR, f"fixmaps_{duration}", img_name)
                    # NOVO CAMINHO PARA O OVERLAY HEATMAP
                    overlay_heatmap_path = os.path.join(SALIENCY_MAPS_DIR, f"overlay_heatmaps_{duration}", f"overlay_{img_name}")
                    print(overlay_heatmap_path)
                    dados_finais.append({
                        "participante": id_participante_log,
                        "media_name": img_name,
                        "categoria": category,
                        "bloco": block,
                        "image_path": img_path,
                        "scanpath_path": scanpath_path,
                        "heatmap_path": heatmap_path,
                        "fixmap_path": fixmap_path,
                        "overlay_heatmap_path": overlay_heatmap_path, # Novo
                        "dados_oculares": log_data_imagem
                    })
            except Exception as e:
                print(f"ERRO ao processar o arquivo de log '{log_path}': {e}")
                
    print(f"--- FIM DA BUSCA. Total de {len(dados_finais)} conjuntos de dados para análise. ---")
    return dados_finais