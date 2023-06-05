# -*- coding: utf-8 -*-
"""
Created on Wed May 31 23:47:17 2023

@author: Usuario
"""

# Cargar datos
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import base64
import altair as alt#Grafico con geojson
import numpy as np

# Función para descargar base de datos LINK PARA QUE LA PERSONA DESCARGE LA BASE DE DATOS
def get_table_download_link(crimenes):
    csv = crimenes.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()  # some strings <-> bytes conversions necessary here
    href = f'<a href="data:file/csv;base64,{b64}" download="datos.csv">Descargar archivo csv</a>'
    return href


# Carga Bases de datos 

hate = pd.read_csv('hate crime (1).csv', sep = ';')
trata = pd.read_csv('TRATA DE PERSONAS (1).csv', sep = ';')
est = pd.read_csv('estimated_crimes_1979_2020.csv', sep = ',')

#Limpieza de bases 

#-------------------------------------------------------------------------------------------------------

############## EST_CRIMES ###########################

#Seleccionamos variables con las que se trabajara 

b1 = est.loc[:,['year','state_name','population','violent_crime','homicide','rape_legacy','rape_revised','robbery','aggravated_assault','property_crime','burglary','larceny','motor_vehicle_theft']]

# Borramos los registros innestables 
b1 = b1.dropna(subset=['state_name'])
b1 = b1.fillna(0)

# nombres estados a minusculas 
b2 = b1.copy()
b2['state_name'] = b1['state_name'].apply(lambda x: x.lower())

# Nueva variable 
b3 = b2.copy()
b3['total_crimes'] = b3['aggravated_assault']+b3['burglary']+b3['homicide']+b3['violent_crime']+b3['larceny']+b3['motor_vehicle_theft']+b3['property_crime']+b3['rape_revised']+b3['rape_legacy']+b3['robbery']
b3['prom_tot_crimes'] = (b3['aggravated_assault']+b3['burglary']+b3['homicide']+b3['violent_crime']+b3['larceny']+b3['motor_vehicle_theft']+b3['property_crime']+b3['rape_revised']+b3['rape_legacy']+b3['robbery'])/11
b3['indice_crimines'] = b3['prom_tot_crimes'] / b3['population']


############## HATE CRIME  ###########################

h1 = hate.loc[:,['year','state_name','agency_type_name', 'location_name','offender_race', 'bias_desc','total_offender_count','offense_name','victim_types','victim_count']]


#Tratamiento de nulos de las variables, se reemplazaron los nulos con la categoria de desconocido/otro.
h2 = h1.copy()
h2['location_name']=h2['location_name'].fillna('Other/Unknown')
h2['bias_desc']=h2['bias_desc'].fillna('Unknown')
h2['victim_types']=h2['victim_types'].fillna('Unknown')

# Homologacion de categorias 
h3 = h2.copy()
h3['agency_type_name'] = h3['agency_type_name'].replace(['Other','Other State Agency'],'Other State Agency') 
h3['offender_race'] = h3['offender_race'].replace(['Unknown','Not Specified'], 'Unknown')
h3['bias_desc'] = h3['bias_desc'].replace(['Unknown',"Unknown (offender\'s motivation not known)"], 'Unknown') #NO CAMBIA POR LA COMILLA QUE HAY 
h3['offense_name'] = h3['offense_name'].replace(['Destruction/Damage/Vandalism of Property','Burglary/Breaking & Entering', 'Arson', 'Stolen Property Offenses'], 'Property Crimes') 
h3['offense_name'] = h3['offense_name'].replace(['All Other Larceny','Robbery'], 'Robbery') 
h3['offense_name'] = h3['offense_name'].replace(['Drug/Narcotic Violations','Drug Equipment Violations'], 'Drug/Narcotic Violations') 
h3['offense_name'] = h3['offense_name'].replace(['Theft From Motor Vehicle','Motor Vehicle Theft'], 'Motor Vehicle Theft') 
h3['offense_name'] = h3['offense_name'].replace(['Impersonation','Identity Theft'], 'Impersonation') 
h3['offense_name'] = h3['offense_name'].replace(['Prostitution','Assisting or Promoting Prostitution','Purchasing Prostitution'], 'Prostitution') 
h3['offense_name'] = h3['offense_name'].replace(['Human Trafficking, Commercial Sex Acts', 'Human Trafficking, Involuntary Servitude'], 'Human Trafficking') 
h3['victim_types'] = h3['victim_types'].replace(['Other', 'Unknown'], 'Unknown') 

