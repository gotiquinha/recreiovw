import streamlit as st
import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import re

def formatar_numero(numero):
    if isinstance(numero, str):
        return numero
    if numero >= 1000000:
        return f"{numero/1000000:.1f}M".replace('.', ',')
    elif numero >= 1000:
        return f"{numero/1000:.1f}K".replace('.', ',')
    return str(int(numero))

# Configuração da página
st.set_page_config(page_title="SEO Recreio Volksvagen", layout="wide")
st.title("SEO Recreio Volksvagen")

# Função para extrair data do relatório
def extrair_data(texto):
    match = re.search(r'Data de geração: (.*)', texto)
    if match:
        return match.group(1)
    return ""

# Função para extrair números do texto
def extrair_numero(texto, padrao):
    match = re.search(padrao, texto)
    if match:
        numero = match.group(1)
        return float(numero.replace('.', '').replace(',', '.'))
    return 0

# Função para carregar e processar dados
def carregar_dados(arquivo):
    with open(arquivo, 'r', encoding='utf-8') as f:
        dados = json.load(f)
        conteudo = dados['conteudo']
        
        # Extraindo dados do conteúdo
        trafico_organico = int(re.search(r'Tráfego estimado: (\d+\.?\d*)', conteudo).group(1).replace('.', ''))
        palavras_chave = int(re.search(r'Palavras-chave orgânicas: (\d+\.?\d*)', conteudo).group(1).replace('.', ''))
        dominios_ref = int(re.search(r'Domínios de referência: (\d+)', conteudo).group(1))
        backlinks = float(re.search(r'Total: ([\d,\.]+) milhões', conteudo).group(1).replace(',', '.')) * 1000000 if 'milhões' in conteudo else int(re.search(r'Total: (\d+)', conteudo).group(1))
        
        return {
            'Tráfego Orgânico': trafico_organico,
            'Palavras-chave': palavras_chave,
            'Domínios de Referência': dominios_ref,
            'Total de Backlinks': backlinks
        }

# Carregando dados do arquivo principal
with open('analise_detalhada_recreiovw_por_pagina.json', 'r', encoding='utf-8') as f:
    dados_principais = json.load(f)
    data_geracao = re.search(r'Data de geração: (.*)', dados_principais['conteudo']).group(1)

# Carregando os dados
dados_vw = carregar_dados('analise_detalhada_recreiovw_por_pagina.json')
dados_concorrentes = {
    'Carbel': carregar_dados('analise_detalhada_carbel_por_pagina.json'),
    'Grupo AB': carregar_dados('analise_detalhada_grupoab_por_pagina.json'),
    'WTotal VW': carregar_dados('analise_detalhada_wtotalvw_por_pagina.json'),
    'Roma VW': carregar_dados('relatorio_romavw.json'),
    'Servopa': carregar_dados('relatorio_servopa.json'),
    'Saga VW': carregar_dados('relatorio_sagavw.json')
}

# Introdução
st.header("Introdução")
st.write(f"""
Este relatório apresenta uma análise comparativa de performance SEO entre a Recreio VW (Líder) e seus principais concorrentes no mercado automotivo.
As análises são baseadas em dados reais coletados através do https://pt.semrush.com/seo/

**Período da Análise:** Últimos 12 meses (até {data_geracao})
""")

# Análise do Tráfego Orgânico Total
st.header("1. Análise do Tráfego Orgânico Total")
st.write("""
O Tráfego Orgânico Total representa o número de visitantes que chegam ao site através de resultados de busca não pagos.
Esta métrica é crucial para avaliar a visibilidade natural do site nos mecanismos de busca.
Quanto maior o tráfego orgânico, melhor o posicionamento do site nos resultados de busca.
""")

# Criando DataFrame para o tráfego orgânico
trafico_organico = {
    'Empresa': ['Recreio VW (Líder)'] + list(dados_concorrentes.keys()),
    'Tráfego Orgânico': [
        dados_vw['Tráfego Orgânico']
    ] + [dados['Tráfego Orgânico'] for dados in dados_concorrentes.values()]
}

