import pandas as pd
import streamlit as st
import joblib

modelo = joblib.load('modelo.joblib')

x_numericos = {'latitude': 0, 'longitude': 0, 'accommodates': 0, 'bathrooms': 0, 'bedrooms': 0, 'beds': 0, 'extra_people': 0,
               'minimum_nights': 0, 'ano': 0, 'mes': 0, 'n_amenities': 0, 'host_listings_count': 0}

x_true_false = {'host_is_superhost': 0, 'instant_bookable': 0}

x_listas = {'property_type': ['Apartment', 'Bed and breakfast', 'Condominium', 'Guest suite', 'Guesthouse', 'Hostel', 'House', 'Loft', 'Outros', 'Serviced apartment'],
            'room_type': ['Entire home/apt', 'Hotel room', 'Private room', 'Shared room'],
            'cancelation_policy': ['flexible', 'moderate', 'strict', 'strict_14_with_grace_period']
            }

dicionario = {}

for item in x_listas:
    for valor in x_listas[item]:
        dicionario[f'{item}_{valor}'] = 0

for item in x_numericos:
    if item == 'latitude' or item == 'longitude':
        valor = st.number_input(f'{item}',step=0.00001, value=0.0, format="%.5f")
    elif item == 'extra_people':
        valor = st.number_input(f'{item}', step=0.01, value=0.0)
    else:
        valor = st.number_input(f'{item}', step=1, value=0)
    x_numericos[item] = valor

for item in x_true_false:
    valor = st.selectbox(f'{item}', ('Sim','Não'))
    if valor == "Sim":
        x_true_false[item] = 1
    else:
        x_true_false[item] = 0

for item in x_listas:
    valor = st.selectbox(f'{item}', x_listas[item])


botao = st.button('Prever Valor do Imovel')
