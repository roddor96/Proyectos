# Importar las librerías que vamos a usar
import pandas as pd
import plotly.express as px
import streamlit as st

#Asignar los datos a un DF
car_data=pd.read_csv('vehicles_us.csv')

#---------------------------------------LIMPIAR DATOS-----------------------------------------------

#'is_4wd' se refiere si el auto tiene tracción en las 4 ruedas, comprobar que solo hay datos vacios y 1s, 
#de ser así cambiar los datos vacios por 0

traccion=car_data.groupby(['is_4wd'])['model'].count()
car_data['is_4wd']=car_data['is_4wd'].fillna(0)

#El color de la pintura se va a rellenar con "Unknown" no hay otra forma de llenarlo

car_data['paint_color']=car_data['paint_color'].fillna('Unknown')

#El número de cilindros, kilometraje y año se van a rellenar con el promedio de su categoría

car_data['cylinders']=car_data['cylinders'].fillna(int(car_data['cylinders'].mean()))
car_data['model_year']=car_data['model_year'].fillna(int(car_data['model_year'].mean()))
car_data['odometer']=car_data['odometer'].fillna(int(car_data['odometer'].mean()))

#El tipo de datos de las categorías model_year, cylinders, odometer y is_4wd serán cambiados a int

type_change=['model_year','cylinders','odometer','is_4wd']
for category in type_change:
    car_data[category]=car_data[category].astype('int')

#Cambiar el tipo de dato de date_posted

import datetime as dt
car_data['date_posted'] = pd.to_datetime(car_data['date_posted'], format='%Y-%m-%d')

#Extraer marcas de los coches

car_data['brand'] = car_data['model'].str.split(' ', n=1, expand=True)[0]

#Confirmar que los cambios se hayan realizado
car_data.info()


st.header('Información de venta de coches usados')
hist_button = st.button('Construir histograma') # crear un botón
     
if hist_button: # al hacer clic en el botón
    # escribir un mensaje
    st.write('Creación de un histograma para el conjunto de datos de anuncios de venta de coches')
         
    # crear un histograma
    fig = px.histogram(car_data, x="odometer")
     
    # mostrar un gráfico Plotly interactivo
    st.plotly_chart(fig, use_container_width=True)

min_price, max_price = st.slider(
    "Selecciona el rango de precios:",
    min_value=int(car_data["price"].min()),
    max_value=int(car_data["price"].max()),
    value=(10000, 50000),  # Valores iniciales
    step=1000)

filtered_df = car_data[(car_data["price"] >= min_price) & (car_data["price"] <= max_price)]

# Crear gráfico de barras (distribución de precios)
st.subheader(f"Distribución de Precios (Autos entre {min_price:,}  y  {max_price:,})")
fig = px.histogram(
    filtered_df,
    x="price",
    nbins=200,  # Número de barras
    title="Distribución de Precios",
    labels={"price": "Precio (USD)", "count": "Número de Autos"},
    width=1000,
    height=500
)

# Personalizar el gráfico
fig.update_layout(bargap=0.1)  # Espacio entre barras

# Mostrar el gráfico
st.plotly_chart(fig, use_container_width=True)

# 5. Mostrar estadísticas básicas
st.write(f"**Total de autos en este rango:** {len(filtered_df):,}")
st.write(f"**Precio promedio:** ${filtered_df['price'].mean():,.2f}")

selected_brands = st.multiselect(
    "Selecciona las marcas a visualizar:",
    options=car_data['brand'].unique(),
    default=car_data['brand'].unique()[:5] 
)


# Aplicar filtros al DataFrame
filtered_df = car_data[car_data['brand'].isin(selected_brands)]


# ---- GRÁFICO DE BARRAS ----
st.subheader(f"Total de Ventas por Marca (Marcas seleccionadas: {len(selected_brands)})")

# Contar vehículos por marca
sales_by_brand = filtered_df['brand'].value_counts().reset_index()
sales_by_brand.columns = ['brand', 'count']

# Crear gráfico con Plotly
fig = px.bar(
    sales_by_brand,
    x='brand',
    y='count',
    color='brand',
    labels={'brand': 'Marca', 'count': 'Número de Vehículos'},
    text_auto=True  # Muestra los valores en las barras
)

# Personalizar layout
fig.update_layout(
    xaxis_title="Marca",
    yaxis_title="Ventas Totales",
    hovermode="x"
)

# Mostrar gráfico
st.plotly_chart(fig, use_container_width=True)

# ---- DATOS ADICIONALES ----
st.write(f"**Total de vehículos filtrados:** {len(filtered_df):,}")
st.dataframe(sales_by_brand.sort_values('count', ascending=False))


# Obtener fechas mínima y máxima
min_date = car_data['date_posted'].min().date()
max_date = car_data['date_posted'].max().date()

# Slider de fechas
selected_range = st.slider(
    "Selecciona el rango de fechas:",
    min_value=min_date,
    max_value=max_date,
    value=(min_date, max_date),  # Rango inicial completo
    format="YYYY-MM-DD"
)

# Convertir a datetime64 para comparación
start_date = pd.to_datetime(selected_range[0])
end_date = pd.to_datetime(selected_range[1])

# Filtrar DataFrame
filtered_df_date = car_data[(car_data['date_posted'] >= start_date) & (car_data['date_posted'] <= end_date)]

# ---- GRÁFICO DE DISPERSIÓN ----
st.subheader(f"Publicaciones por Día ({start_date.date()} a {end_date.date()})")

# Agrupar por fecha y contar autos
daily_counts = filtered_df_date.groupby(filtered_df_date['date_posted'].dt.date).size().reset_index(name='count')

# Crear gráfico
fig = px.scatter(
    daily_counts,
    x='date_posted',
    y='count',
    labels={'date_posted': 'Fecha de Publicación', 'count': 'Número de Autos'},
)

# Personalizar
fig.update_traces(marker=dict(size=8, opacity=0.7))
fig.update_layout(
    xaxis_title="Fecha",
    yaxis_title="Autos Publicados",
    hovermode="x unified"
)

# Mostrar gráfico
st.plotly_chart(fig, use_container_width=True)

# ---- DATOS ADICIONALES ----

col1, col2 = st.columns(2)
with col1:
    st.metric("Total de autos", len(filtered_df))
with col2:
    st.metric("Publicaciones diarias promedio", round(daily_counts['count'].mean(), 1))
    
st.write("Datos por fecha:")
st.dataframe(daily_counts.sort_values('date_posted', ascending=False))
