import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.patches import Patch
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')

# Configurações de estilo
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")
plt.rcParams['figure.figsize'] = (14, 8)
plt.rcParams['font.size'] = 12
plt.rcParams['axes.labelsize'] = 13
plt.rcParams['axes.titlesize'] = 15
plt.rcParams['legend.fontsize'] = 11
plt.rcParams['figure.titlesize'] = 16

# Cores personalizadas
CORES = {
    'Dilma': '#1f77b4',      # Azul
    'Temer': '#ff7f0e',      # Laranja
    'Bolsonaro': '#d62728',  # Vermelho
    'Lula': '#2ca02c',       # Verde
    'background': '#f8f9fa'
}

class AnaliseGrafica:
    def __init__(self):
        self.df = None
        self.carregar_dados()
        
    def carregar_dados(self):
        """Carrega ou cria os dados"""
        try:
            self.df = pd.read_excel('dados_tratados.xlsx')
            print(f"✅ Dados carregados: {len(self.df)} registros")
        except:
            print("⚠️ Criando dados para análise gráfica...")
            self.criar_dados()
    
    def criar_dados(self):
        """Cria dados de exemplo"""
        datas = pd.date_range(start='2012-01-01', end='2026-07-01', freq='Q')
        
        # Dados reais aproximados
        desemprego = np.array([
            8.0, 7.5, 7.0, 6.5, 6.0, 5.5, 5.0, 4.8, 4.9, 4.8, 4.8, 4.9,
            5.2, 5.5, 5.8, 6.0, 6.5, 7.0, 7.5, 8.0, 8.5, 9.0, 9.5, 10.0,
            10.5, 11.0, 11.5, 12.0, 12.5, 13.0, 13.5, 13.7, 14.0, 13.8,
            13.5, 13.0, 12.5, 12.0, 11.5, 11.0, 10.5, 10.0, 9.5, 9.0,
            8.5, 8.0, 7.5, 7.0, 6.5, 6.0, 5.8, 5.6, 5.5, 5.4, 5.3, 5.2,
            5.1, 5.0, 4.9
        ])[:len(datas)]
        
        # Variáveis adicionais
        rendimento = 2000 + (80 * np.arange(len(datas))) + np.random.normal(0, 30, len(datas))
        informalidade = 40 - 0.12 * np.arange(len(datas)) + np.random.normal(0, 1.5, len(datas))
        informalidade = np.clip(informalidade, 30, 45)
        empregos = 35 + 0.08 * np.arange(len(datas)) + np.random.normal(0, 1, len(datas))
        
        self.df = pd.DataFrame({
            'Data': datas,
            'Taxa_Desemprego': desemprego,
            'Rendimento_Medio': rendimento,
            'Informalidade': informalidade,
            'Empregos_Formais': empregos
        })
        
        self.df['Ano'] = self.df['Data'].dt.year
        self.df['Trimestre'] = self.df['Data'].dt.quarter
        self.df['Governo'] = self.df['Ano'].apply(self.classificar_governo)
        
        print(f"✅ Dados criados: {len(self.df)} registros")
    
    def classificar_governo(self, ano):
        """Classifica o ano por governo"""
        governos = {
            'Dilma': (2012, 2016),
            'Temer': (2016, 2018),
            'Bolsonaro': (2019, 2022),
            'Lula': (2023, 2026)
        }
        for governo, (ano_inicio, ano_fim) in governos.items():
            if ano_inicio <= ano <= ano_fim:
                return governo
        return 'Outro'
    
    def grafico_evolucao_completa(self):
        """Gráfico 1: Evolução completa da taxa de desemprego"""
        print("\n📈 Gerando gráfico de evolução completa...")
        
        fig, ax = plt.subplots(figsize=(16, 8))
        
        # Plotar dados por governo
        for governo in ['Dilma', 'Temer', 'Bolsonaro', 'Lula']:
            dados = self.df[self.df['Governo'] == governo]
            if len(dados) > 0:
                ax.plot(dados['Data'], dados['Taxa_Desemprego'],
                       label=governo, color=CORES[governo],
                       linewidth=2.5, marker='o', markersize=6)