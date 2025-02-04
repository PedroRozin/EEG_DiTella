import numpy as np
import explorepy as exp
import matplotlib.pyplot as plt
import pandas as pd
import msvcrt
import time
EEG = exp.Explore()
EEG.connect("Explore_8575")
# EEG.acquire()
T_inicial=time.monotonic()
print(T_inicial)
EEG.record_data(file_name=r"C:\Users\iandersen\Documents\Python Scripts\Delay\Delay", do_overwrite=True)
Conectado = True
while(Conectado == True):
    print('Ingrese comando')
    Entrada=input()
    if Entrada == "Off":
        EEG.stop_recording()
        T_final=time.monotonic()
        print(T_final)
        EEG.disconnect()
        Conectado = False
        break
    if Entrada == "Markers":
        i=1
        print("Presione 'Space' para colocar un marker y 'Esc' para salir del modo Markers")
        key = None
        while key != '\x1b':
            key = msvcrt.getwch()
            if key == ' ':
                EEG.set_marker(i)
                EEG.set_external_marker(EEG.stream_processor._get_sw_marker_time(), 'Custom')
                i=i+1
            if key == '\x1b':
                print('Saliste del modo Markers')
                break
print(T_final-T_inicial)

def importar_archivos(nombre): #solo poner el nombre del archivo (no ExG). solo formato csv

    df= pd.read_csv(str(f'{nombre}_ExG.csv'), delimiter ="," )
    offset=df["TimeStamp"][0]
    df["TimeStamp"]= df["TimeStamp"] - df["TimeStamp"][0]
    df= df.rename(columns= {"TimeStamp" : "Tiempo"})
    DeltaT= df["Tiempo"][len(df["Tiempo"])-1]
    return df, offset, DeltaT

Datos, offset, DeltaT = importar_archivos(r"./Delay/Delay")

print(T_final-T_inicial-DeltaT)