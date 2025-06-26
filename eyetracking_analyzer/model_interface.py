# eyetracking_analyzer/model_interface.py
import os
import google.generativeai as genai
from PIL import Image
from config import MODELO_GENERATIVO

def setup_genai_api():
    """Configura a API do Gemini usando a chave do ambiente."""
    try:
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("Chave de API do Google não encontrada na variável de ambiente GOOGLE_API_KEY.")
        genai.configure(api_key=api_key)
        print("API do Gemini configurada com sucesso.")
        return True
    except Exception as e:
        print(f"Erro ao configurar a API do Gemini: {e}")
        return False

def submeter_dados_ao_modelo(prompt_texto, caminho_imagem):
    """
    Submete a imagem e o prompt de texto ao modelo Gemini Vision.
    """
    print(f"--- SUBMETENDO '{os.path.basename(caminho_imagem)}' AO MODELO {MODELO_GENERATIVO} ---")
    
    try:
        img = Image.open(caminho_imagem)
        conteudo_prompt = [prompt_texto, img]
        model = genai.GenerativeModel(MODELO_GENERATIVO)
        response = model.generate_content(conteudo_prompt)
        
        print("   - Resposta recebida do modelo.")
        return response.text
    except FileNotFoundError:
        return f"ERRO: A imagem não foi encontrada em '{caminho_imagem}'."
    except Exception as e:
        return f"ERRO ao contatar a API do Gemini: {e}"