#Transformacion tipo de letra 
h3['state_name'] = h3['state_name'].apply(lambda x: x.lower())


############## TRATA DE PERSONAS   ###########################

#Transformacion tipo de letra 

t1 = trata.copy()
t1=t1.rename(columns = lambda x: x.lower())

#Seleccion variables 

t2 = t1.loc[:,['year','state_name','agency_type_name', 'offense_subcat_name','actual_count','cleared_count']]

#Homologar variables
t3= t2.copy()
t3['agency_type_name']=t3['agency_type_name'].replace(['Other','Other State Agency'],'Other State Agency') 
t3['agency_type_name'].value_counts()
t3['state_name'] = t3['state_name'].apply(lambda x: x.lower())


################### LAS BASES DEPURADAS SON EST : b3 ; HATE : h3 ; TRATA : t3 ##########################

#-------------------------------------------------------------------------------------------------------

# ELABORACION DASHBOARD 

# Utilizar la página completa en lugar de una columna central estrecha
st.set_page_config(layout="wide")

# Título principal, h1 denota el estilo del título 1
st.markdown("<h1 style='text-align: center; color: #FFFFFF;'> 📊 Historico criminalidad en Estados Unidos 🗽  </h1>", unsafe_allow_html=True)
 
#------------------------------------------------------------------------------------------------------------------------------------------------
c1, c2, c3, c4, c5= st.columns((1,1,1,1,1)) # Dividir el ancho en 5 columnas de igual tamaño

#----- # Top Año

c1.markdown("<h3 style='text-align: left; color: white;'> Top Año </h3>", unsafe_allow_html=True)

tf = pd.read_csv('tablas_juntas.csv', sep = ';')
tf['prom_crimenes'] = round(tf['prom_crimenes'],1)

c1.text('➕ ' +str('1992')+ ': '+str(tf['prom_crimenes'].max()))
c1.text('➖ ' +str('2021')+ ': '+str(tf['prom_crimenes'].min()))

##-------# Top Estado
c2.markdown("<h3 style='text-align: left; color: white;'> Top Estado </h3>", unsafe_allow_html=True)

b = pd.DataFrame(tf.groupby(['state_name'])['prom_crimenes'].sum().reset_index().sort_values('prom_crimenes', ascending = False))#Estados y prom
b['porcentaje'] = (b['prom_crimenes']/(b['prom_crimenes'].sum()))*100
z = b.loc[:,['state_name','porcentaje']]
y = pd.DataFrame(z.value_counts().reset_index())

z['porcentaje'] = round(z['porcentaje'],2)

t1 = z.iloc[0,0]
t2 = z.iloc[0,1]

t7 = z.iloc[1,0]
t4 = z.iloc[1,1]

t5 = z.iloc[2,0]
t6 = z.iloc[2,1]

c2.text('1️⃣ ' +str(t1)+': '+str(t2)+'%' )
c2.text('2️⃣ ' +str(t7)+': '+str(t4)+'%')
c2.text('3️⃣ ' +str(t5)+': '+str(t6)+'%' )

#------------- Top Delitos comunes

c3.markdown("<h3 style='text-align: left; color: white;'> Top Delitos Comunes </h3>", unsafe_allow_html=True)


b3['one'] = 1

vio = pd.DataFrame(b3.groupby(['one'])['violent_crime'].sum()).reset_index().rename(columns = {'violent_crime':'cantidad'})
vio['tipo_delito'] =  'violent_crime'

hom = pd.DataFrame(b3.groupby(['one'])['homicide'].sum()).reset_index().rename(columns = {'homicide':'cantidad'})
hom['tipo_delito'] =  'homicide'

