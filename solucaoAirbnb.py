import pandas as pd
import pathlib

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

base_airbnb = pd.concat(bases)
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
colunas = ['host_response_rate','host_is_superhost','host_listings_count','latitude','longitude','is_location_exact','property_type','room_type','accommodates','bathrooms','bedrooms','beds','bed_type','amenities','price','security_deposit','cleaning_fee','guests_included','extra_people','minimum_nights','maximum_nights','number_of_reviews','review_scores_rating','review_scores_accuracy','review_scores_cleanliness','review_scores_checkin','review_scores_communication','review_scores_location','review_scores_value','instant_bookable','is_business_travel_ready','cancellation_policy','ano','mes']

base_airbnb = base_airbnb.loc[:, colunas]
print(base_airbnb)