import streamlit as st
import pandas as pd
from streamlit import session_state as ss
import numpy as np

st.title("Chequeos formulario metadatos" )
tab1, tab2, tab3 = st.tabs(["Chequeo Individual","Chequeo Pares","Solo RFID"])
bad_serials = pd.read_excel("bad_serials.xlsx")
with tab1:
    arch1 = st.file_uploader("Cargue el archivo a revisar")
    if arch1:
        df1 = pd.read_excel(arch1, skiprows=4)
        df1 = df1.loc[:,["ID","Device Descr",	"Device ID"]]
        df1.dropna(subset="Device ID", inplace=True)
        rfid = df1[df1["Device Descr"] == "RFID Tag"]
        ble = df1[df1["Device Descr"] == "GPS Device"]

        BLE_unico = len(ble["Device ID"].unique())
        RFID_unico = len(rfid["Device ID"].unique())
        BLE_duplicado = (ble["Device ID"].value_counts() > 1)
        RFID_duplicado = (rfid["Device ID"].value_counts() > 2)
        BLE_long = ble["Device ID"].str.len().unique()
        RFID_long = rfid["Device ID"].str.len().unique()
        errores=0
        if BLE_unico !=210:
            errores+=1
            st.error(f"Hay {BLE_unico} BLE registrados y deberian ser 210, revise el archivo")
        if RFID_unico != 210:
            errores+=1
            st.error(f"Hay {RFID_unico} RFID registrados y deberian ser 210, revise el archivo")
        if any(BLE_duplicado):
            errores+=1
            st.error("Hay dispositivos BLE duplicados, revise el archivo")
            st.write(f"**Dispositivo(s) duplicado(s)**: {BLE_duplicado[BLE_duplicado].index[0]}")
        if any(RFID_duplicado):
            errores+=1
            st.error("Hay dispositivos RFID duplicados, revise el archivo")
            st.write(f"**Dispositivo(s) duplicado(s)**: {RFID_duplicado[RFID_duplicado].index[0]}")
        if len(BLE_long) >1:
            errores+=1
            if (BLE_long[0]!=7 )| (BLE_long[1]!=7):
                st.error("Hay un serial que no corresponde a BLE, revise el archivo")
                ble_wrong_len = [x for x in BLE_long if x != 7][0]
                ble_wrong_len =ble[ble["Device ID"].str.len() ==ble_wrong_len]
                st.dataframe(ble_wrong_len)
        if len(RFID_long) >1:
            errores+=1
            if (RFID_long[0]!=27 )| (RFID_long[1]!=27):
                st.error("Hay un serial que no corresponde a RFID, revise el archivo")
                rfid_wrong_len = [x for x in RFID_long if x != 27][0]
                rfid_wrong_len =rfid[rfid["Device ID"].str.len() ==rfid_wrong_len]
                st.dataframe(rfid_wrong_len)

        if errores==0:
            st.success("Ha pasado los chequeos iniciales, cargue el archivo a la carpeta correspondiente")          
        else:
            st.error(f"TIENE {errores} ERRORES, revise el archivo nuevamente")
            
with tab2:
    arch2 = st.file_uploader("Cargue los dos archivos", accept_multiple_files=True)
    if arch2:
        df_t1 = pd.read_excel(arch2[0], skiprows=4)
        df_t2 = pd.read_excel(arch2[1], skiprows=4)
        df_t1 = df_t1.loc[:,["ID","Device Descr",	"Device ID"]]
        df_t2 = df_t2.loc[:,["ID","Device Descr",	"Device ID"]]
        df_t1.dropna(subset="Device ID", inplace=True)
        df_t2.dropna(subset="Device ID", inplace=True)
        rfid1 = df_t1.loc[df_t1["Device Descr"] == "RFID Tag","Device ID"]
        ble1 = df_t1.loc[df_t1["Device Descr"] == "GPS Device", "Device ID"]
        rfid2 = df_t2.loc[df_t2["Device Descr"] == "RFID Tag", "Device ID"]
        ble2 = df_t2.loc[df_t2["Device Descr"] == "GPS Device", "Device ID"]

        #Union
        df12 = df_t1.drop_duplicates(subset=("Device ID"))
        df22 = df_t2.drop_duplicates(subset=("Device ID"))
        tm = df12.merge(df22, on="Device ID", how="inner").shape

        #Join
        
        df12 = df12.pivot(index="ID", columns="Device Descr").droplevel(level=0, axis=1)
        df22 = df22.pivot(index="ID", columns="Device Descr").droplevel(level=0, axis=1)

        df12["key"] = df12["GPS Device"] + "--" + df12["RFID Tag"]
        df22["key"] = df22["GPS Device"] + "--" + df22["RFID Tag"]

        df_join = df12.merge(df22, on="key", how="inner",suffixes=["","_R"])

        if tm[0]!=420:
            st.error("Los archivos tienen diferentes seriales, revise los archivos")

            st.write(f"RFID en archivo 1 y no en 2: {rfid1[~rfid1.isin(rfid2)].unique()}")
            st.write(f"RFID en archivo 2 y no en 1: {rfid2[~rfid2.isin(rfid1)].unique()}")
            st.write(f"BLE en archivo 1 y no en 2: {ble1[~ble1.isin(ble2)].unique()}")
            st.write(f"BLE en archivo 2 y no en 1: {ble2[~ble2.isin(ble1)].unique()}")

        elif df_join.shape[0] !=210:
            st.error("Los archivos tienen diferentes seriales, revise los archivos")
            st.write(f"RFID en archivo 1 y no en 2: {rfid1[~rfid1.isin(rfid2)].values}")
            st.write(f"RFID en archivo 2 y no en 1: {rfid2[~rfid2.isin(rfid1)].values}")
        else:
            st.success("Ambos archivos estan correctos!")
            @st.cache_data
            def convert_df(df):
                return df.to_csv(index=False).encode('utf-8')
            data = convert_df(df_join["GPS Device"])

            descargar=st.download_button(
                label="Descargar archivo",
                data=data,
                file_name=f"SerialesBLE.csv",
                mime='text/csv',
            )