rap1 = pd.DataFrame(b3.groupby(['one'])['rape_legacy'].sum()).reset_index().rename(columns = {'rape_legacy':'cantidad'})
rap1['tipo_delito'] =  'rape_legacy'

rap = pd.DataFrame(b3.groupby(['one'])['rape_revised'].sum()).reset_index().rename(columns = {'rape_revised':'cantidad'})
rap['tipo_delito'] =  'rape_revised'

rob = pd.DataFrame(b3.groupby(['one'])['robbery'].sum()).reset_index().rename(columns = {'robbery':'cantidad'})
rob['tipo_delito'] =  'rob'

agg = pd.DataFrame(b3.groupby(['one'])['aggravated_assault'].sum()).reset_index().rename(columns = {'aggravated_assault':'cantidad'})
agg['tipo_delito'] =  'aggravated_assault'

prop= pd.DataFrame(b3.groupby(['one'])['property_crime'].sum()).reset_index().rename(columns = {'property_crime':'cantidad'})
prop['tipo_delito'] =  'property_crime'

bur= pd.DataFrame(b3.groupby(['one'])['burglary'].sum()).reset_index().rename(columns = {'burglary':'cantidad'})
bur['tipo_delito'] =  'burglary'

lan = pd.DataFrame(b3.groupby(['one'])['larceny'].sum()).reset_index().rename(columns = {'larceny':'cantidad'})
lan['tipo_delito'] =  'larceny'

mct = pd.DataFrame(b3.groupby(['one'])['motor_vehicle_theft'].sum()).reset_index().rename(columns = {'motor_vehicle_theft':'cantidad'})
mct['tipo_delito'] =  'motor_vehicle_theft'

fff = pd.concat([mct,lan,bur,prop,rob,rap,rap1,hom,vio,agg])
fff.sort_values(['cantidad'],ascending = False)

## Crimen con mayor nomero es propierity crime

p1 = fff.iloc[0,2]
p2 = fff.iloc[0,1]

c3.text('' +str(p1))
c3.text('' +str(p2))

#------------- Top Crimenes odio

c4.markdown("<h3 style='text-align: left; color: white;'> Top Crimenes de odio </h3>", unsafe_allow_html=True)

p3 = h3['victim_count'].sum()

c4.text('' +str(p3)+ ' victimas')
#------------- Top Trata de personas 

c5.markdown("<h3 style='text-align: left; color: white;'> Top Trata de personas </h3>", unsafe_allow_html=True)

p4 = t3['actual_count'].sum()

c5.text('' +str(p4)+ ' victimas')

#------------------------------------------------------------------------------------------------------------------------------------------------
#BASE DE DATOS 
crimenes = pd.read_csv('crimenes.csv') # base de datos
crimenes['year'] = pd.to_datetime(crimenes['year'], format='%Y')#Dar formato de fecha a los datos
crimenes['year'] = crimenes['year'].dt.year # sacar columna con año


crimenes['state_name'] = crimenes['state_name'].apply(lambda x: x.lower().strip() if pd.notnull(x) else x) #Homologar los estados

crimenes['state_name']=crimenes['state_name'].apply(lambda x: x.capitalize().strip() if pd.notnull(x) else x)#Poner la primera letra en mayuscula


#Caja de selección de estado 
estados= ['Todos los estados'] + list(crimenes['state_name'].unique())
#hay que homologar los nomnbres  tienen espacio y no los toma como unique
panel1= st.container()

