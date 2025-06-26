# main.py
from dotenv import load_dotenv
from eyetracking_analyzer.data_loader import buscar_dados_participante
from eyetracking_analyzer.model_interface import setup_genai_api, submeter_dados_ao_modelo
from eyetracking_analyzer.prompt_builder import construir_prompt_completo
# Atualizando o nome da função importada
from eyetracking_analyzer.reporter import salvar_relatorio_jsonl
from eyetracking_analyzer.pdf_generator import criar_relatorio_pdf
import time

def executar_analise_completa(parametros_busca):
    """
    Função principal que orquestra a busca, submissão e armazenamento com dados enriquecidos.
    """
    if not setup_genai_api():
        print("Falha na configuração da API. Encerrando o script.")
        return

    dados_para_analise = buscar_dados_participante(**parametros_busca)
    if not dados_para_analise:
        print("Nenhum dado encontrado para processar. Encerrando.")
        return

    # Renomeando a lista para maior clareza
    lista_de_resultados = []
    
    for dados in dados_para_analise:
        prompt = construir_prompt_completo(dados)
        #resposta_modelo = submeter_dados_ao_modelo(prompt, dados['image_path'])
        resposta_modelo = "Resposta do modelo..........."
        
        # --- MONTAGEM DO DICIONÁRIO COMPLETO ---
        # Este dicionário agora contém todos os campos que você solicitou.
        resultado_completo = {
            "participante": dados['participante'],
            "media_name": dados['media_name'],
            "categoria": dados['categoria'],
            "bloco": dados['bloco'],
            "prompt": prompt,
            "image_path": dados['image_path'],
            "scanpath_path": dados['scanpath_path'],
            "heatmap_path": dados['heatmap_path'],
            "fixmap_path": dados['fixmap_path'],
            "overlay_heatmap_path": dados['overlay_heatmap_path'],
            "Resposta": resposta_modelo 
            # Note que não é mais necessário o .replace("\n", " ") pois o JSON lida com isso
        }
        
        lista_de_resultados.append(resultado_completo)
        
        criar_relatorio_pdf(dados, resposta_modelo)
        
        print("Aguardando 2 segundos para evitar limite de requisições...")
        time.sleep(2) 
    
    # Chamando a função renomeada com a lista de resultados completos.
    salvar_relatorio_jsonl(lista_de_resultados)


# --- PONTO DE ENTRADA DO SCRIPT ---
if __name__ == "__main__":
    load_dotenv()
    
    parametros = {
        "participante": None,
        "media_name": "cd9e29.jpg", 
        "tipo_de_midia": None
    }
    
    executar_analise_completa(parametros)