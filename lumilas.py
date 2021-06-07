import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk
import plotly.graph_objects as go
import time

from PIL import Image
from bson_decode import ingest_bson

colors = {
    "nada": [255,0,0,80],
    "vial": [0,255,0,220],
    "villa": [255,0,255,220],
    "palo": [0,128,128,220],
    "doble": [255,255,0,220],
    "otro": [0,255,255,220],
    "indeterminado": [250,128,14,220]
}

def colors_dict(label):
    global colors
    res = [colors[x] for x in label]
    return res

def main():
    coln1, col_tit, coln3 = st.beta_columns([1,2,1])
    col_tit.title('Lumilas: aplicación de análisis :zap:')

    st.write('## Carga de datos')
    file = st.file_uploader('Seleccione el archivo .csv que quiera analizar',type='csv')

    ph = st.empty()
    if file is not None:
        #og = cache_load_data(file)
        data = pd.read_csv(file)
        #ph.success('Datos cargados correctamente')
        # Pretend we're doing some computation that takes time.
        time.sleep(1.7)
        ph.empty()

        col1, col2, col3 = st.beta_columns([1,2,1])

        x = inflate_preview_column(col1,data)
        inflate_map_column(col2,data,x)
        inflate_modification_column(col3,data)

    #'''Made with :heart: by LSI.'''

def inflate_preview_column(col, data):
    with col:
        st.header('Datos')
        st.dataframe(data.head(400))
        #st.write('## Alertas:',0)
        st.write('## Configuración de mapa')
        r = st.slider('Radio punto', min_value=1, max_value=7, value=5, step=1)
        return r

def inflate_map_column(col,df,x):

    with col:
        st.header('Mapa')
        mp = st.empty()
        df['colors'] = colors_dict(df['clase_str'].to_list())
        mp.pydeck_chart(pdk.Deck(
        map_style='mapbox://styles/mrodrigueza/ck8fw3dx139zl1invheqydp3j',
        initial_view_state=pdk.ViewState(
            latitude= np.mean(df['streetlight_lat'].to_numpy()), 
            longitude= np.mean(df['streetlight_lon'].to_numpy()),
            zoom=16,
            pitch=0,
        ),
        layers=[
            pdk.Layer(
                'ScatterplotLayer',
                data=df[['streetlight_lon','streetlight_lat','clase_str','streetlight_date','timestamp', 'streetlight_angle', 'streetlight_height','lux_aux','colors']],
                get_position='[streetlight_lon,streetlight_lat]',
                get_radius = x,
                opacity = 1,
                get_color = 'colors',#'[255, 242, 0]', #df['clase_str'].applymap(lambda x: colors[x]),
                pickable=True 
            ) 
        ],
        tooltip={
                    'html': '<b>Fecha:</b> {streetlight_date} <br> <b> Id:</b> {timestamp} <br> <b> Clase:</b> {clase_str} <br> <b> luz:</b> {lux_aux} <br> <b> Altura:</b> {streetlight_height} <br> <b> Ángulo:</b> {streetlight_angle}' ,
                    'style': 
                    {
                        "backgroundColor": "steelblue",
                        'color': 'white'
                    }
                }
    ), use_container_width=True)

def inflate_modification_column(col,data):
    with col:
        st.header('Inspección')
        cloud = st.selectbox('Luminaria a estudiar', ['id 1','id 2', 'id n'])
        #st.image('Std_Lamparon.png',use_column_width=True)
        st.plotly_chart(get_plotly_fig_hd(pd.read_csv('/home/marcos/Escritorio/cluster_3_6_2019_18_56_20_10.csv')),use_container_width=True) #hard-coded -> change in future
        #st.plotly_chart(get_plotly_fig(get_xyz_from_bson(ingest_bson()),use_container_width=True) #hard-coded -> change in future

def get_plotly_fig(xyz_tuple):
    fig = go.Figure(data=[go.Scatter3d(x=xyz_tuple[0], y=xyz_tuple[1], z=xyz_tuple[2], mode='markers',marker=dict(size=1))])
    fig.update_layout(margin=dict(l=20,r=0,b=70,t=0))
    fig.update_scenes(xaxis_visible=False, yaxis_visible=False, zaxis_visible=False)
    return fig


def get_plotly_fig_hd(df):
    fig = go.Figure(data=[go.Scatter3d(x=df.x, y=df.y, z=df.z, mode='markers',marker=dict(size=1.5))])
    fig.update_layout(margin=dict(l=20,r=0,b=70,t=0))
    fig.update_scenes(xaxis_visible=False, yaxis_visible=False, zaxis_visible=False)
    return fig

def ingest_bson(encoded_str):

    raw_list = encoded_str.split('-')
    map_object = map(int, raw_list)
    list_of_integers = list(map_object)
    bson_raw = bytearray(list_of_integers)
    b = bson.loads(bson_raw)
    return b

def get_xyz_from_bson(bson_object):
    x = [element['x'] for element in bson_object['data']] 
    y = [element['y'] for element in bson_object['data']] 
    z = [element['z'] for element in bson_object['data']]   

    return (x,y,z)  
#@st.cache  # 👈 This function will be cached
def process_data(df):

    icon_data = {
    "x":0,
    "y":0,
    "width": 32,
    "height": 32, 
    "mask": True
    }
  
    st.write("## Here's a quick preview of the Data loaded ")
    st.dataframe(df.head(10)) 

    '''## Map with three-dimensional info '''
    st.pydeck_chart(pdk.Deck(
     map_style='mapbox://styles/mrodrigueza/ck8fw3dx139zl1invheqydp3j',
     initial_view_state=pdk.ViewState(
         latitude=40.349972, 
         longitude= -3.753149,
         zoom=14,
         pitch=35,
     ),
     layers=[
         pdk.Layer(
            'ScatterplotLayer',
            data=df,
            get_position='[lon, lat]',
            get_radius = 7,
            get_color = [255, 251, 138,255],#'[255, 242, 0]',
            auto_highlight = True,
            pickable=True,
            extruded=True,
         ),
         pdk.Layer(
            'IconLayer',
            data=df,
            icon_atlas='/home/marcos/Descargas/Diseño sin título.png',
            icon_mapping= 'icon_data',
            get_position='[lon, lat]',
            get_size=2,
            pickable=True,
            size_scale=10
         )
     ]
 ),use_container_width=True)

    '''## Heatmap :fire: '''

    st.pydeck_chart(pdk.Deck(
     map_style='mapbox://styles/mrodrigueza/ck8fw3dx139zl1invheqydp3j',
     initial_view_state=pdk.ViewState(
         latitude=40.349972, 
         longitude= -3.753149,
         zoom=12,
         pitch=0,
     ),
     layers=[
         pdk.Layer(
            'HeatmapLayer',
            data=df,
            get_position='[lon, lat]',
            radius_pixels = 12,
            color_range=[[255, 247, 0,255],[255, 251, 138,255],[255, 254, 237,255]]
         )
     ]
 ))

@st.cache 
def load_image(path):
    im = Image.open(path)
    return im

@st.cache 
def cache_load_data(path):
    return pd.read_csv(path)

if __name__ == "__main__":
    st.set_page_config(
        page_title='Lumilas App',
        page_icon=':zap:',
        layout='wide',
        initial_sidebar_state='collapsed',
        )
        
    main()