with panel1:
    columns = st.columns([2, 0.2, 2.1, 0.2, 1.2, 0.2, 1.2])
    
    with columns[0]:
        year1 = st.slider('Año en el que se presento el suceso', 1979, 2021)
        datos= crimenes.loc[crimenes['year']==year1]
        state = columns[2].selectbox(
            'state_name',
            (estados),
            key='state')
        if state == "Todos los estados":
            state_datos= crimenes.groupby('year').sum().reset_index()
        else:
            state_datos= crimenes.loc[crimenes['state_name']== state].sort_values('year',ascending = True)
                
    g1, g2 = st.columns([1,2])
    with g1:
        url="https://raw.githubusercontent.com/deldersveld/topojson/master/countries/united-states/us-albers.json"#mapa de division por estado 
        estado= alt.topo_feature(url, "us")
              
        map1= alt.Chart(estado).mark_geoshape(stroke='Lightgray').encode(
            color= alt.Color('prom_crimenes:Q'), 
            tooltip=['state_name:N', 'prom_crimenes:Q']
        ).transform_lookup(
            lookup= 'properties.name',
            from_=alt.LookupData(datos,'state_name', list(datos.columns ))
        ).project(
            type='albersUsa')
        
        st.altair_chart(map1, use_container_width=True)#Mostrar grafico estados 
    
    with g2:
        fig = px.line(state_datos, x='year', y='prom_crimenes',  width=900, height=450)

        # Editar gráfica
        fig.update_layout(
                title='Evolución de la criminalidad en ' +state+ ' a través de los años',
                title_x=0.33,
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                template = 'simple_white',
                xaxis_title="<b>Año<b>",
                yaxis_title='<b>´Promedio de crimenes<b>')

        # Enviar gráfica a streamlit
        st.plotly_chart(fig)#Grafica con la evolución por estado
        
#-----------------------------------------------------------------------------------------------------------------------------------------
# Grafica barras ; construccion bases

#c1, c2, c3 = st.columns((1,6,1))

st.markdown("<h3 style='text-align: Center; color: white;'> Estados con mayor numero de delitos comunes </h3>", unsafe_allow_html=True)

z11 = pd.DataFrame(b3.groupby(['state_name'])['violent_crime'].sum()).reset_index().rename(columns = {'violent_crime':'cantidad'})
z11['tipo_delito'] =  'violent_crime'

z12 = pd.DataFrame(b3.groupby(['state_name'])['homicide'].sum()).reset_index().rename(columns = {'homicide':'cantidad'})
z12['tipo_delito'] =  'homicide'

z13 = pd.DataFrame(b3.groupby(['state_name'])['rape_legacy'].sum()).reset_index().rename(columns = {'rape_legacy':'cantidad'})
z13['tipo_delito'] =  'rape_legacy'

z14 = pd.DataFrame(b3.groupby(['state_name'])['rape_revised'].sum()).reset_index().rename(columns = {'rape_revised':'cantidad'})
z14['tipo_delito'] =  'rape_revised'

z15 = pd.DataFrame(b3.groupby(['state_name'])['robbery'].sum()).reset_index().rename(columns = {'robbery':'cantidad'})
z15['tipo_delito'] =  'rob'

z16 = pd.DataFrame(b3.groupby(['state_name'])['aggravated_assault'].sum()).reset_index().rename(columns = {'aggravated_assault':'cantidad'})
z16['tipo_delito'] =  'aggravated_assault'

z17 = pd.DataFrame(b3.groupby(['state_name'])['property_crime'].sum()).reset_index().rename(columns = {'property_crime':'cantidad'})
z17['tipo_delito'] =  'property_crime'

z18= pd.DataFrame(b3.groupby(['state_name'])['burglary'].sum()).reset_index().rename(columns = {'burglary':'cantidad'})
z18['tipo_delito'] =  'burglary'

z19 = pd.DataFrame(b3.groupby(['state_name'])['larceny'].sum()).reset_index().rename(columns = {'larceny':'cantidad'})
z19['tipo_delito'] =  'larceny'

z20 = pd.DataFrame(b3.groupby(['state_name'])['motor_vehicle_theft'].sum()).reset_index().rename(columns = {'motor_vehicle_theft':'cantidad'})
z20['tipo_delito'] =  'motor_vehicle_theft'


zf = pd.concat([z11,z12,z13,z14,z15,z16,z17,z18,z19,z20])
zf = zf.sort_values(['cantidad'],ascending = False)

