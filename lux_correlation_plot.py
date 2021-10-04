import pandas as pd
import pydeck as pdk
import numpy as np
import streamlit as st

def main():
    st.write('## Carga de datos')
    file = st.file_uploader('Seleccione el archivo .csv que quiera analizar',type='csv')

    ph = st.empty()
    if file is not None:
        df = pd.read_csv(file)
        df["end_lat"] = ""
        df["end_lon"] = ""

        for i,row in df.iterrows():
            df.loc[i,"end_lat"] = row["lat"] + row["v_lat"]
            df.loc[i,"end_lon"] = row["lon"] + row["v_lon"]
        
        st.header('Mapa')
        mp = st.empty()
    
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
                data=df[['lon','lat']],
                get_position='[lon,lat]',
                get_radius = 1,
                opacity = 1,
                get_color = '[3, 252, 140]', #df['clase_str'].applymap(lambda x: colors[x]),
                pickable=True 
            ),
            pdk.Layer(
                'ScatterplotLayer',
                data=df[['end_lon','end_lat']],
                get_position='[end_lon,end_lat]',
                get_radius = 1,
                opacity = 1,
                get_color = '[255, 242, 0]', #df['clase_str'].applymap(lambda x: colors[x]),
                pickable=True 
            ),
            pdk.Layer(
                'LineLayer',
                data=df[['lon','lat','end_lon','end_lat']],
                get_source_position='[lon,lat]',
                get_target_position='[end_lon,end_lat]',
                get_color=[255,0,0,200],
                get_width=3,
                highlight_color=[255, 255, 0],
                picking_radius=10,
                auto_highlight=True,
                pickable=True,
            )],
        ), use_container_width=True)

if __name__ == "__main__":
    st.set_page_config(
        page_title='Lumilas lux correlation',
        page_icon=':zap:',
        layout='wide',
        initial_sidebar_state='collapsed',
        )
        
    main()