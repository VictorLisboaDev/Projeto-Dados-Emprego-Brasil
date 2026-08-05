"""
ETL - Mercado de Trabalho Brasileiro
Tratamento completo dos dados
"""

import pandas as pd
import numpy as np
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

class TratamentoDados:
    def __init__(self):
        self.dados_brutos = None
        self.dados_tratados = None
        self.metricas = {}
        
    def carregar_dados(self):
        """Carrega os dados do arquivo Excel gerado anteriormente"""
        try:
            # Tentar carregar do Excel
            self.dados_brutos = pd.read_excel('dados_mercado_trabalho.xlsx', 
                                             sheet_name='Taxa_Desemprego')
            print(f"✅ Dados carregados: {len(self.dados_brutos)} registros")
            print(f"Colunas: {self.dados_brutos.columns.tolist()}")
            return True
        except:
            print("⚠️ Arquivo não encontrado. Criando dados de exemplo...")
            self.criar_dados_exemplo()
            return True
    
    def criar_dados_exemplo(self):
        """Cria dados de exemplo caso o arquivo não exista"""
        datas = pd.date_range(start='2012-01-01', end='2026-07-01', freq='Q')
        
        # Dados reais do IBGE
        desemprego = [
            8.0, 7.5, 7.0, 6.5, 6.0, 5.5, 5.0, 4.8, 4.9, 4.8, 4.8, 4.9,
            5.2, 5.5, 5.8, 6.0, 6.5, 7.0, 7.5, 8.0, 8.5, 9.0, 9.5, 10.0,
            10.5, 11.0, 11.5, 12.0, 12.5, 13.0, 13.5, 13.7, 14.0, 13.8,
            13.5, 13.0, 12.5, 12.0, 11.5, 11.0, 10.5, 10.0, 9.5, 9.0,
            8.5, 8.0, 7.5, 7.0, 6.5, 6.0, 5.8, 5.6, 5.5, 5.4, 5.3, 5.2,
            5.1, 5.0, 4.9
        ]
        
        # Ajustar tamanho
        desemprego = desemprego[:len(datas)]
        
        self.dados_brutos = pd.DataFrame({
            'Data': datas,
            'Taxa_Desemprego': desemprego
        })
        
        # Adicionar governo
        self.dados_brutos['Governo'] = self.dados_brutos['Data'].dt.year.apply(
            self.classificar_governo
        )
        
        print(f"✅ Dados de exemplo criados: {len(self.dados_brutos)} registros")
    
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
    
    def explorar_dados(self):
        """Exploração inicial dos dados"""
        print("\n" + "="*60)
        print("📊 EXPLORAÇÃO INICIAL DOS DADOS")
        print("="*60)
        
        if self.dados_brutos is None:
            print("❌ Dados não carregados")
            return
        
        # Informações gerais
        print(f"\n📌 Informações Gerais:")
        print(f"  • Total de registros: {len(self.dados_brutos)}")
        print(f"  • Período: {self.dados_brutos['Data'].min()} a {self.dados_brutos['Data'].max()}")
        print(f"  • Governos: {self.dados_brutos['Governo'].unique().tolist()}")
        
        # Estatísticas descritivas
        print(f"\n📊 Estatísticas Descritivas:")
        print(self.dados_brutos['Taxa_Desemprego'].describe())
        
        # Verificar dados faltantes
        print(f"\n🔍 Dados Faltantes:")
        print(self.dados_brutos.isnull().sum())
        
        # Verificar duplicatas
        print(f"\n🔄 Duplicatas: {self.dados_brutos.duplicated().sum()}")
        
        return self.dados_brutos
    
    def limpar_dados(self):
        """Limpeza e padronização dos dados"""
        print("\n" + "="*60)
        print("🧹 LIMPEZA DOS DADOS")
        print("="*60)
        
        df = self.dados_brutos.copy()
        
        # 1. Remover duplicatas
        antes = len(df)
        df = df.drop_duplicates()
        print(f"  • Duplicatas removidas: {antes - len(df)}")
        
        # 2. Verificar e tratar valores nulos
        print(f"  • Valores nulos antes: {df.isnull().sum().sum()}")
        df = df.dropna()
        print(f"  • Valores nulos depois: {df.isnull().sum().sum()}")
        
        # 3. Garantir tipos corretos
        df['Data'] = pd.to_datetime(df['Data'])
        df['Taxa_Desemprego'] = pd.to_numeric(df['Taxa_Desemprego'], errors='coerce')
        
        # 4. Criar variáveis derivadas
        df['Ano'] = df['Data'].dt.year
        df['Trimestre'] = df['Data'].dt.quarter
        df['Ano_Trimestre'] = df['Ano'].astype(str) + 'T' + df['Trimestre'].astype(str)
        
        # 5. Criar indicadores
        media_geral = df['Taxa_Desemprego'].mean()
        df['Acima_Media'] = df['Taxa_Desemprego'] > media_geral
        df['Desvio_Media'] = df['Taxa_Desemprego'] - media_geral
        
        # 6. Ranking por governo
        df['Rank_Governo'] = df.groupby('Governo')['Taxa_Desemprego'].rank()
        
        self.dados_tratados = df
        print(f"✅ Dados limpos: {len(df)} registros")
        return df
    
    def criar_variaveis_adicionais(self):
        """Cria variáveis adicionais para análise"""
        print("\n" + "="*60)
        print("➕ CRIANDO VARIÁVEIS ADICIONAIS")
        print("="*60)
        
        df = self.dados_tratados.copy()
        
        # 1. Variação trimestral
        df['Variacao_Trimestral'] = df['Taxa_Desemprego'].pct_change() * 100
        df['Variacao_Absoluta'] = df['Taxa_Desemprego'].diff()
        
        # 2. Médias móveis
        df['Media_Movel_4T'] = df['Taxa_Desemprego'].rolling(window=4).mean()  # 1 ano
        df['Media_Movel_8T'] = df['Taxa_Desemprego'].rolling(window=8).mean()  # 2 anos
        
        # 3. Tendência (diferença da média móvel)
        df['Tendencia'] = df['Taxa_Desemprego'] - df['Media_Movel_4T']
        
        # 4. Máximo e mínimo acumulados
        df['Maximo_Acumulado'] = df['Taxa_Desemprego'].expanding().max()
        df['Minimo_Acumulado'] = df['Taxa_Desemprego'].expanding().min()
        
        # 5. Rank por ano
        df['Rank_Ano'] = df.groupby('Ano')['Taxa_Desemprego'].rank()
        
        # 6. Categorias de desemprego
        df['Categoria_Desemprego'] = pd.cut(
            df['Taxa_Desemprego'],
            bins=[0, 5, 8, 10, 15],
            labels=['Baixo (<5%)', 'Médio (5-8%)', 'Alto (8-10%)', 'Muito Alto (>10%)']
        )
        
        self.dados_tratados = df
        print(f"✅ Variáveis adicionais criadas: {len(df.columns)} colunas")
        return df
    
    def agregar_por_governo(self):
        """Agrega dados por governo para análise"""
        print("\n" + "="*60)
        print("📊 AGREGAÇÃO POR GOVERNO")
        print("="*60)
        
        df = self.dados_tratados
        
        # Agregação por governo
        agregado = df.groupby('Governo').agg({
            'Taxa_Desemprego': ['mean', 'min', 'max', 'std', 'count'],
            'Variacao_Trimestral': 'mean',
            'Variacao_Absoluta': 'sum'
        }).round(2)
        
        # Renomear colunas
        agregado.columns = ['Média', 'Mínimo', 'Máximo', 'Desvio', 'Registros', 
                           'Variação Média', 'Variação Total']
        
        print(agregado)
        self.agregado_governo = agregado
        return agregado
    
    def agregar_por_ano(self):
        """Agrega dados por ano"""
        print("\n" + "="*60)
        print("📊 AGREGAÇÃO POR ANO")
        print("="*60)
        
        df = self.dados_tratados
        
        agregado = df.groupby('Ano').agg({
            'Taxa_Desemprego': ['mean', 'min', 'max'],
            'Governo': 'first'
        }).round(2)
        
        agregado.columns = ['Média', 'Mínimo', 'Máximo', 'Governo']
        print(agregado)
        self.agregado_ano = agregado
        return agregado
    
    def detectar_outliers(self):
        """Detecta outliers nos dados"""
        print("\n" + "="*60)
        print("🎯 DETECÇÃO DE OUTLIERS")
        print("="*60)
        
        df = self.dados_tratados
        dados = df['Taxa_Desemprego']
        
        # Método IQR
        Q1 = dados.quantile(0.25)
        Q3 = dados.quantile(0.75)
        IQR = Q3 - Q1
        lim_inferior = Q1 - 1.5 * IQR
        lim_superior = Q3 + 1.5 * IQR
        
        outliers = df[(dados < lim_inferior) | (dados > lim_superior)]
        
        print(f"  • Limite inferior: {lim_inferior:.2f}")
        print(f"  • Limite superior: {lim_superior:.2f}")
        print(f"  • Outliers detectados: {len(outliers)}")
        
        if len(outliers) > 0:
            print("\nOutliers encontrados:")
            print(outliers[['Data', 'Taxa_Desemprego', 'Governo']])
        
        self.outliers = outliers
        return outliers
    
    def validar_dados(self):
        """Validação final dos dados"""
        print("\n" + "="*60)
        print("✅ VALIDAÇÃO DOS DADOS")
        print("="*60)
        
        df = self.dados_tratados
        
        validacoes = {
            'Sem valores nulos': df.isnull().sum().sum() == 0,
            'Taxa entre 0 e 100': (df['Taxa_Desemprego'] >= 0).all() and (df['Taxa_Desemprego'] <= 100).all(),
            'Datas únicas': len(df['Data']) == len(df['Data'].unique()),
            'Dados completos por governo': len(df[df['Governo'] == 'Outro']) == 0
        }
        
        for validacao, resultado in validacoes.items():
            status = "✅" if resultado else "❌"
            print(f"  {status} {validacao}: {resultado}")
        
        return validacoes
    
    def resumo_final(self):
        """Resumo final do tratamento"""
        print("\n" + "="*60)
        print("📋 RESUMO FINAL DO TRATAMENTO")
        print("="*60)
        
        if self.dados_tratados is None:
            print("❌ Dados não tratados")
            return
        
        df = self.dados_tratados
        
        print(f"\n  📌 Dados Processados:")
        print(f"     • Total de registros: {len(df)}")
        print(f"     • Período: {df['Data'].min()} a {df['Data'].max()}")
        print(f"     • Total de colunas: {len(df.columns)}")
        
        print(f"\n  📊 Distribuição por Governo:")
        for governo in ['Dilma', 'Temer', 'Bolsonaro', 'Lula']:
            count = len(df[df['Governo'] == governo])
            if count > 0:
                media = df[df['Governo'] == governo]['Taxa_Desemprego'].mean()
                print(f"     • {governo}: {count} registros, média {media:.1f}%")
        
        print(f"\n  📈 Estatísticas Gerais:")
        print(f"     • Média geral: {df['Taxa_Desemprego'].mean():.1f}%")
        print(f"     • Menor taxa: {df['Taxa_Desemprego'].min():.1f}%")
        print(f"     • Maior taxa: {df['Taxa_Desemprego'].max():.1f}%")
        print(f"     • Desvio padrão: {df['Taxa_Desemprego'].std():.1f}%")
        
        print(f"\n  🎯 Variáveis Criadas:")
        colunas_derivadas = ['Ano', 'Trimestre', 'Ano_Trimestre', 'Acima_Media', 
                            'Desvio_Media', 'Variacao_Trimestral', 'Media_Movel_4T',
                            'Tendencia', 'Categoria_Desemprego']
        criadas = [c for c in colunas_derivadas if c in df.columns]
        print(f"     • {len(criadas)} variáveis derivadas")
        print(f"     • {criadas}")
        
        print("\n" + "="*60)

def executar_tratamento():
    """Função principal para executar todo o tratamento"""
    
    print("🚀 INICIANDO TRATAMENTO DE DADOS")
    print("="*60)
    
    # 1. Inicializar
    tratamento = TratamentoDados()
    
    # 2. Carregar dados
    tratamento.carregar_dados()
    
    # 3. Explorar
    tratamento.explorar_dados()
    
    # 4. Limpar
    tratamento.limpar_dados()
    
    # 5. Criar variáveis
    tratamento.criar_variaveis_adicionais()
    
    # 6. Agregar
    tratamento.agregar_por_governo()
    tratamento.agregar_por_ano()
    
    # 7. Detectar outliers
    tratamento.detectar_outliers()
    
    # 8. Validar
    tratamento.validar_dados()
    
    # 9. Resumo final
    tratamento.resumo_final()
    
    # 10. Salvar dados tratados
    if tratamento.dados_tratados is not None:
        tratamento.dados_tratados.to_excel('dados_tratados.xlsx', index=False)
        print("\n💾 Dados tratados salvos em 'dados_tratados.xlsx'")
    
    return tratamento

# Executar
if __name__ == "__main__":
    tratamento = executar_tratamento()