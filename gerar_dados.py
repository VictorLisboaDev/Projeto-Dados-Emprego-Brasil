"""
Projeto: Análise do Mercado de Trabalho Brasileiro (2012-2026)
VERSÃO DEFINITIVA - CORRIGIDA
"""

import sidrapy
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')

# Configuração de estilo
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (14, 7)

class AnaliseMercadoTrabalho:
    def __init__(self):
        self.governos = {
            'Dilma': (2012, 2016),
            'Temer': (2016, 2018),
            'Bolsonaro': (2019, 2022),
            'Lula': (2023, 2026)
        }
        self.dados = {}
        
    def baixar_dados(self):
        """Baixa os dados do IBGE"""
        print("🔄 Baixando dados do IBGE/SIDRA...")
        
        try:
            # Tabela 4092 - Taxa de desocupação
            print("  - Baixando taxa de desemprego (tabela 4092)...")
            self.dados['desemprego'] = sidrapy.get_table(
                table_code="4092",
                territorial_level="1",
                ibge_territorial_code="all",
                period="all"
            )
            
            # Tabela 4662 - Rendimento médio
            print("  - Baixando rendimento médio (tabela 4662)...")
            self.dados['rendimento'] = sidrapy.get_table(
                table_code="4662",
                territorial_level="1",
                ibge_territorial_code="all",
                period="all"
            )
            
            print("✅ Dados baixados com sucesso!")
            return True
            
        except Exception as e:
            print(f"❌ Erro ao baixar dados: {e}")
            return False
    
    def processar_taxa_desemprego(self):
        """Processa a taxa de desemprego de forma robusta"""
        print("🔄 Processando taxa de desemprego...")
        
        df = self.dados['desemprego']
        
        # Mostrar estrutura para debug
        print(f"Colunas: {df.columns.tolist()}")
        print(f"Primeiras linhas:\n{df.head(3)}")
        
        # Filtrar dados do Brasil
        df_brasil = df[df['D4N'] == 'Brasil']
        
        # Extrair período (D1C) e valor (V)
        periodos = df_brasil['D1C'].astype(str).str.zfill(6)  # Garantir 6 dígitos
        valores = df_brasil['V'].astype(str).str.replace(',', '.').str.replace('...', '')
        
        # Converter para numérico
        taxas = pd.to_numeric(valores, errors='coerce')
        
        # Converter período para data
        datas = []
        for p in periodos:
            try:
                # Formato: AAAATT (ex: 202201)
                ano = int(p[:4])
                trim = int(p[4:6])
                # Criar data no início do trimestre
                if trim == 1:
                    data = f"{ano}-01-01"
                elif trim == 2:
                    data = f"{ano}-04-01"
                elif trim == 3:
                    data = f"{ano}-07-01"
                else:
                    data = f"{ano}-10-01"
                datas.append(pd.to_datetime(data))
            except:
                datas.append(pd.NaT)
        
        # Criar DataFrame
        df_final = pd.DataFrame({
            'Data': datas,
            'Taxa_Desemprego': taxas
        })
        
        # Remover nulos
        df_final = df_final.dropna()
        
        # Adicionar governo
        df_final['Governo'] = df_final['Data'].dt.year.apply(self.classificar_governo)
        
        self.df_desemprego = df_final
        print(f"✅ Taxa de desemprego: {len(df_final)} registros processados")
        return df_final
    
    def processar_rendimento(self):
        """Processa o rendimento médio"""
        print("🔄 Processando rendimento médio...")
        
        df = self.dados['rendimento']
        
        # Filtrar dados do Brasil
        df_brasil = df[df['D4N'] == 'Brasil']
        
        # Extrair período e valor
        periodos = df_brasil['D1C'].astype(str).str.zfill(6)
        valores = df_brasil['V'].astype(str).str.replace(',', '.').str.replace('...', '')
        
        # Converter para numérico
        rendimentos = pd.to_numeric(valores, errors='coerce')
        
        # Converter período para data
        datas = []
        for p in periodos:
            try:
                ano = int(p[:4])
                trim = int(p[4:6])
                if trim == 1:
                    data = f"{ano}-01-01"
                elif trim == 2:
                    data = f"{ano}-04-01"
                elif trim == 3:
                    data = f"{ano}-07-01"
                else:
                    data = f"{ano}-10-01"
                datas.append(pd.to_datetime(data))
            except:
                datas.append(pd.NaT)
        
        # Criar DataFrame
        df_final = pd.DataFrame({
            'Data': datas,
            'Rendimento_Medio': rendimentos
        })
        
        df_final = df_final.dropna()
        df_final['Governo'] = df_final['Data'].dt.year.apply(self.classificar_governo)
        
        self.df_rendimento = df_final
        print(f"✅ Rendimento médio: {len(df_final)} registros processados")
        return df_final
    
    def classificar_governo(self, ano):
        """Classifica o ano por governo"""
        for governo, (ano_inicio, ano_fim) in self.governos.items():
            if ano_inicio <= ano <= ano_fim:
                return governo
        return 'Outro'
    
    