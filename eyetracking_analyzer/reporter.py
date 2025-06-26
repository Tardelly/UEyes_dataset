# eyetracking_analyzer/reporter.py
import os
import pandas as pd
from config import OUTPUT_CSV_PATH, OUTPUT_DIR

# Renomeando a função para maior clareza
def salvar_relatorio_jsonl(lista_resultados):
    """
    Salva a lista de dicionários de resultados em um arquivo .jsonl.
    """
    if not lista_resultados:
        print("Nenhuma análise foi gerada para salvar.")
        return

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # O nome do arquivo agora será .jsonl
    caminho_saida_robusto = OUTPUT_CSV_PATH.replace('.csv', '.jsonl')

    try:
        df_resultados = pd.DataFrame(lista_resultados)
        
        df_resultados.to_json(
            caminho_saida_robusto,
            orient='records',
            lines=True,
            force_ascii=False,
            indent=None
        )
        
        print(f"--- ANÁLISE COMPLETA. Relatório robusto salvo em: '{caminho_saida_robusto}' ---")
    
    except Exception as e:
        print(f"ERRO ao salvar o relatório em JSON Lines: {e}")