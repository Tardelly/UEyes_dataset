import os
import pandas as pd
import argparse

# Importa as funções da nossa biblioteca e as configurações
from eyetracking_analyzer.visualizer import gerar_heatmap, gerar_scanpath
from config import IMAGES_DIR, LOGS_DIR, OUTPUT_VIS_DIR

def main(args):
    """
    Encontra os arquivos de dados necessários e chama as funções de geração de visualizações.
    """
    participante = args.participante
    media_name = args.media

    # Cria o diretório de saída, se não existir
    os.makedirs(OUTPUT_VIS_DIR, exist_ok=True)

    log_file_found = False
    for log_filename in os.listdir(LOGS_DIR):
        # Procura por um participante específico
        if f"_kh0{participante.zfill(2)}_" not in log_filename:
            continue
        
        try:
            df_log = pd.read_csv(os.path.join(LOGS_DIR, log_filename))
            fixations_df = df_log[df_log['MEDIA_NAME'] == media_name]
            
            if not fixations_df.empty:
                base_image_path = os.path.join(IMAGES_DIR, media_name)
                if not os.path.exists(base_image_path):
                    print(f"ERRO: Imagem base '{media_name}' não encontrada.")
                    continue
                
                print(f"\nProcessando dados de '{log_filename}' para a mídia '{media_name}'...")
                log_file_found = True
                
                # Define os nomes dos arquivos de saída.
                base_output_name = f"{media_name.split('.')[0]}_P{participante.zfill(2)}"
                heatmap_output_path = os.path.join(OUTPUT_VIS_DIR, f"heatmap_{base_output_name}.png")
                scanpath_output_path = os.path.join(OUTPUT_VIS_DIR, f"scanpath_{base_output_name}.png")
                
                # Chama as funções da biblioteca
                gerar_heatmap(fixations_df, base_image_path, heatmap_output_path)
                gerar_scanpath(fixations_df, base_image_path, scanpath_output_path)
                break 
        except Exception as e:
            print(f"Erro ao processar {log_filename}: {e}")
            
    if not log_file_found:
        print(f"Não foram encontrados dados de fixação para o participante '{participante}' e a mídia '{media_name}'.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Gera visualizações de Heatmap e Scanpath a partir de dados de rastreamento ocular.")
    parser.add_argument("-p", "--participante", required=True, help="ID do participante (ex: 01)")
    parser.add_argument("-m", "--media", required=True, help="Nome do arquivo da imagem (ex: desktop_ui_02.png)")
    
    args = parser.parse_args()
    main(args)