df_trafico = pd.DataFrame(trafico_organico)

# Gráfico de barras para tráfego orgânico
fig_trafico = px.bar(df_trafico, x='Empresa', y='Tráfego Orgânico',
                    title='Comparação do Tráfego Orgânico Total',
                    color='Empresa')
st.plotly_chart(fig_trafico, use_container_width=True)

# Análise de Palavras-chave Comerciais
st.header("2. Análise de Palavras-chave Comerciais")
st.write("""
As Palavras-chave Comerciais são termos de busca que indicam intenção de compra ou interesse comercial.
Esta métrica avalia quantas palavras-chave com potencial de conversão o site está posicionado.
Um maior número de palavras-chave comerciais bem posicionadas indica maior potencial de geração de leads e vendas.
""")

# Criando DataFrame para palavras-chave
palavras_chave = {
    'Empresa': ['Recreio VW (Líder)'] + list(dados_concorrentes.keys()),
    'Palavras-chave Comerciais': [
        dados_vw['Palavras-chave']
    ] + [dados['Palavras-chave'] for dados in dados_concorrentes.values()]
}

df_palavras = pd.DataFrame(palavras_chave)

# Gráfico de radar para palavras-chave
fig_palavras = px.line_polar(df_palavras, r='Palavras-chave Comerciais', theta='Empresa',
                           line_close=True, title='Distribuição de Palavras-chave Comerciais')
st.plotly_chart(fig_palavras, use_container_width=True)

# Análise da Autoridade do Domínio
st.header("3. Análise da Autoridade do Domínio")
st.write("""
### O que são Backlinks?
Backlinks são links de outros sites que apontam para o seu site. Por exemplo, quando um blog automotivo menciona e 
coloca um link para a Recreio VW, isso é um backlink. Eles são importantes porque:
- Funcionam como "votos de confiança" para o Google
- Ajudam a aumentar a autoridade do site
- Trazem tráfego direto de outros sites

### Como medimos a Autoridade?
A autoridade é medida considerando dois fatores principais encontrados nos relatórios:
1. **Número total de backlinks**: quantidade total de links apontando para o site
2. **Domínios de referência**: quantidade de sites diferentes que fazem links para o site (quanto mais diversificado, melhor)
""")

# Adicionando informações detalhadas sobre backlinks
st.write("### Dados Detalhados de Autoridade")

# Selecionando apenas as colunas relevantes para autoridade
colunas_autoridade = ['Empresa', 'Palavras-chave', 'Domínios de Referência', 'Total de Backlinks']
dados_detalhados = pd.DataFrame([
    {'Empresa': 'Recreio VW (Líder)', **dados_vw},
    {'Empresa': 'Carbel', **dados_concorrentes['Carbel']},
    {'Empresa': 'Grupo AB', **dados_concorrentes['Grupo AB']},
    {'Empresa': 'WTotal VW', **dados_concorrentes['WTotal VW']},
    {'Empresa': 'Roma VW', **dados_concorrentes['Roma VW']},
    {'Empresa': 'Servopa', **dados_concorrentes['Servopa']},
    {'Empresa': 'Saga VW', **dados_concorrentes['Saga VW']}
])[colunas_autoridade]

# Formatando os números grandes
dados_detalhados['Total de Backlinks'] = dados_detalhados['Total de Backlinks'].apply(formatar_numero)

# Exibindo tabela comparativa com formatação brasileira
st.dataframe(dados_detalhados.style.background_gradient(cmap='Blues'))

st.write("""
### Análise dos Dados de Autoridade
Com base nos dados dos relatórios, podemos observar:
- A quantidade de domínios únicos que fazem referência a cada site
- O número total de backlinks de cada concorrente
""")

# Análise de Share de Tráfego
st.header("4. Análise de Share de Tráfego")
st.write("""
**Nota Importante:** Os dados apresentados nesta seção são exclusivamente da Recreio Volkswagen (Grupo Líder), 
representando a distribuição do tráfego orgânico e pago específico desta concessionária.
""")