zfprop = zf[zf['tipo_delito'] == 'property_crime' ].sort_values('cantidad',ascending = False).head(3)
zfvio = zf[zf['tipo_delito'] == 'violent_crime' ].sort_values('cantidad',ascending = False).head(3)
zfhom = zf[zf['tipo_delito'] == 'homicide' ].sort_values('cantidad',ascending = False).head(3)
zfrap1 = zf[zf['tipo_delito'] == 'rape_legacy' ].sort_values('cantidad',ascending = False).head(3)
zfrap2 = zf[zf['tipo_delito'] == 'rape_revised' ].sort_values('cantidad',ascending = False).head(3)
zfrob = zf[zf['tipo_delito'] == 'robbery' ].sort_values('cantidad',ascending = False).head(3)
zfagg = zf[zf['tipo_delito'] == 'aggravated_assault' ].sort_values('cantidad',ascending = False).head(3)
zfbur = zf[zf['tipo_delito'] == 'burglary' ].sort_values('cantidad',ascending = False).head(3)
zflar = zf[zf['tipo_delito'] == 'larceny' ].sort_values('cantidad',ascending = False).head(3)
zfmot = zf[zf['tipo_delito'] == 'motor_vehicle_theft' ].sort_values('cantidad',ascending = False).head(3)

#creacion pestaña
est1 = ['All crimes']+list(zf['tipo_delito'].unique())
est2 = st.selectbox(
    'crimenes',
    (est1),
    key = 'Crimes')

if est2 == 'All crimes' : 
    g1 = px.bar(zf, x='state_name', y='cantidad',width=1300, height=450)

    # agregar detalles a la gráfica
    g1.update_layout(
        xaxis_title = 'Estados',
        yaxis_title = 'Cantidad de registros',
        template = 'simple_white',
        title_x = 0.5)
    
    g1.update_xaxes(linecolor='white')
    g1.update_yaxes(linecolor='white')
    
    g1.update_traces(marker_color = 'goldenrod')
    

    st.plotly_chart(g1)

elif est2 == 'property_crime' : 
    g2 = px.bar(zfprop, x='state_name', y='cantidad',width=1300, height=450)

    # agregar detalles a la gráfica
    g2.update_layout(
        xaxis_title = 'Estados',
        yaxis_title = 'Cantidad de registros',
        template = 'simple_white',
        title_x = 0.5)
    
    g2.update_xaxes(linecolor='white')
    g2.update_yaxes(linecolor='white')
    g2.update_traces(marker_color = 'goldenrod')
    st.plotly_chart(g2)

elif est2 == 'violent_crime' : 
    g3 = px.bar(zfvio, x='state_name', y='cantidad',width=1300, height=450)

    # agregar detalles a la gráfica
    g3.update_layout(
        xaxis_title = 'Estados',
        yaxis_title = 'Cantidad de registros',
        template = 'simple_white',
        title_x = 0.5)
    
    g3.update_xaxes(linecolor='white')
    g3.update_yaxes(linecolor='white')
    g3.update_traces(marker_color = 'goldenrod')

    st.plotly_chart(g3)

elif est2 == 'homicide' : 
    g4 = px.bar(zfhom, x='state_name', y='cantidad',width=1300, height=450)

    # agregar detalles a la gráfica
    g4.update_layout(
        xaxis_title = 'Estados',
        yaxis_title = 'Cantidad de registros',
        template = 'simple_white',
        title_x = 0.5)
    
    g4.update_xaxes(linecolor='white')
    g4.update_yaxes(linecolor='white')
    g4.update_traces(marker_color = 'goldenrod')

    st.plotly_chart(g4)
    
elif est2 == 'rape_legacy' : 
    g5 = px.bar(zfrap1, x='state_name', y='cantidad',width=1300, height=450)

    # agregar detalles a la gráfica
    g5.update_layout(
        xaxis_title = 'Estados',
        yaxis_title = 'Cantidad de registros',
        template = 'simple_white',
        title_x = 0.5)
    
    g5.update_xaxes(linecolor='white')
    g5.update_yaxes(linecolor='white')
    g5.update_traces(marker_color = 'goldenrod')

    st.plotly_chart(g5)

