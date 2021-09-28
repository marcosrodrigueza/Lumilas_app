from numpy.core.numeric import NaN
import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk
import plotly.graph_objects as go
import time
import uuid
import io
import json
import base64

from PIL import Image
#from bson_decode import ingest_bson

labels = ['vial', 'villa', 'doble', 'otro', 'nada', 'palo']

colors = {
    "nada": [255,0,0,80],
    "vial": [0,255,0,220],
    "villa": [255,0,255,220],
    "palo": [0,128,128,220],
    "doble": [255,255,0,220],
    "otro": [0,255,255,220],
    "indeterminado": [250,128,14,220]
}

def unique(list1):  
    # insert the list to the set
    list_set = set(list1)
    # convert the set to the list
    unique_list = (list(list_set))
    return unique_list

def colors_dict(label):
    global colors
    res = [colors[x] for x in label]
    return res

def main():
    coln1, col_tit, coln3 = st.columns([1,2,1])
    #col_tit.title('Lumilas: aplicación de análisis :zap:')
    col_tit.image(load_image('logo.jpg'), use_column_width=True)
    st.write('## Carga de datos')
    file = st.file_uploader('Seleccione el archivo .csv que quiera analizar',type='csv')

    ph = st.empty()
    if file is not None:
        #og = cache_load_data(file)
        data = None
        if 'data' not in st.session_state:
            data = pd.read_csv(file)
            st.session_state.data = data
        data = st.session_state.data
        #data['uuid'] = [uuid.uuid1() for _ in range(len(data.index))]
        data['id'] = ""
        for index,row in data.iterrows():
            data.loc[index,'id'] = str(row['uuid'])[0:8]
        #ph.success('Datos cargados correctamente')
        # Pretend we're doing some computation that takes time.
        #time.sleep(1.7)
        ph.empty()

        col1, col2, col3 = st.columns([1,2,1])

        x = inflate_preview_column(col1,data)
        inflate_map_column(col2,data,x)
        new_data = inflate_modification_column(col3,data,file)
        st.session_state.data = new_data
        #print(st.session_state.data)
        st.markdown('---')
        save_modifications_display(data,new_data,file)


    #'''Made with :heart: by LSI.'''

def inflate_preview_column(col, data):
    with col:
        st.header('Tabla Valores')
        st.dataframe(data.head(400))
        #st.write('## Alertas:',0)
        st.markdown("---")
        st.write('## Configuración de mapa')
        r = st.slider('Radio de los puntos', min_value=1, max_value=10, value=5, step=1)
        st.markdown("---")
        st.write('## Aplicación')
        refresh = st.button("Refrescar datos e interfaz")
        return r

def inflate_map_column(col,df,x):

    with col:
        st.header('Mapa')
        mp = st.empty()

        df['colors'] = colors_dict(df['clase_str'].to_list())
        mp.pydeck_chart(pdk.Deck(
        map_style='mapbox://styles/mrodrigueza/ck8fw3dx139zl1invheqydp3j',
        initial_view_state=pdk.ViewState(
            latitude= np.mean(df['lat'].to_numpy()), 
            longitude= np.mean(df['lon'].to_numpy()),
            zoom=16,
            pitch=0,
            height=590,
        ),
        layers=[
            pdk.Layer(
                'ScatterplotLayer',
                data=df[['lon','lat','clase_str','streetlight_date','streetlight_date', 'streetlight_angle', 'streetlight_height','lux_aux','colors','id','streetlight_date']],
                get_position='[lon,lat]',
                get_radius = x,
                opacity = 1,
                get_color = 'colors',#'[255, 242, 0]', #df['clase_str'].applymap(lambda x: colors[x]),
                pickable=True 
            ) 
        ],
        tooltip={
                    'html': '<b>Fecha:</b> {streetlight_date} <br> <b> Id:</b> {id} <br> <b> ts:</b> {streetlight_date}<br> <b> Clase:</b> {clase_str} <br> <b> Luz:</b> {lux_aux} <br> <b> Altura:</b> {streetlight_height} <br> <b> Ángulo:</b> {streetlight_angle}' ,
                    'style': 
                    {
                        "backgroundColor": "steelblue",
                        'color': 'white'
                    }
                }
    ), use_container_width=True)

        st.image(load_image('leyenda.png'), use_column_width=True)

