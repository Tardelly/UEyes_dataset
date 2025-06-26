# eyetracking_analyzer/pdf_generator.py
import os
from PIL import Image, ImageDraw, ImageFont
from fpdf import FPDF
from config import PDF_REPORTS_DIR

def criar_imagem_composta(image_paths_with_titles, output_path):
    """
    Cria uma única imagem composta a partir de várias imagens, organizando-as em uma grade.

    Args:
        image_paths_with_titles (list): Uma lista de tuplas (título, caminho_da_imagem).
        output_path (str): O caminho para salvar a imagem composta final.

    Returns:
        bool: True se a imagem foi criada com sucesso, False caso contrário.
    """
    try:
        # --- Configurações de Layout da Imagem Composta ---
        PADDING = 40
        SPACING = 30
        TITLE_HEIGHT = 40
        THUMB_WIDTH, THUMB_HEIGHT = 800, 600
        COLS = 3
        
        # --- Cálculo das Dimensões da Imagem Final ---
        num_images = len(image_paths_with_titles)
        rows = (num_images + COLS - 1) // COLS
        total_width = (THUMB_WIDTH * COLS) + (SPACING * (COLS - 1)) + (PADDING * 2)
        total_height = (THUMB_HEIGHT * rows) + (TITLE_HEIGHT * rows) + (SPACING * (rows - 1)) + (PADDING * 2)

        # --- Criação da Tela (Canvas) Branca ---
        composite_image = Image.new('RGB', (total_width, total_height), 'white')
        draw = ImageDraw.Draw(composite_image)

        # --- Carregamento da Fonte ---
        try:
            # Tenta usar uma fonte comum. Altere o caminho se necessário.
            font_path = "arial.ttf" # Em Windows: "C:/Windows/Fonts/arial.ttf"
            title_font = ImageFont.truetype(font_path, 32)
        except IOError:
            print(f"AVISO: Fonte '{font_path}' não encontrada. Usando fonte padrão.")
            title_font = ImageFont.load_default()

        # --- Montagem da Grade de Imagens ---
        x, y = PADDING, PADDING
        for i, (title, path) in enumerate(image_paths_with_titles):
            # Carrega a imagem ou cria um placeholder se não encontrada
            try:
                img = Image.open(path)
                img.thumbnail((THUMB_WIDTH, THUMB_HEIGHT))
            except FileNotFoundError:
                img = Image.new('RGB', (THUMB_WIDTH, THUMB_HEIGHT), (230, 230, 230))
                d = ImageDraw.Draw(img)
                d.text((50, 280), f"Imagem não encontrada:\n{os.path.basename(path)}", fill=(0,0,0))
            
            # Desenha o título na tela principal
            draw.text((x, y), title, font=title_font, fill=(0,0,0))
            
            # Cola a miniatura da imagem na tela principal
            composite_image.paste(img, (x, y + TITLE_HEIGHT))
            
            # Atualiza as coordenadas para a próxima imagem na grade
            if (i + 1) % COLS == 0:
                x = PADDING
                y += THUMB_HEIGHT + TITLE_HEIGHT + SPACING
            else:
                x += THUMB_WIDTH + SPACING
        
        composite_image.save(output_path)
        print(f"  - Imagem composta criada em: {output_path}")
        return True

    except Exception as e:
        print(f"  - ERRO ao criar imagem composta: {e}")
        return False


def criar_relatorio_pdf(dados_analise, resposta_modelo):
    """
    Gera um arquivo PDF que inclui uma imagem composta de todas as análises visuais.
    """
    os.makedirs(PDF_REPORTS_DIR, exist_ok=True)
    
    # --- Define os caminhos e títulos para a imagem composta ---
    imagens_para_compor = [
        ("Imagem Base", dados_analise['image_path']),
        ("Heatmap (7s)", dados_analise['heatmap_path']),
        ("Overlay Heatmap (7s)", dados_analise['overlay_heatmap_path']),
        ("Scanpath (7s)", dados_analise['scanpath_path']),
        ("Mapa de Fixação (7s)", dados_analise['fixmap_path']),
    ]
    
    # Define um caminho temporário para a imagem composta
    nome_base_arquivo = f"temp_{dados_analise['media_name'].replace('.', '_')}_P{dados_analise['participante']}"
    caminho_imagem_composta = os.path.join(PDF_REPORTS_DIR, f"{nome_base_arquivo}.png")

    # --- 1. Cria a Imagem Composta ---
    sucesso_composicao = criar_imagem_composta(imagens_para_compor, caminho_imagem_composta)

    # --- 2. Cria o PDF ---
    pdf = FPDF(orientation='P', unit='mm', format='A4')
    pdf.add_page()
    
    # Cabeçalho do PDF
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(0, 10, f"Análise de Rastreamento Ocular", 0, 1, 'C')
    pdf.ln(5)
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 8, f"Mídia: {dados_analise['media_name']}", 0, 1)
    pdf.set_font('Arial', '', 12)
    pdf.cell(0, 8, f"Participante: {dados_analise['participante']} | Categoria: {dados_analise['categoria']}", 0, 1)
    pdf.ln(10)

    # Corpo do Relatório de Texto
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, 'Relatório Gerado pelo Modelo de IA', 0, 1)
    texto_processado = resposta_modelo.encode('latin-1', 'replace').decode('latin-1')
    pdf.set_font('Arial', '', 11)
    pdf.multi_cell(0, 5, texto_processado)

    # Adiciona a imagem composta em uma nova página paisagem
    if sucesso_composicao:
        pdf.add_page(orientation='L')
        pdf.set_font('Arial', 'B', 14)
        pdf.cell(0, 10, 'Galeria de Imagens da Análise', 0, 1, 'C')
        pdf.image(caminho_imagem_composta, x=10, y=30, w=pdf.w - 20) # Largura quase total da página
    
    # --- 3. Salva o PDF Final ---
    nome_arquivo_pdf = f"Relatorio_Final_{nome_base_arquivo.replace('temp_', '')}.pdf"
    caminho_saida_pdf = os.path.join(PDF_REPORTS_DIR, nome_arquivo_pdf)
    
    try:
        pdf.output(caminho_saida_pdf)
        print(f"  - Relatório PDF final salvo em: {caminho_saida_pdf}")
    except Exception as e:
        print(f"  - ERRO ao salvar PDF final: {e}")

    # --- 4. Limpeza (remove a imagem composta temporária) ---
    if os.path.exists(caminho_imagem_composta):
        os.remove(caminho_imagem_composta)