elif est2 == 'rape_revised' : 
    g5 = px.bar(zfrap2, x='state_name', y='cantidad',width=1300, height=450)

    # agregar detalles a la gráfica
    g5.update_layout(
        xaxis_title = 'Estados',
        yaxis_title = 'Cantidad de registros',
        template = 'simple_white',
        title_x = 0.5)
    
    g5.update_xaxes(linecolor='white')
    g5.update_yaxes(linecolor='white')
    g5.update_traces(marker_color = 'goldenrod')

    st.plotly_chart(g5)


elif est2 == 'robbery' : 
    g5 = px.bar(zfrob, x='state_name', y='cantidad',width=1300, height=450)

    # agregar detalles a la gráfica
    g5.update_layout(
        xaxis_title = 'Estados',
        yaxis_title = 'Cantidad de registros',
        template = 'simple_white',
        title_x = 0.5)
    
    g5.update_xaxes(linecolor='white')
    g5.update_yaxes(linecolor='white')
    g5.update_traces(marker_color = 'goldenrod')

    st.plotly_chart(g5)
    
elif est2 == 'aggravated_assault' : 
    g5 = px.bar(zfagg, x='state_name', y='cantidad',width=1300, height=450)

    # agregar detalles a la gráfica
    g5.update_layout(
        xaxis_title = 'Estados',
        yaxis_title = 'Cantidad de registros',
        template = 'simple_white',
        title_x = 0.5)
    
    g5.update_xaxes(linecolor='white')
    g5.update_yaxes(linecolor='white')
    g5.update_traces(marker_color = 'goldenrod')

    st.plotly_chart(g5)
    
elif est2 == 'burglary' : 
     g5 = px.bar(zfbur, x='state_name', y='cantidad',width=1300, height=450)

     # agregar detalles a la gráfica
     g5.update_layout(
         xaxis_title = 'Estados',
         yaxis_title = 'Cantidad de registros',
         template = 'simple_white',
         title_x = 0.5)
     
     g5.update_xaxes(linecolor='white')
     g5.update_yaxes(linecolor='white')
     g5.update_traces(marker_color = 'goldenrod')

     st.plotly_chart(g5)   

elif est2 == 'larceny' : 
     g5 = px.bar(zflar, x='state_name', y='cantidad',width=1300, height=450) #,width=1400, height=450

     # agregar detalles a la gráfica
     g5.update_layout(
         xaxis_title = 'Estados',
         yaxis_title = 'Cantidad de registros',
         template = 'simple_white',
         title_x = 0.5)
     
     g5.update_xaxes(linecolor='white')
     g5.update_yaxes(linecolor='white')
     g5.update_traces(marker_color = 'goldenrod')

     st.plotly_chart(g5)   

elif est2 == 'motor_vehicle_theft' : 
     g5 = px.bar(zfmot, x='state_name', y='cantidad',width=1300, height=450)

     # agregar detalles a la gráfica
     g5.update_layout(
         xaxis_title = 'Estados',
         yaxis_title = 'Cantidad de registros',
         template = 'simple_white',
         title_x = 0.5)
     
     g5.update_xaxes(linecolor='white')
     g5.update_yaxes(linecolor='white')
     g5.update_traces(marker_color = 'goldenrod')

     st.plotly_chart(g5)   

#-----------------------------------------------------------------------------------------------------------------------------------------------

df= pd.read_csv('TRATA DE PERSONAS.csv',delimiter=';') # base datos
df=df.rename(columns = lambda x: x.lower())
df = df.loc[:,['data_year','state_name','agency_type_name', 'offense_subcat_name','actual_count','cleared_count']]# nos quedamos con solo las variables de 'data_year','state_name','agency_type_name', 'offense_subcat_name','actual_count','cleared_count'
df = df.rename(columns={'data_year':'year'}) #Cambiamos nombre de año
#----------------------------------------
# Utilizar la página completa en lugar de una columna central estrecha
#st.set_page_config(layout="wide")



# Título principal, h1 denota el estilo del título 1
st.markdown("<h3 style='text-align: center; color: #FFFFFF;'>Estados mas influyentes en el trafico de personas </h3>", unsafe_allow_html=True)


