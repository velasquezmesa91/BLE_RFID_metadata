import streamlit as st
import pandas as pd
from streamlit import session_state as ss
import numpy as np

st.title("Chequeos formulario metadatos" )
tab1, tab2, tab3 = st.tabs(["Chequeo Individual","Chequeo Pares","Chequeo Grupal"])
bad_serials = pd.read_excel("bad_serials.xlsx")
with tab1:
    arch1 = st.file_uploader("Cargue el archivo a revisar")
    if arch1:
        df1 = pd.read_excel(arch1, skiprows=4)
        df1 = df1.loc[:,["ID","Device Descr",	"Device ID"]]
        df1.dropna(subset="Device ID", inplace=True)
        rfid_ind = df1["Device Descr"] == "RFID Tag"
        ble_ind = df1["Device Descr"] == "GPS Device"

        BLE_unico = len(df1.loc[ble_ind,"Device ID"].unique())
        RFID_unico = len(df1.loc[rfid_ind,"Device ID"].unique())
        BLE_duplicado = (df1.loc[ble_ind,"Device ID"].value_counts() > 1).sum()
        RFID_duplicado = (df1.loc[rfid_ind,"Device ID"].value_counts() > 2).sum()
        BLE_long = df1.loc[ble_ind,"Device ID"].str.len().unique()
        RFID_long = df1.loc[rfid_ind,"Device ID"].str.len().unique()

        if BLE_unico !=210:
            st.error(f"Hay {BLE_unico} BLE registrados y deberian ser 210, revise el archivo")
        elif RFID_unico != 210:
            st.error(f"Hay {RFID_unico} RFIS registrados y deberian ser 210, revise el archivo")
        elif BLE_duplicado >0:
            st.error("Hay dispositivos BLE duplicados, revise el archivo")
            duplicados_ble = df1.loc[(df1.loc[ble_ind,"Device ID"].value_counts() > 1),"Device ID"]
            st.write(f"Duplicados:{duplicados_ble}")
        elif RFID_duplicado >0:
            st.error("Hay dispositivos RFID duplicados, revise el archivo")
            duplicados_rfid = df1.loc[(df1.loc[rfid_ind,"Device ID"].value_counts() > 2),"Device ID"]
            st.write(f"Duplicados:{duplicados_rfid}")
        elif len(BLE_long) >1:
            if (BLE_long[0]!=7 )| (BLE_long[1]!=7):
                st.error("Hay un serial que no corresponde a BLE, revise el archivo")
                mala_lon = df1.loc[df1.loc[ble_ind,"Device ID"].str.len() !=7,"Device ID"]
                st.write(mala_lon)
        elif len(RFID_long) >1:
            if (BLE_long[0]!=27 )| (BLE_long[1]!=27):
                st.error("Hay un serial que no corresponde a RFID, revise el archivo")
                mala_lon_rfid = df1.loc[df1.loc[rfid_ind,"Device ID"].str.len() !=27,"Device ID"]
                st.write(mala_lon_rfid)
        else:
            st.success("Ha pasado los chequeos iniciales, cargue el archivo a la carpeta correspondiente")

        #RFID_bad = bad_serials.ID.isin(df1.loc[rfid_ind,"Device ID"]).sum()
        #print(f"Numero de Seriales malos estiba 1: {RFID_bad}")



        #st.dataframe(df, skiprows=4)




