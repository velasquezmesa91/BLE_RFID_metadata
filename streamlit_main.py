import streamlit as st
import pandas as pd
from streamlit import session_state as ss
import numpy as np

#Session States
if 'page_title' not in ss:
    ss["page_title"] = "Formulario de registro metadatos" 
if "button_state" not in ss:
    ss["button_state"]=False

#Callbacks
def change_title():
    ss["page_title"] = "Formulario de registro metadatos " + tipo_dispositivos
def shutdown():
    ss["button_state"]=True
def enable():
    ss["button_state"]=False


#Sidebar
with st.sidebar:
    st.title("configuracion")
    tipo_dispositivos = st.radio("Seleccione dispositivos",["RFID","RFID + BLE"])



st.title("Formulario de Registro Metadatos" )

with st.form("my_form"):
    st.subheader("Hablador")
    col1,col2, col3 = st.columns(3)
    col4,col5, col6 = st.columns(3)
    col7,col8, col9 = st.columns(3)

    with col1:
        ciudad = st.selectbox("Seleccione la ciudad",["BOGOTA","MEDELLIN"])
    
    with col2:
        tipo_molde = st.selectbox("Seleccione el tipo de molde",["ESTECO","PRO25"])

    with col3:
        tamaño = st.selectbox("Seleccione el tamaño de canastilla",
                            ["60x40x13","60x40x18","60x40x25",
                            "60x40x24","30x40x15","30x40x21","60x40x21"])
    with col4:
        color = st.selectbox("Seleccione el color de canastilla",["NEGRO","VERDE"])

    with col5:
        equipo = st.selectbox("Seleccione el equipo de registro",["2D SCANNER"])

    with col6:
        cantidad = st.number_input("Ingrese la cantidad de canastillas",min_value=0)

    
    with col7:
        lote = st.text_input("Ingrese el lote o numero de estiba",
                        placeholder="EST-00-01122023",
                        help="Recuerde que el lote se construye con: EST-#Número estiba-DíaMesAño"
                        )
    with col8:
        responsable1= st.text_input("Ingrese el nombre del responsable 1")
    with col9:
        responsable2= st.text_input("Ingrese el nombre del responsable 2")

    # Every form must have a submit button.
    submitted = st.form_submit_button("Actualizar hablador", type="primary")

    if submitted:
        hablador=pd.DataFrame(
                {
                    "variables":["Ciudad","Tipo Molde","Tamaño", "Color",
                        "Equipo de resgitro","Dispositivo","Cantidad", "Lote","Responsables"],
                    "":[ciudad,tipo_molde, tamaño,color, equipo,tipo_dispositivos, cantidad, lote,
                        responsable1+"-"+responsable2 ]
                }
                )
        hablador.set_index("variables", inplace=True)
        st.table(hablador)
        st.caption("Por favor revise que la información en el hablador sea correcta antes de descargar el archivo")
        


if tipo_dispositivos == "RFID":
    df = pd.DataFrame({"Serial": [None]*560})

    edited_df = st.data_editor(
        data=df,
        column_config={
        "Serial":st.column_config.TextColumn("Serial")}
                            )

elif tipo_dispositivos == "RFID + BLE":
    indexes = [np.ceil(x/3) for x in range(1,10)]
    df = pd.DataFrame(
        {"index":indexes,
        "Tipo Dispositivo":["RFID","BLE","RFID"]*3,
        "Serial": [None]*9,
        }
                        )
    edited_df = st.data_editor(
        data=df,
        column_config={
        "index": st.column_config.NumberColumn("Index",disabled=True),
        "tipo dispositivo":st.column_config.TextColumn("Tipo Dispositivo", disabled=True),
        "Serial":st.column_config.TextColumn("Serial")},
        hide_index=True
                            )


#favorite_command = edited_df.loc[edited_df["rating"].idxmax()]["command"]
#st.markdown(f"Your favorite command is **{favorite_command}** 🎈")