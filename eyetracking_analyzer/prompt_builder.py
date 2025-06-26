# eyetracking_analyzer/prompt_builder.py
# eyetracking_analyzer/prompt_builder.py

def sumarizar_dados_oculares(df_dados):
    """Cria um resumo quantitativo geral dos dados de rastreamento ocular."""
    if df_dados.empty:
        return "Nenhum dado ocular disponível."
    
    num_fixacoes = len(df_dados)
    duracao_total = df_dados['FPOGD'].sum()
    duracao_media_fixacao = df_dados['FPOGD'].mean()
    
    return (
        f"**Resumo Quantitativo Geral:**\n"
        f"- Número total de fixações: {num_fixacoes}\n"
        f"- Duração total de observação (soma das fixações): {duracao_total:.2f} segundos\n"
        f"- Duração média por fixação: {duracao_media_fixacao:.3f} segundos"
    )

def formatar_dados_oculares_como_listas(df_dados):
    """
    Formata as colunas de dados oculares especificadas como listas de strings separadas.
    """
    if df_dados.empty:
        return "Nenhum dado de fixação disponível para formatar."

    # Define as colunas a serem formatadas e seu respectivo formato de string
    # Arredondar os floats para 4 casas decimais economiza espaço e mantém a precisão
    formatos = {
        'FPOGX': '{:.4f}',
        'FPOGY': '{:.4f}',
        'FPOGS': '{:.4f}',
        'FPOGD': '{:.4f}',
        'FPOGID': '{}'
        # A coluna 'USER' não é sequencial, então não a incluímos aqui.
        # Ela já está no contexto do prompt.
    }
    
    listas_formatadas = []
    
    for col, fmt in formatos.items():
        if col in df_dados.columns:
            # Converte cada valor na coluna para uma string, usando o formato definido
            valores_str = [fmt.format(v) for v in df_dados[col]]
            # Junta todos os valores de string com um ponto e vírgula
            valores_juntos = ';'.join(valores_str)
            # Cria a string final no formato "COLUNA = [valores]"
            listas_formatadas.append(f"{col} = [{valores_juntos}]")
    
    # Junta cada string de lista com uma quebra de linha
    return "\n".join(listas_formatadas)


def construir_prompt_completo(dados_analise):
    """
    Monta o prompt final com um resumo geral e os dados sequenciais
    formatados como listas.
    """
    # Gera o resumo geral
    sumarizacao_geral = sumarizar_dados_oculares(dados_analise['dados_oculares'])
    
    # Formata os dados brutos no formato de lista solicitado
    dados_como_listas = formatar_dados_oculares_como_listas(dados_analise['dados_oculares'])

    # Descrição das colunas para dar contexto ao modelo
    descricao_colunas_contexto = """
**Contexto das Métricas Oculares:**
As listas de dados sequenciais representam:
- **FPOGX**: A sequência de coordenadas X (horizontal) de cada fixação.
- **FPOGY**: A sequência de coordenadas Y (vertical) de cada fixação.
- **FPOGS**: O momento de início de cada fixação em segundos.
- **FPOGD**: A duração de cada fixação em segundos.
- **FPOGID**: O identificador sequencial de cada fixação.
"""

    # Monta o prompt final
    prompt = f"""
**Análise de Comportamento Ocular e Cena**

**Contexto da Tarefa:**
- Mídia Analisada: {dados_analise['media_name']}
- Categoria: {dados_analise['categoria']}
- Participante: {dados_analise['participante']}

**Dados de Rastreamento Ocular:**
{sumarizacao_geral}

**Sequência de Fixações (formato de lista):**
{dados_como_listas}

{descricao_colunas_contexto}

**Tarefa de Análise Solicitada:**
Com base na IMAGEM FORNECIDA e nos DADOS OCULARES SEQUENCIAIS acima, realize a seguinte análise:

1.  **Análise Qualitativa:**
    - Descreva o padrão da trajetória ocular (scanpath) do participante. Use as listas de coordenadas FPOGX e FPOGY para descrever o caminho que o olhar percorreu na imagem (ex: "começou no centro, moveu-se para o canto superior esquerdo, depois para uma área de texto à direita").
    - Analise a cena na imagem. Identifique os objetos, textos ou elementos gráficos mais proeminentes.
    - Correlacione a trajetória ocular com os elementos da cena. As sequências de fixações se concentram em áreas específicas da imagem? Essas áreas correspondem aos elementos que você identificou como importantes?

2.  **Análise Quantitativa:**
    - Analise as listas de FPOGS e FPOGD. Existem fixações de longa duração em pontos específicos da trajetória? O que isso pode indicar sobre o interesse ou dificuldade do participante naqueles pontos da imagem?
    - A sequência de fixações é rápida e dispersa (muitas fixações curtas) ou lenta e focada (poucas fixações longas)? Relacione isso com o tipo de conteúdo da imagem (ex: uma imagem complexa pode gerar mais fixações exploratórias).

Por favor, estruture sua resposta de forma clara, separando a análise qualitativa da quantitativa.
"""
    return prompt