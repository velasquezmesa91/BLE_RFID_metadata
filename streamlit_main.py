import streamlit as st
import pandas as pd
from streamlit import session_state as ss
import numpy as np

#Session States
if 'page_title' not in ss:
    ss["page_title"] = "Formulario de registro metadatos" 
if "button_state" not in ss:
    ss["button_state"]=False
if "final_data" not in ss:
    ss["final_data"] = pd.DataFrame()

#Callbacks
def change_title():
    ss["page_title"] = "Formulario de registro metadatos " + tipo_dispositivos
def shutdown():
    ss["button_state"]=True
def enable():
    ss["button_state"]=False
def revision():
    ss["final_data"] = final_df


#Sidebar
    


st.title("Formulario de Registro Metadatos" )
tab1, tab2 = st.tabs(["Hablador","Registro de datos"])

with tab1:
    with st.container(border=True):
        st.subheader("Hablador")
        tipo_dispositivos = st.radio("Seleccione dispositivos",["RFID","RFID + BLE"])
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

        #st.caption("Por favor revise que la información en el hablador sea correcta y que haya registrado correctamente los códigos de las canastillas antes de descargar el archivo")
        #descargar = st.download_button("Descargar",data=ss["final_data"],
         #                              file_name=f"{lote} {responsable1}-{responsable2}.xlsx")
        

with tab2:
    if tipo_dispositivos == "RFID":
        df = pd.DataFrame({"Serial": [None]*560})

        edited_df = st.data_editor(
            data=df,
            column_config={
            "Serial":st.column_config.TextColumn("Serial")}
                                )

    elif tipo_dispositivos == "RFID + BLE":
        indexes = [np.ceil(x/3) for x in range(1,1681)]
        df = pd.DataFrame(
            {"index":indexes,
            "Tipo Dispositivo":["RFID","BLE","RFID"]*560,
            "Serial": [None]*1680,
            }
                            )
        edited_df = st.data_editor(
            data=df,
            column_config={
            "index": st.column_config.NumberColumn("Index",disabled=True),
            "Tipo Dispositivo":st.column_config.TextColumn("Tipo Dispositivo", disabled=True),
            "Serial":st.column_config.TextColumn("Serial", width=250)
            },
            hide_index=True
                                )

        #Chequeos 
        #ind_ble= edited_df["Tipo Dispositivo"] == "BLE"
        #ind_rfid= edited_df["Tipo Dispositivo"] == "RFID"
        rfid =edited_df.loc[edited_df["Tipo Dispositivo"] == "RFID",:]
        ble = edited_df.loc[edited_df["Tipo Dispositivo"] == "BLE",:]
        #Se comprueba si hay duplicados
        duplicados_rfid = (rfid.loc[:,"Serial"].value_counts() >2)
        duplicados_ble = (ble.loc[:,"Serial"].value_counts() >1)
        #Comprueba la longitud de los seriales
        lon_rfid = rfid.dropna().loc[:,"Serial"].str.len()!=27
        lon_ble = ble.dropna().loc[:,"Serial"].str.len()!=7
      
        if duplicados_rfid.sum()>0:
            st.error(f"¡HAY VALORES DUPLICADOS! Los valores {list(duplicados_rfid[duplicados_rfid].index)} se han duplicado, corrijalos antes se seguir el escaneo")
        elif duplicados_ble.sum()>0:
            st.error(f"¡HAY VALORES DUPLICADOS! Los valores {list(duplicados_ble[duplicados_ble].index)} se han duplicado, corrijalos antes se seguir el escaneo")
        
        if any(lon_rfid):
            st.error(f"¡HAY VALORES ERRÓNEOS! Los valores {rfid.dropna().loc[lon_rfid,"Serial"].values} NO corresponden a un serial RFID, corríjalos antes de continuar con el escaneo")
        elif any(lon_ble):
            st.error(f"¡HAY VALORES ERRÓNEOS! Los valores {ble.dropna().loc[lon_ble,"Serial"].values} NO corresponden a un serial BLE, corríjalos antes de continuar con el escaneo")

        revisar = st.button("Revisar Datos", type="primary")

        if revisar:
            final_df = edited_df.dropna()
            rfid_unico =final_df.loc[final_df["Tipo Dispositivo"] == "RFID","Serial"].unique()
            ble_unico = final_df.loc[final_df["Tipo Dispositivo"] == "BLE","Serial"].unique()

            if (tamaño == "60x40x25") & (len(rfid_unico)!=210):
                st.error(f"Hay {len(rfid_unico)} dispositivos RFID registrados, una estiba de tamaño {tamaño} contiene 210 canastillas, compruebe nuevamente el registro")
            elif (tamaño == "30x40x15") & (len(rfid_unico)!=560):
                st.error(f"Hay {len(rfid_unico)} dispositivos RFID registrados, una estiba de tamaño {tamaño} contiene 560 canastillas, compruebe nuevamente el registro")
            elif (tamaño == "60x40x25") & (len(ble_unico)!=210):
                st.error(f"Hay {len(ble_unico)} dispositivos BLE registrados, una estiba de tamaño {tamaño} contiene 210 canastillas, compruebe nuevamente el registro")
            elif (tamaño == "30x40x15") & (len(ble_unico)!=560):
                st.error(f"Hay {len(ble_unico)} dispositivos BLE registrados, una estiba de tamaño {tamaño} contiene 560 canastillas, compruebe nuevamente el registro")
            else:
                st.success("¡Ha pasado la revisión inicial! Descargue el archivo y envíelo al supervisor para revisión")
                st.caption("Por favor revise que la información en el hablador sea correcta y que haya registrado correctamente los códigos de las canastillas antes de descargar el archivo")
                @st.cache_data
                def convert_df(df):
                    return df.to_csv(index=False).encode('utf-8')
                data = convert_df(final_df)

                st.download_button(
                    label="Descargar archivo",
                    data=data,
                    file_name=f"{lote} {responsable1}-{responsable2}.csv",
                    mime='text/csv',
                )




        



    
           

        


#favorite_command = edited_df.loc[edited_df["rating"].idxmax()]["command"]
#st.markdown(f"Your favorite command is **{favorite_command}** 🎈")