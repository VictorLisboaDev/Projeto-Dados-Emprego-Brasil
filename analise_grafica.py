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
        
        # Adicionar linhas verticais para mudanças de governo
        for governo, (ano, _) in [('Dilma', (2012,)), ('Temer', (2016,)), 
                                   ('Bolsonaro', (2019,)), ('Lula', (2023,))]:
            ax.axvline(x=pd.Timestamp(f'{ano}-01-01'), 
                      color='gray', linestyle='--', alpha=0.3)
        
        # Adicionar linha de média geral
        media_geral = self.df['Taxa_Desemprego'].mean()
        ax.axhline(y=media_geral, color='black', linestyle=':', 
                  alpha=0.6, linewidth=1.5, label=f'Média Geral: {media_geral:.1f}%')
        
        # Adicionar área de tendência
        z = np.polyfit(self.df['Data'].map(pd.Timestamp.toordinal), 
                      self.df['Taxa_Desemprego'], 3)
        p = np.poly1d(z)
        x_trend = self.df['Data']
        y_trend = p(x_trend.map(pd.Timestamp.toordinal))
        ax.plot(x_trend, y_trend, 'k--', alpha=0.5, linewidth=2, 
               label='Tendência Polinomial')
        
        # Configurações do gráfico
        ax.set_title('Evolução da Taxa de Desemprego no Brasil (2012-2026)', 
                    fontsize=18, fontweight='bold')
        ax.set_xlabel('Data', fontsize=14)
        ax.set_ylabel('Taxa de Desemprego (%)', fontsize=14)
        ax.legend(loc='upper left', fontsize=12)
        ax.grid(True, alpha=0.3)
        
        # Formatar datas
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
        ax.xaxis.set_major_locator(mdates.YearLocator())
        
        # Ajustar limites
        ax.set_xlim(self.df['Data'].min(), self.df['Data'].max())
        ax.set_ylim(0, max(self.df['Taxa_Desemprego']) * 1.15)
        
        plt.tight_layout()
        plt.savefig('1_evolucao_completa.png', dpi=300, bbox_inches='tight')
        plt.show()
        print("✅ Gráfico salvo: '1_evolucao_completa.png'")
    
    def grafico_comparativo_governos(self):
        """Gráfico 2: Comparação entre governos"""
        print("\n📊 Gerando gráfico comparativo entre governos...")
        
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        axes = axes.flatten()
        
        # Preparar dados
        governos = ['Dilma', 'Temer', 'Bolsonaro', 'Lula']
        
        for idx, governo in enumerate(governos):
            ax = axes[idx]
            dados = self.df[self.df['Governo'] == governo]
            
            if len(dados) > 0:
                # Histograma
                ax.hist(dados['Taxa_Desemprego'], bins=10, 
                       color=CORES[governo], alpha=0.7, edgecolor='black')
                
                # Estatísticas
                media = dados['Taxa_Desemprego'].mean()
                mediana = dados['Taxa_Desemprego'].median()
                std = dados['Taxa_Desemprego'].std()
                
                ax.axvline(media, color='red', linestyle='--', 
                          linewidth=2, label=f'Média: {media:.1f}%')
                ax.axvline(mediana, color='green', linestyle=':', 
                          linewidth=2, label=f'Mediana: {mediana:.1f}%')
                
                ax.set_title(f'{governo} ({self.df[self.df["Governo"] == governo]["Ano"].min()}-'
                           f'{self.df[self.df["Governo"] == governo]["Ano"].max()})', 
                           fontsize=14, fontweight='bold')
                ax.set_xlabel('Taxa de Desemprego (%)')
                ax.set_ylabel('Frequência')
                ax.legend()
                ax.grid(True, alpha=0.3)
        
        plt.suptitle('Distribuição da Taxa de Desemprego por Governo', 
                    fontsize=18, fontweight='bold')
        plt.tight_layout()
        plt.savefig('2_comparativo_governos.png', dpi=300, bbox_inches='tight')
        plt.show()
        print("✅ Gráfico salvo: '2_comparativo_governos.png'")
    
    def grafico_boxplot_governos(self):
        """Gráfico 3: Boxplot comparativo"""
        print("\n📊 Gerando boxplot comparativo...")
        
        fig, ax = plt.subplots(figsize=(14, 8))
        
        # Criar boxplot
        data = [self.df[self.df['Governo'] == gov]['Taxa_Desemprego'] 
                for gov in ['Dilma', 'Temer', 'Bolsonaro', 'Lula']]
        
        bp = ax.boxplot(data, patch_artist=True, widths=0.6)