#DIVIDIR POR COLUMNAS
c1, c2= st.columns((1,1))


#----------------------------------------Pareto
# 5 cuales son los estaods que representaron mayor actividad de delitos reportados 
# crear base
df1 = df.copy() #se crea copia de tabla
df1=df1.rename(columns = lambda x: x.lower())



df1 = df1.groupby(['state_name'])[['actual_count']].sum().sort_values('actual_count', ascending=False).rename(columns={'actual_count':'delitos_reportados'})
df1['ratio'] = df1.apply(lambda x: x.cumsum()/df1['delitos_reportados'].sum())

 
# Definir figura
fig = go.Figure([go.Bar(x=df1.index, y=df1['delitos_reportados'], yaxis='y1', name='sessions id'),
                 go.Scatter(x=df1.index, y=df1['ratio'], yaxis='y2', name='Delitos reportados por estado', hovertemplate='%{y:.1%}', marker={'color': '#FFFFFF'})])

# Agregar detalles
fig.update_layout(template='plotly_white', showlegend=False, hovermode='x', bargap=.3,
                  title={'text': '<b>Delitos reportados por estado<b>', 'x': 0.3}, 
                  yaxis={'title': 'Delitos reportados'},
                  yaxis2={'rangemode': "tozero", 'overlaying': 'y', 'position': 1, 'side': 'right', 'title': 'ratio', 'tickvals': np.arange(0, 1.1, .2), 'tickmode': 'array', 'ticktext': [str(i) + '%' for i in range(0, 101, 20)]})

fig.update_xaxes(linecolor='white')
fig.update_yaxes(linecolor='white')

c1.plotly_chart(fig)
#----------------------------------------Grafico efectividad
df2 = df.copy() #se crea copia de tabla

año = df2.groupby(['year','state_name'])[['actual_count','cleared_count']].sum().rename(columns={'actual_count':'delitos_reportados','cleared_count':'delitos_resueltos'})# agrupamos por año y estado con la cantidad de delitos reportados y delitos resueltos
año = año.reset_index().rename(columns={'year': 'Año', 'state_name': 'Nombre del estado', 'delitos_reportados': 'Delitos reportados', 'delitos_resueltos': 'Delitos resueltos'})

estados_filtrar = ['Texas', 'Nevada', 'Minnesota', 'Florida']
estados_filtrados = año[año['Nombre del estado'].isin(estados_filtrar)]

estados_filtrados['efectividad'] = (estados_filtrados['Delitos resueltos'] / estados_filtrados['Delitos reportados'])*100 # creamos la columna con el indice de efectividad 
EF=estados_filtrados.copy()
EF.sort_values(by = ['efectividad'], ascending= False).rename(columns={'efectividad':'efectividad (%)'})

estados_seleccionados = ['Texas', 'Nevada', 'Minnesota', 'Florida']
efectividad_estados = EF[EF['Nombre del estado'].isin(estados_seleccionados)]
promedio_efectividad = efectividad_estados.groupby('Nombre del estado')['efectividad'].mean().reset_index()

 #Tabla del promedio de efectividad de cada estado
tabla_efectividad = pd.DataFrame(promedio_efectividad)
tabla_efectividad = tabla_efectividad.sort_values(by='efectividad', ascending=False)

#Grafica de lines, evolucion de efectividad por estado
fig2 = go.Figure()

for estado in estados_seleccionados:
    datos_estado = efectividad_estados[efectividad_estados['Nombre del estado'] == estado]
    fig2.add_trace(go.Scatter(x=datos_estado['Año'], y=datos_estado['efectividad'], mode='lines', name=estado ) )

# Personaliza el diseño del gráfico
fig2.update_layout(
    title='Evolución de la efectividad por estado',
    title_x= 0.25,
    xaxis=dict(title='Año'),
    yaxis=dict(title='Efectividad (%)'),
)    


fig2.update_xaxes(linecolor='white')
fig2.update_yaxes(linecolor='white')
# Muestra la figura
c2.plotly_chart(fig2)     

