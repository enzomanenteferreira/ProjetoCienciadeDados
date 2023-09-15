import pandas as pd
import numpy as np
import pathlib
import seaborn as sns
import matplotlib.pyplot as plt
import time
import pl

# cronometrar o tempo de execução do codigo
start_time = time.time()

meses = {'jan':1, 'fev':2, 'mar':3, 'abr':4, 'mai':5, 'jun':6,'jul':7, 'ago':8, 'set':9, 'out':10,'nov':11,'dez':12}

caminho_bases = pathlib.Path('datasets')

bases = []

# Percorrer todos os arquivos da pasta
for arquivo in caminho_bases.iterdir():
     nome_arquivo = arquivo.name
     if nome_arquivo[:3] in meses:
        mes = meses[arquivo.name[:3]]
        ano = int((arquivo.name[-8:]).replace('.csv',''))
        df = pd.read_csv(caminho_bases / arquivo.name, low_memory= False)
        df['ano'] = ano
        df['mes'] = mes

        bases.append(df)

base_airbnb = pd.concat(bases, ignore_index=True)
#print(base_airbnb)

#como temos muitas colunas, nosso modelo pode acabar ficando muito lento.
#alem disso, uma analise rapida permite ver que varias colunas não são necessarias para o nosso modelo de previsão.
#por isso, vamos excluir algumas colunas da nossa base - tipos de colunos que serão excluidas:
#1 : IDs, links e informaçoes não relevantes para o modelo
#2 : colunas repetidas ou extremamente parecidas com outra(que dão a mesma informaçao para o modelo). Ex: Data x Ano/mes
#3 : colunas preenchidas com texto livre -> nao rodaremos nenhuma analise de palavras ou algo do tipo
#4 : colunas em que todos ou quase todos os valores são iguais

# para isso, vamos criar um arquivo em excel com os 1000 primeiros registros e fazer uma analise qualitativa
#print(list(base_airbnb.columns))
base_airbnb.head(1000).to_csv('primeiros_registros.csv',sep =';')

# Depois da analise qualitativa das colunas, levando em conta os criterios explicados acima, ficamos com as seguintes colunas
colunas = ['host_response_time','host_response_rate','host_is_superhost','host_listings_count','latitude','longitude','property_type','room_type','accommodates','bathrooms','bedrooms','beds','bed_type','amenities','price','security_deposit','cleaning_fee','guests_included','extra_people','minimum_nights','maximum_nights','number_of_reviews','review_scores_rating','review_scores_accuracy','review_scores_cleanliness','review_scores_checkin','review_scores_communication','review_scores_location','review_scores_value','instant_bookable','is_business_travel_ready','cancellation_policy','ano','mes']

base_airbnb = base_airbnb.loc[:, colunas]
#print(base_airbnb)
#print(list(base_airbnb.columns))

# tratar valores faltando
# As colunas com mais de 300.000 valores NaN foram excluidas da analise, devido a grande disparidade em dados faltantes
for coluna in base_airbnb:
   if base_airbnb[coluna].isnull().sum() > 300000:
       base_airbnb = base_airbnb.drop(coluna, axis=1)
#print(base_airbnb.isnull().sum())


# exclui as linhas com valor NaN
base_airbnb = base_airbnb.dropna()
#print(base_airbnb.isnull().sum())


# preço e extra people estão sendo reconhecidos como objeto ao inves de float, portanto deve-se mudar o tipo de variavel da coluna
#price
base_airbnb['price'] = base_airbnb['price'].str.replace('$','')
base_airbnb['price'] = base_airbnb['price'].str.replace(',','')
base_airbnb['price'] = base_airbnb['price'].astype(np.float32, copy=False)

# extra people
base_airbnb['extra_people'] = base_airbnb['extra_people'].str.replace('$','')
base_airbnb['extra_people'] = base_airbnb['extra_people'].str.replace(',','')
base_airbnb['extra_people'] = base_airbnb['extra_people'].astype(np.float32, copy=False)

#print(base_airbnb.dtypes)


#  plotar o grafico de correlação
#plt.figure(figsize=(15,10))
#sns.heatmap(base_airbnb.corr(numeric_only=True),annot = True,cmap='Greens')
#plt.show()

# Definição de funções para analise de outliers
def limites(coluna):
    q1 = coluna.quantile(0.25)
    q3 = coluna.quantile(0.75)
    amplitude = q3 - q1
    return q1 - 1.5 * amplitude, q3 + 1.5 * amplitude