# Palavras-chave Orgânicas
st.subheader("Principais Palavras-chave Orgânicas")
st.write("""
Análise das principais palavras-chave que geram tráfego orgânico (gratuito) para o site.
Estas são as buscas onde o site aparece naturalmente nos resultados do Google, sem custos de publicidade.
""")

# Criando DataFrame para palavras-chave orgânicas
df_kw_organicas = pd.DataFrame([
    ["recreio veículos", "1.900", "4,76%"],
    ["recreio vw", "880", "2,20%"],
    ["recreio volkswagen", "880", "2,20%"],
    ["volkswagen recreio", "720", "1,80%"],
    ["recreio bh", "2.900", "1,19%"]
], columns=["Palavra-chave", "Volume", "Tráfego"])

st.dataframe(df_kw_organicas, hide_index=True)

# Explicação sobre sobreposição de palavras-chave
st.info("""
**Nota sobre palavras-chave duplicadas:**
Algumas palavras-chave (como "recreio volkswagen" e "recreio bh") aparecem tanto nas buscas orgânicas quanto pagas. 
Isso é uma estratégia intencional onde:
- O site aparece naturalmente (orgânico) nesses termos
- A empresa também investe em anúncios para os mesmos termos
- Isso garante maior visibilidade e protege a marca contra anúncios de concorrentes
""")

# Distribuição por Intenção
st.subheader("Distribuição por Intenção de Busca")
st.write("""
A intenção de busca representa o objetivo do usuário ao realizar uma pesquisa. Cada tipo indica:

- **Informacional**: Buscas por informações gerais, como "como funciona financiamento Volkswagen" ou "qual melhor SUV VW"
- **Navegacional**: Buscas diretas pela marca ou concessionária, como "recreio volkswagen" ou "vw recreio"
- **Comercial**: Buscas com intenção de compra, como "comprar polo zero km" ou "preço volkswagen nivus"
- **Transacional**: Buscas para realizar uma ação específica, como "agendar test drive vw" ou "solicitar cotação volkswagen"
""")

# Criando DataFrame para intenções de busca
df_intencoes = pd.DataFrame([
    ["Informacional", "8.300", "22.000", "79,9%"],
    ["Navegacional", "465", "6.100", "4,5%"],
    ["Comercial", "1.100", "7.300", "10,2%"],
    ["Transacional", "560", "544", "5,4%"]
], columns=["Tipo de Busca", "Palavras-chave", "Tráfego", "Porcentagem"])

st.dataframe(df_intencoes, hide_index=True)

# Palavras-chave Pagas
st.subheader("Principais Palavras-chave Pagas")
st.write("""
Análise das principais palavras-chave pagas e seus resultados. 

**Legenda:**
- **Posição**: Colocação do anúncio na página de resultados do Google (1 = primeiro anúncio no topo)
- **Volume**: Quantidade média mensal de buscas por essa palavra-chave
- **CPC (Custo Por Clique)**: Valor médio pago por cada clique no anúncio
- **Tráfego**: Percentual do tráfego total que essa palavra-chave gera
""")

# Criando DataFrame para palavras-chave pagas
df_kw_pagas = pd.DataFrame([
    ["recreio bh", 1, "2.900", "R$ 0,47", "62,38%"],
    ["recreio volkswagen", 1, "880", "R$ 1,05", "18,80%"],
    ["recreio campos", 1, "170", "R$ 1,23", "3,21%"],
    ["concessionária da volkswagen rj", 1, "170", "R$ 1,23", "3,21%"],
    ["volkswagen rio de janeiro", 2, "480", "R$ 1,58", "2,75%"]
], columns=["Palavra-chave", "Posição", "Volume", "CPC", "Tráfego"])

st.dataframe(df_kw_pagas, hide_index=True)

# Resumo do Tráfego Pago
st.write("""
**Resumo do Tráfego Pago:**
- Total de palavras-chave pagas: 15 (↓ 6%)
- Custo mensal estimado: R$ 117,00
- Tráfego estimado: 218 visitas (estável)
""") 