with tab3:
    arch3 = st.file_uploader("Cargue los dos archivos", accept_multiple_files=True, key="rfid")
    if arch3:
        df_rfid1 =pd.read_excel(arch3[0])[["Serial"]].dropna()
        df_rfid2 = pd.read_excel(arch3[1])[["Serial"]].dropna()
        df_rfid_join = df_rfid1.merge(df_rfid2, how="inner",on="Serial")
        errores =0


        if any(df_rfid1.duplicated()):
            errores+=1
            st.error("Hay un serial duplicado en el archivo 1 revise el archivo")
            st.dataframe(df_rfid1[df_rfid1.duplicated()])
        if any(df_rfid2.duplicated()):
            errores+=1
            st.error("Hay un serial duplicado en el archivo 2 revise el archivo")
            st.dataframe(df_rfid2[df_rfid2.duplicated()])
        if len(df_rfid1["Serial"].str.len().unique())>1:
            errores+=1
            st.error("Hay seriales que no corresponden en el archivo 1 a RFID. revise el archivo")
        if len(df_rfid2["Serial"].str.len().unique())>1:
            errores+=1
            st.error("Hay seriales que no corresponden en el archivo 2 a RFID. revise el archivo")
        if df_rfid1.shape[0] != 560:
            errores+=1
            st.error(f"Hay {df_rfid1.shape[0]} seriales únicos en el archivo 1, deberian haber 560, revise el archivo")
        if df_rfid2.shape[1] != 560:
            errores+=1
            st.error(f"Hay {df_rfid2.shape[0]} seriales únicos en el archivo 2, deberian haber 560, revise el archivo")   
        if df_rfid_join.shape[0] != 560:
            errores+=1
            st.error("Los archivos tienen seriales diferentes, reviselos")
        
        uno_no_en_dos = df_rfid1[(~df_rfid1.Serial.isin(df_rfid2.Serial))]
        dos_no_en_uno = df_rfid2[(~df_rfid2.Serial.isin(df_rfid1.Serial))]
        if len(uno_no_en_dos)>0:
            errores+=1
            st.error("Hay Seriales en el archivo uno que no estan en el 2")
            st.write(f"Seriales en archivo 1 y no en archivo 2:")
            st.dataframe(uno_no_en_dos)
        if len(dos_no_en_uno)>0:
            errores+=1
            st.error("Hay Seriales en el archivo dos que no estan en el 1")
            st.write(f"Seriales en archivo 2 y no en archivo 1:")
            st.dataframe(dos_no_en_uno)
        seriales_malos1 =df_rfid1.Serial.isin(bad_serials.ID)
        seriales_malos2 =df_rfid2.Serial.isin(bad_serials.ID)
        if any(seriales_malos1):
            errores+=1
            st.error("El archivo 1 tiene seriales malos, retirelos de la estiba")
            st.dataframe(df_rfid1[df_rfid1.Serial.isin(bad_serials.ID)])
        if any(seriales_malos2):
            errores+=1
            st.error("El archivo 2 tiene seriales malos, retirelos de la estiba")
            st.dataframe(df_rfid2[df_rfid2.Serial.isin(bad_serials.ID)])
        if errores ==0:
            st.success("Los archivos estan correctos, puede liberar la estiba")
        
        


   
         




        #st.dataframe(df, skiprows=4)