def excluir_outliers(df,nome_coluna):
    qntd_linhas = df.shape[0]
    lim_inf, lim_sup = limites(df[nome_coluna])
    df = df.loc[(df[nome_coluna] >= lim_inf) & (df[nome_coluna] <= lim_sup), :]
    linhas_removidas = qntd_linhas - df.shape[0]
    return df, linhas_removidas

def diagrama_caixa(coluna):
    fig, (ax1,ax2) = plt.subplots(1,2)
    fig.set_size_inches(15,5)
    sns.boxplot(x=coluna, ax=ax1)
    ax2.set_xlim(limites(coluna))
    sns.boxplot(x=coluna, ax=ax2)
    plt.show()

def histograma(coluna):
    plt.figure(figsize=(15,5))
    sns.distplot(coluna, hist=True)
    plt.show()

def grafico_barra(coluna):
    plt.figure(figsize=(15,5))
    ax = sns.barplot(x=coluna.value_count().index,y=coluna.value_counts())
    ax.set_xlim(limites(coluna))

# excluindo os valores da coluna com valores acima do limite superior 
base_airbnb, linhas_removidas = excluir_outliers(base_airbnb,'price')
print('{} linhas removidas'.format(linhas_removidas))
 
base_airbnb, linhas_removidas = excluir_outliers(base_airbnb,'host_listings_count')
print('{} linhas removidas'.format(linhas_removidas))

base_airbnb, linhas_removidas = excluir_outliers(base_airbnb,'accommodates')
print('{} linhas removidas'.format(linhas_removidas))

base_airbnb, linhas_removidas = excluir_outliers(base_airbnb,'bathrooms')
print('{} linhas removidas'.format(linhas_removidas))

base_airbnb, linhas_removidas = excluir_outliers(base_airbnb,'minimum_nights')
print('{} linhas removidas'.format(linhas_removidas))

# chamar a função de diagrama de caixa
#diagrama_caixa(base_airbnb['price'])

# chamar a função de histograma
#histograma(base_airbnb['price'])

# Remover a feature analise, pois parece que os usuarios usam muito o valor
# padrao do airbnb como 1 guest includes, podendo levar o modelo a considerar
# uma feature que na verdade não é essencial para definição de preço
base_airbnb = base_airbnb.drop('guests_included', axis = 1)
base_airbnb = base_airbnb.drop('maximum_nights', axis = 1)
base_airbnb = base_airbnb.drop('number_of_reviews', axis = 1)
print(base_airbnb.shape)


# tratamento colunas de valores texto
#print(base_airbnb['property_type'].value_counts())
plt.figure(figsize=(15,5))
sns.set_theme(style = "whitegrid")
grafico = sns.countplot(x=base_airbnb['property_type'])
grafico.tick_params(axis='x',rotation=80)
#plt.show()

tabela_tipos_casa = base_airbnb['property_type'].value_counts()
colunas_agrupar = []

for tipo in tabela_tipos_casa.index:
    if tabela_tipos_casa[tipo] < 2000:
        colunas_agrupar.append(tipo)
#print(colunas_agrupar)

for tipo in colunas_agrupar:
    base_airbnb.loc[base_airbnb['property_type']==tipo,'property_type'] = 'Outros'


#print(base_airbnb['room_type'].value_counts())
#print(base_airbnb['bed_type'].value_counts())

# agrupando categorias de bed_type
tabela_bed_type = base_airbnb['bed_type'].value_counts()
colunas_agrupar = []

for tipo in tabela_bed_type.index:
    if tabela_bed_type[tipo] < 10000:
        colunas_agrupar.append(tipo)
#print(colunas_agrupar)

for tipo in colunas_agrupar:
    base_airbnb.loc[base_airbnb['bed_type']==tipo,'bed_type'] = 'Outros'


#print(base_airbnb['cancellation_policy'].value_counts())

# agrupando categorias de cancellation_policy
tabela_cancellation = base_airbnb['cancellation_policy'].value_counts()
colunas_agrupar = []

for tipo in tabela_cancellation.index:
    if tabela_cancellation[tipo] < 10000:
        colunas_agrupar.append(tipo)
#print(colunas_agrupar)

for tipo in colunas_agrupar:
    base_airbnb.loc[base_airbnb['cancellation_policy']==tipo,'cancellation_policy'] = 'strict'


base_airbnb['n_amenities'] = base_airbnb['amenities'].str.split(',').apply(len)
base_airbnb = base_airbnb.drop('amenities',axis=1)

base_airbnb, linhas_removidas = excluir_outliers(base_airbnb,'n_amenities')
print('{} linhas removidas'.format(linhas_removidas))






print("Process finished --- %s seconds ---" % (time.time() - start_time))