#_-----------------------------------------------------------------------------------------------------------------------------------------------
#st.set_page_config(layout="wide") #USAR TODA LA PANTALLA
# Cargar datos
h3= pd.read_csv('h3.csv',delimiter=',') # base datos
#h3=h3.rename(columns = lambda x: x.lower())
#h3 = df.loc[:,['data_year','state_name','agency_type_name', 'offense_subcat_name','actual_count','cleared_count']]# nos quedamos con solo las variables de 'data_year','state_name','agency_type_name', 'offense_subcat_name','actual_count','cleared_count'
#h3 = h3.rename(columns={'data_year':'year'}) #Cambiamos nombre de año
#----------------------------------------

# crear dataset
base = h3.groupby(['offender_race'])[['total_offender_count']].count().reset_index()

dic = {'Unknown':'Desconocida',
       'White':'Blanca',
       'Black or African American':'Negra / Africano-Americano',
       'Multiple':'Múltiple',
       'Asian':'Asiatica',
       'American Indian or Alaska Native':'Indio Americano o Nativo de Alaska',
       'Native Hawaiian or Other Pacific Islander':'Nativo Hawaiano o isleño del pacifico'}

base['offender_race'] = base['offender_race'].replace(dic)

#----------------------------------------
#dividir columnas 
c1, c2= st.columns((1,1))

# crear gráfica:
fig = px.pie(base , values = 'total_offender_count', names = 'offender_race', title = '<b>Raza del agresor<b>',width=700, height=700)

# agregar detalles a la gráfica:
fig.update_layout(
    template = 'simple_white',
    legend_title = 'Raza',
    title_x = 0.3)
c1.plotly_chart(fig)     

## Grafico lugares de la agresión
# crear dataset con las 10 mayores categorias.
base1= h3.groupby(['location_name'])[['total_offender_count']].count().reset_index()

base1 = base1.sort_values(by='total_offender_count', ascending=False)
top_categories = base1.head(5)

dic = {'Residence/Home':'Residencia/Hogar', 
       'Highway/Road/Alley/Street/Sidewalk':'Carretera/Ruta/Callejón/Calle/Acera',
       'Other/Unknown':'Otro/Desconocido',
       'School/College':'Escuela/Universidad',
       'Parking/Drop Lot/Garage':'Estacionamiento/Garage',
       'Church/Synagogue/Temple/Mosque':'Iglesia/Sinagoga/Templo/Mezquita',
       'Commercial/Office Building':'Comercial/Edificios de oficinas',
       'Restaurant':'Restaurante',
       'Bar/Nightclub':'Bar/Club Nocturno',
       'Government/Public Building':'Gobierno/Edificio Público'}

top_categories['location_name'] = top_categories['location_name'].replace(dic)

# crear gráfica:
fig2 = px.pie(top_categories , values = 'total_offender_count', names='location_name', title = '<b>Lugares de la agresion<b>',width=700, height=700)

# agregar detalles a la gráfica:
fig2.update_layout(
    template = 'simple_white',
    legend_title = 'Lugares',
    title_x = 0.3)

c2.plotly_chart(fig2)

# Checkbox
if st.checkbox('Obtener delitos por año y estado', False): # genera un boton para mostrar las tabñas

    tablafinal = crimenes.rename(columns ={'year':'Año','state_name':'Estado','prom_crimenes':'Cantidad_de_delitos'})

    # Código para convertir el DataFrame en una tabla plotly resumen
    fig77 = go.Figure(data=[go.Table(
        header=dict(values=list(tablafinal.columns), # encabezado de tabla 
        fill_color='darkgrey', # color relleno encabezado
        line_color='black'), # color borde de encabezdo
        cells=dict(values=[tablafinal.Año, tablafinal.Estado, tablafinal.Cantidad_de_delitos],fill_color='black',line_color='lightgrey'))
       ]) # valores que van en las celdas
    
    fig77.update_layout(width=500, height=450)

# Enviar tabla a streamlit
    st.write(fig77)


#DESCARGAR BASE
# Generar link de descarga
st.markdown(get_table_download_link(crimenes), unsafe_allow_html=True)





