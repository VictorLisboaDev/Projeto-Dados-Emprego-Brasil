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

 # Cores
        for patch, cor in zip(bp['boxes'], ['#1f77b4', '#ff7f0e', '#d62728', '#2ca02c']):
            patch.set_facecolor(cor)
            patch.set_alpha(0.7)
        
        ax.set_xticklabels(['Dilma', 'Temer', 'Bolsonaro', 'Lula'])
        ax.set_ylabel('Taxa de Desemprego (%)', fontsize=14)
        ax.set_xlabel('Governo', fontsize=14)
        ax.set_title('Distribuição da Taxa de Desemprego por Governo', 
                    fontsize=18, fontweight='bold')
        ax.grid(True, alpha=0.3)
        
        # Adicionar pontos para visualização
        for i, gov in enumerate(['Dilma', 'Temer', 'Bolsonaro', 'Lula']):
            dados = self.df[self.df['Governo'] == gov]['Taxa_Desemprego']
            x = np.random.normal(i+1, 0.04, len(dados))
            ax.scatter(x, dados, alpha=0.3, color='black', s=30)
        
        plt.tight_layout()
        plt.savefig('3_boxplot_governos.png', dpi=300, bbox_inches='tight')
        plt.show()
        print("✅ Gráfico salvo: '3_boxplot_governos.png'")
    
    def grafico_correlacao(self):
        """Gráfico 4: Matriz de correlação"""
        print("\n📊 Gerando matriz de correlação...")
        
        # Selecionar variáveis
        vars_corr = ['Taxa_Desemprego', 'Rendimento_Medio', 'Informalidade', 'Empregos_Formais']
        corr_matrix = self.df[vars_corr].corr()
        
        # Criar figura
        fig, ax = plt.subplots(figsize=(10, 8))
        
        # Heatmap
        im = ax.imshow(corr_matrix, cmap='coolwarm', vmin=-1, vmax=1)
        
        # Adicionar valores
        for i in range(len(vars_corr)):
            for j in range(len(vars_corr)):
                text = ax.text(j, i, f'{corr_matrix.iloc[i, j]:.2f}',
                             ha='center', va='center', color='black' if abs(corr_matrix.iloc[i, j]) < 0.7 else 'white',
                             fontsize=12, fontweight='bold')
        
        ax.set_xticks(range(len(vars_corr)))
        ax.set_yticks(range(len(vars_corr)))
        ax.set_xticklabels(vars_corr, fontsize=12)
        ax.set_yticklabels(vars_corr, fontsize=12)
        
        plt.colorbar(im, ax=ax, label='Correlação')
        ax.set_title('Matriz de Correlação do Mercado de Trabalho', 
                    fontsize=18, fontweight='bold')
        
        plt.tight_layout()
        plt.savefig('4_matriz_correlacao.png', dpi=300, bbox_inches='tight')
        plt.show()
        print("✅ Gráfico salvo: '4_matriz_correlacao.png'")
    
    def grafico_scatter(self):
        """Gráfico 5: Gráficos de dispersão"""
        print("\n📊 Gerando gráficos de dispersão...")
        
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        
        # 1. Desemprego vs Rendimento
        ax1 = axes[0, 0]
        scatter1 = ax1.scatter(self.df['Rendimento_Medio'], 
                             self.df['Taxa_Desemprego'],
                             c=self.df['Ano'], cmap='viridis', 
                             s=50, alpha=0.6)
        ax1.set_xlabel('Rendimento Médio (R$)', fontsize=12)
        ax1.set_ylabel('Taxa de Desemprego (%)', fontsize=12)
        ax1.set_title('Desemprego vs Rendimento', fontsize=14, fontweight='bold')
        ax1.grid(True, alpha=0.3)
        plt.colorbar(scatter1, ax=ax1, label='Ano')
        
        # 2. Desemprego vs Informalidade
        ax2 = axes[0, 1]
        scatter2 = ax2.scatter(self.df['Informalidade'], 
                             self.df['Taxa_Desemprego'],
                             c=self.df['Ano'], cmap='plasma', 
                             s=50, alpha=0.6)
        ax2.set_xlabel('Informalidade (%)', fontsize=12)
        ax2.set_ylabel('Taxa de Desemprego (%)', fontsize=12)
        ax2.set_title('Desemprego vs Informalidade', fontsize=14, fontweight='bold')
        ax2.grid(True, alpha=0.3)
        plt.colorbar(scatter2, ax=ax2, label='Ano')
        
        # 3. Desemprego vs Empregos Formais
        ax3 = axes[1, 0]
        scatter3 = ax3.scatter(self.df['Empregos_Formais'], 
                             self.df['Taxa_Desemprego'],
                             c=self.df['Ano'], cmap='inferno', 
                             s=50, alpha=0.6)
        ax3.set_xlabel('Empregos Formais (milhões)', fontsize=12)
        ax3.set_ylabel('Taxa de Desemprego (%)', fontsize=12)
        ax3.set_title('Desemprego vs Empregos Formais', fontsize=14, fontweight='bold')
        ax3.grid(True, alpha=0.3)
        plt.colorbar(scatter3, ax=ax3, label='Ano')
        
        # 4. Múltiplas variáveis
        ax4 = axes[1, 1]
        for governo in ['Dilma', 'Temer', 'Bolsonaro', 'Lula']:
            dados = self.df[self.df['Governo'] == governo]
            if len(dados) > 0:
                ax4.scatter(dados['Rendimento_Medio'], 
                          dados['Taxa_Desemprego'],
                          label=governo, color=CORES[governo],
                          s=50, alpha=0.6)
        
        ax4.set_xlabel('Rendimento Médio (R$)', fontsize=12)
        ax4.set_ylabel('Taxa de Desemprego (%)', fontsize=12)
        ax4.set_title('Desemprego vs Rendimento por Governo', fontsize=14, fontweight='bold')
        ax4.legend()
        ax4.grid(True, alpha=0.3)
        
        plt.suptitle('Análise de Correlação do Mercado de Trabalho', 
                    fontsize=18, fontweight='bold')
        plt.tight_layout()
        plt.savefig('5_scatter_plots.png', dpi=300, bbox_inches='tight')
        plt.show()
        print("✅ Gráfico salvo: '5_scatter_plots.png'")
    
    def grafico_tendencias(self):
        """Gráfico 6: Tendências e projeções"""
        print("\n📊 Gerando gráfico de tendências...")
        
        fig, ax = plt.subplots(figsize=(16, 8))

