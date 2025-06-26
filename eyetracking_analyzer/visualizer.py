# eyetracking_analyzer/visualizer.py
import os
import io
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from PIL import Image, ImageDraw, ImageFont

def gerar_heatmap(fixations_df, base_image_path, output_path):
    """
    Gera um mapa de calor (heatmap) a partir dos dados de fixação e o sobrepõe
    à imagem base.
    """
    try:
        base_image = Image.open(base_image_path)
        width, height = base_image.size

        pixel_x = fixations_df['FPOGX'] * width
        pixel_y = fixations_df['FPOGY'] * height
        
        fig, ax = plt.subplots(figsize=(width/100, height/100))
        
        sns.kdeplot(
            x=pixel_x, y=pixel_y, ax=ax, fill=True, cmap="jet",
            alpha=0.6, levels=100, thresh=0.05
        )
        
        ax.set_xlim(0, width)
        ax.set_ylim(height, 0)
        ax.axis('off')
        fig.patch.set_alpha(0)
        
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=100, bbox_inches='tight', pad_inches=0)
        buf.seek(0)
        heatmap_image = Image.open(buf)
        plt.close(fig)

        base_image_rgba = base_image.convert('RGBA')
        heatmap_rgba = heatmap_image.resize(base_image.size)
        
        composite_image = Image.alpha_composite(base_image_rgba, heatmap_rgba)
        
        composite_image.convert('RGB').save(output_path)
        print(f"  - Heatmap salvo em: {output_path}")

    except Exception as e:
        print(f"  - ERRO ao gerar heatmap: {e}")

def gerar_scanpath(fixations_df, base_image_path, output_path, radius=15):
    """
    Desenha o caminho do olhar (scanpath) sobre a imagem base.
    """
    try:
        base_image = Image.open(base_image_path).convert('RGBA')
        width, height = base_image.size
        
        draw = ImageDraw.Draw(base_image)

        try:
            font = ImageFont.truetype("arial.ttf", size=radius)
        except IOError:
            font = ImageFont.load_default()

        fixations = []
        for _, row in fixations_df.iterrows():
            fixations.append((row['FPOGX'] * width, row['FPOGY'] * height))

        if len(fixations) > 1:
            draw.line(fixations, fill=(66, 135, 245, 200), width=3)

        for i, (x, y) in enumerate(fixations):
            if i == 0:
                color = (46, 204, 113, 255) # Verde
            elif i == len(fixations) - 1:
                color = (231, 76, 60, 255) # Vermelho
            else:
                color = (52, 152, 219, 255) # Azul
            
            bbox = [x - radius, y - radius, x + radius, y + radius]
            draw.ellipse(bbox, fill=color, outline=(255, 255, 255, 255), width=2)
            
            text = str(i + 1)
            text_bbox = draw.textbbox((0,0), text, font=font)
            text_width = text_bbox[2] - text_bbox[0]
            text_height = text_bbox[3] - text_bbox[1]
            draw.text((x - text_width / 2, y - text_height / 2), text, font=font, fill="white")
            
        base_image.convert('RGB').save(output_path)
        print(f"  - Scanpath salvo em: {output_path}")

    except Exception as e:
        print(f"  - ERRO ao gerar scanpath: {e}")