def inflate_modification_column(col,data,my_file):
    with col:
        st.header('Inspección')
        cloud = st.selectbox('Luminaria a estudiar', data['id'].to_list())
        with st.form("my_form"):
            #st.image('Std_Lamparon.png',use_column_width=True)
            #st.plotly_chart(get_plotly_fig_hd(pd.read_csv('/home/marcos/Escritorio/cluster_3_6_2019_18_56_20_10.csv')),use_container_width=True) #hard-coded -> change in future
            register = data[data['id']==cloud].iloc[0]
            st.plotly_chart(get_plotly_fig(get_xyz_from_dict(decode_cjson(register['jpoints']))),use_container_width=True) #hard-coded -> change in future
            st.markdown("---")
            st.write('**_Clase sugerida por el sistema_**: ', '<span style="color:blue">{0}</span>'.format(register['clase_str']), unsafe_allow_html=True)
            l = st.selectbox('Nueva clase', labels)
            submitted = st.form_submit_button("Modificar")

        if submitted:
            for i,row in data.iterrows():
                if row['uuid'] == register['uuid']:
                    data.loc[i,'clase_str'] = l
                    st.session_state.data = data
                    
            #print(my_file)
            #data.to_csv(my_file)
    return data

def get_plotly_fig(xyz_tuple):
    fig = go.Figure(data=[go.Scatter3d(x=xyz_tuple[0], y=xyz_tuple[1], z=xyz_tuple[2], mode='markers',marker=dict(size=1))])
    fig.update_layout(margin=dict(l=20,r=0,b=0,t=0))
    fig.update_scenes(xaxis_visible=False, yaxis_visible=False, zaxis_visible=False)
    return fig


def get_plotly_fig_hd(df):
    fig = go.Figure(data=[go.Scatter3d(x=df.x, y=df.y, z=df.z, mode='markers',marker=dict(size=1.5))])
    fig.update_layout(margin=dict(l=20,r=0,b=0,t=0),autosize=False,width=800,height=200,)
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

def decode_cjson(cjson_str):
    #print(type(cjson_str))
    #print(cjson_str)
    json_str = cjson_str.replace('*',',')
    return json.loads(json_str)

def get_xyz_from_dict(obj):
    return (obj['x'],obj['y'],obj['z'])

def save_modifications_display(data,new_data,file):
    st.write('## Guardar y exportar')
    l,r = st.columns([1,1])
    r.write("")
    r.write("")
    
    name = l.text_input('Nombre del archivo', file.name[0:-3] + "xlsx")
    save = r.button("Exportar")
    if save:
        new_data.to_excel(name,'Datos luminarias',columns=['uuid','clase_str','streetlight_date','lon','lat','streetlight_x_utm','streetlight_y_utm','streetlight_street', 'streetlight_angle', 'streetlight_height','lux_aux','potencia','tipo lampara'])
        st.success("Exportado correctamente")
        towrite = io.BytesIO()
        downloaded_file = new_data.to_excel(towrite, encoding='utf-8', index=False, header=True, columns=['uuid','streetlight_date','streetlight_date','lon','lat','streetlight_x_utm','streetlight_y_utm','streetlight_street','clase_str', 'streetlight_angle', 'streetlight_height','lux_aux','potencia','tipo lampara'])
        towrite.seek(0)  #reset pointer
        b64 = base64.b64encode(towrite.read()).decode() #some strings
        linko= f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download={name}>Descargar Archivo Excel</a>'
        st.markdown(linko, unsafe_allow_html=True)

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