# Dados por governo
        for governo in ['Dilma', 'Temer', 'Bolsonaro', 'Lula']:
            dados = self.df[self.df['Governo'] == governo]
            if len(dados) > 1:
                # Dados
                ax.plot(dados['Data'], dados['Taxa_Desemprego'],
                       'o-', color=CORES[governo], label=governo,
                       linewidth=2, markersize=6)
                
                # Linha de tendência
                x = np.arange(len(dados))
                y = dados['Taxa_Desemprego'].values
                z = np.polyfit(x, y, 1)
                p = np.poly1d(z)
                
                x_trend = np.linspace(0, len(x)-1, 50)
                y_trend = p(x_trend)
                
                x_dates = [dados['Data'].iloc[0] + 
                          (dados['Data'].iloc[-1] - dados['Data'].iloc[0]) * (t/len(x_trend))
                          for t in range(len(x_trend))]
                
                ax.plot(x_dates, y_trend, '--', color=CORES[governo], 
                       alpha=0.5, linewidth=1.5)
        
        # Adicionar área de projeção
        ultimos_dados = self.df.iloc[-8:]
        x_pred = np.arange(len(ultimos_dados), len(ultimos_dados) + 4)
        z_pred = np.polyfit(np.arange(len(ultimos_dados)), 
                          ultimos_dados['Taxa_Desemprego'], 1)
        p_pred = np.poly1d(z_pred)
        y_pred = p_pred(x_pred)
        
        datas_pred = pd.date_range(start=ultimos_dados['Data'].iloc[-1] + pd.Timedelta(days=90), 
                                  periods=4, freq='Q')
        
        ax.plot(datas_pred, y_pred, 'r--', linewidth=2, label='Projeção')
        ax.fill_between(datas_pred, y_pred - 0.5, y_pred + 0.5, 
                       alpha=0.2, color='red', label='Intervalo de Confiança')
        
        ax.set_title('Tendências da Taxa de Desemprego por Governo', 
                    fontsize=18, fontweight='bold')
        ax.set_xlabel('Data', fontsize=14)
        ax.set_ylabel('Taxa de Desemprego (%)', fontsize=14)
        ax.legend(loc='best', fontsize=12)
        ax.grid(True, alpha=0.3)
        
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
        ax.xaxis.set_major_locator(mdates.YearLocator())
        
        plt.tight_layout()
        plt.savefig('6_tendencias.png', dpi=300, bbox_inches='tight')
        plt.show()
        print("✅ Gráfico salvo: '6_tendencias.png'")
    
    def grafico_radar_governos(self):
        """Gráfico 7: Radar comparativo"""
        print("\n📊 Gerando gráfico radar...")  

         # Calcular métricas por governo
        metricas = {}
        for governo in ['Dilma', 'Temer', 'Bolsonaro', 'Lula']:
            dados = self.df[self.df['Governo'] == governo]
            if len(dados) > 0:
                metricas[governo] = {
                    'Média Desemprego': dados['Taxa_Desemprego'].mean(),
                    'Mínimo': dados['Taxa_Desemprego'].min(),
                    'Máximo': dados['Taxa_Desemprego'].max(),
                    'Estabilidade': 100 - dados['Taxa_Desemprego'].std(),
                    'Rendimento Médio': dados['Rendimento_Medio'].mean() / 100
                }
        
        # Preparar dados para radar
        categories = list(metricas['Dilma'].keys())
        values = {gov: [metricas[gov][cat] for cat in categories] 
                 for gov in metricas.keys()}
        
        # Normalizar para 0-100
        for cat in categories:
            max_val = max([metricas[gov][cat] for gov in metricas.keys()])
            if max_val > 0:
                for gov in metricas.keys():
                    values[gov][categories.index(cat)] = (metricas[gov][cat] / max_val) * 100
        
        # Plotar radar
        angles = np.linspace(0, 2 * np.pi, len(categories), endpoint=False).tolist()
        angles += angles[:1]
        
        fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(projection='polar'))
        
        for governo, cor in CORES.items():
            if governo in values:
                vals = values[governo]
                vals += vals[:1]
                ax.plot(angles, vals, 'o-', linewidth=2, label=governo, color=cor)
                ax.fill(angles, vals, alpha=0.1, color=cor)
        
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(categories, fontsize=12)
        ax.set_ylim(0, 100)
        ax.set_title('Radar Comparativo por Governo', fontsize=18, fontweight='bold', pad=20)
        ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.0))
        ax.grid(True)
        
        plt.tight_layout()
        plt.savefig('7_radar_governos.png', dpi=300, bbox_inches='tight')
        plt.show()
        print("✅ Gráfico salvo: '7_radar_governos.png'")
    
    def grafico_sazonalidade(self):
        """Gráfico 8: Análise sazonal"""
        print("\n📊 Gerando análise sazonal...")
        
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        
        # 1. Médias por trimestre
        ax1 = axes[0, 0]
        medias_trim = self.df.groupby('Trimestre')['Taxa_Desemprego'].mean()
        ax1.bar(medias_trim.index, medias_trim.values, 
               color=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728'])
        ax1.set_xlabel('Trimestre', fontsize=12)
        ax1.set_ylabel('Taxa Média de Desemprego (%)', fontsize=12)
        ax1.set_title('Média por Trimestre', fontsize=14, fontweight='bold')
        ax1.grid(True, alpha=0.3)
        
        # 2. Boxplot por trimestre
        ax2 = axes[0, 1]
        self.df.boxplot(column='Taxa_Desemprego', by='Trimestre', ax=ax2)
        ax2.set_title('Distribuição por Trimestre', fontsize=14, fontweight='bold')
        ax2.set_xlabel('Trimestre', fontsize=12)
        ax2.set_ylabel('Taxa de Desemprego (%)', fontsize=12)
        
        # 3. Variação sazonal
        ax3 = axes[1, 0]
        for governo in ['Dilma', 'Temer', 'Bolsonaro', 'Lula']:
            dados = self.df[self.df['Governo'] == governo]
            if len(dados) > 0:
                medias = dados.groupby('Trimestre')['Taxa_Desemprego'].mean()
                ax3.plot(medias.index, medias.values, 'o-', 
                        label=governo, color=CORES[governo], linewidth=2)
        
        ax3.set_xlabel('Trimestre', fontsize=12)
        ax3.set_ylabel('Taxa de Desemprego (%)', fontsize=12)
        ax3.set_title('Sazonalidade por Governo', fontsize=14, fontweight='bold')
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        
        # 4. Mapa de calor sazonal
        ax4 = axes[1, 1]
        pivot = self.df.pivot_table(index='Ano', columns='Trimestre', 
                                   values='Taxa_Desemprego', aggfunc='mean')
        im = ax4.imshow(pivot, cmap='RdYlGn_r', aspect='auto')
        ax4.set_xticks(range(len(pivot.columns)))
        ax4.set_xticklabels(pivot.columns)
        ax4.set_yticks(range(len(pivot.index)))
        ax4.set_yticklabels(pivot.index)
        ax4.set_xlabel('Trimestre', fontsize=12)
        ax4.set_ylabel('Ano', fontsize=12)
        ax4.set_title('Mapa de Calor Sazonal', fontsize=14, fontweight='bold')
        plt.colorbar(im, ax=ax4, label='Taxa de Desemprego (%)')
        
        plt.suptitle('Análise de Sazonalidade do Desemprego', 
                    fontsize=18, fontweight='bold')
        plt.tight_layout()
        plt.savefig('8_sazonalidade.png', dpi=300, bbox_inches='tight')
        plt.show()
        print("✅ Gráfico salvo: '8_sazonalidade.png'")
    
    def grafico_indicadores_multiplos(self):
        """Gráfico 9: Múltiplos indicadores"""
        print("\n📊 Gerando gráfico de múltiplos indicadores...")
        
        fig, axes = plt.subplots(3, 1, figsize=(16, 14))
        
        # 1. Taxa de Desemprego
        ax1 = axes[0]
        for governo in ['Dilma', 'Temer', 'Bolsonaro', 'Lula']:
            dados = self.df[self.df['Governo'] == governo]
            if len(dados) > 0:
                ax1.plot(dados['Data'], dados['Taxa_Desemprego'],
                        label=governo, color=CORES[governo],
                        linewidth=2.5)
        ax1.set_ylabel('Taxa de Desemprego (%)', fontsize=13)
        ax1.set_title('Taxa de Desemprego', fontsize=15, fontweight='bold')
        ax1.legend(loc='upper right')
        ax1.grid(True, alpha=0.3)
        ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
        
        # 2. Rendimento Médio
        ax2 = axes[1]
        ax2.plot(self.df['Data'], self.df['Rendimento_Medio'], 
                color='purple', linewidth=2.5)
        ax2.fill_between(self.df['Data'], self.df['Rendimento_Medio'] - 20,
                        self.df['Rendimento_Medio'] + 20, alpha=0.2, color='purple')
        ax2.set_ylabel('Rendimento Médio (R$)', fontsize=13)
        ax2.set_title('Rendimento Médio Real', fontsize=15, fontweight='bold')
        ax2.grid(True, alpha=0.3)
        ax2.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
        
        # 3. Informalidade e Empregos Formais
        ax3 = axes[2]
        ax3.plot(self.df['Data'], self.df['Informalidade'], 
                label='Informalidade', color='orange', linewidth=2.5)
        ax3.plot(self.df['Data'], self.df['Empregos_Formais'], 
                label='Empregos Formais (milhões)', color='green', linewidth=2.5)
        ax3.set_ylabel('Percentual / Milhões', fontsize=13)
        ax3.set_xlabel('Data', fontsize=13)
        ax3.set_title('Informalidade e Empregos Formais', fontsize=15, fontweight='bold')
        ax3.legend(loc='upper right')
        ax3.grid(True, alpha=0.3)
        ax3.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
        
        plt.suptitle('Evolução dos Indicadores do Mercado de Trabalho', 
                    fontsize=18, fontweight='bold')
        plt.tight_layout()
        plt.savefig('9_indicadores_multiplos.png', dpi=300, bbox_inches='tight')
        plt.show()
        print("✅ Gráfico salvo: '9_indicadores_multiplos.png'")
    
    def executar_todas_analises(self):
        """Executa todas as análises gráficas"""
        print("\n" + "="*60)
        print("🚀 INICIANDO ANÁLISE GRÁFICA COMPLETA")
        print("="*60)
        
        self.grafico_evolucao_completa()
        self.grafico_comparativo_governos()
        self.grafico_boxplot_governos()
        self.grafico_correlacao()
        self.grafico_scatter()
        self.grafico_tendencias()
        self.grafico_radar_governos()
        self.grafico_sazonalidade()
        self.grafico_indicadores_multiplos()
        
        print("\n" + "="*60)
        print("✅ ANÁLISE GRÁFICA CONCLUÍDA!")
        print("📁 Gráficos gerados:")
        print("  1_evolucao_completa.png")
        print("  2_comparativo_governos.png")
        print("  3_boxplot_governos.png")
        print("  4_matriz_correlacao.png")
        print("  5_scatter_plots.png")
        print("  6_tendencias.png")
        print("  7_radar_governos.png")
        print("  8_sazonalidade.png")
        print("  9_indicadores_multiplos.png")
        print("="*60)

# Executar
if __name__ == "__main__":
    analise = AnaliseGrafica()
    analise.executar_todas_analises()              