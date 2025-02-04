import numpy as np
import explorepy as exp
import matplotlib.pyplot as plt
import pandas as pd
from scipy import signal
from scipy.fft import fft, fftfreq, rfft


def importar_archivos(nombre): #solo poner el nombre del archivo (no ExG). solo formato csv

    df= pd.read_csv(str(f'{nombre}_ExG.csv'), delimiter ="," )
    offset=df["TimeStamp"][0]
    df["TimeStamp"]= df["TimeStamp"] - df["TimeStamp"][0]
    df= df.rename(columns= {"TimeStamp" : "Tiempo"})
    return df, offset

def custom_filter(exg, lf, hf, fs, type):
    """
    Args:
        exg: EEG signal with the shape: (N_chan, N_sample)
        lf: Low cutoff frequency
        hf: High cutoff frequency
        fs: Sampling rate
        type: Filter type, 'bandstop' or 'bandpass'
    Returns:
        (numpy ndarray): Filtered signal (N_chan, N_sample)
    """
    N = 4
    b, a = signal.butter(N, [lf / (fs/2), hf / (fs/2)], type)
    return signal.filtfilt(b, a, exg)

def Analizar_Archivos(Datos, Markers):
    fs = 250
    lf = 5
    hf = 30
    tiempo= Datos["Tiempo"]
    Escala = 100
    Rango=int(len(Markers)-1)
    # Rango=1
    for n in range(0, Rango):
        # if n%2 == 0: 
        fig, axes = plt.subplots(4, 2, figsize = (10, 8))
        fig.text(0.30, 0.04, "Tiempo [$s$]", ha='center', fontsize=14, fontweight="bold")
        fig.text(0.73, 0.04, r"Frecuencia [$Hz$]", ha='center', fontsize=14, fontweight="bold")
        fig.text(0.04, 0.5, r"Tensión [$\mu V$]", va='center', rotation='vertical', fontsize=14, fontweight="bold")
        fig.text(0.5, 0.5, "Intensidad [$s/u$]", va='center', rotation='vertical', fontsize=14, fontweight="bold")
        Inicio = n
        Fin = n+1
        desde = int(Markers["TimeStamp"][Inicio]*250)
        hasta = int(Markers["TimeStamp"][Fin]*250)
        chanels=[1,2,5,6]
        color = ["blue", "orange", "red", "green"]
        for j in range(4):
            filt_sig = custom_filter(Datos[f"ch{chanels[j]}"][desde:hasta], 45, 55, fs, 'bandstop')
            filt_sig = custom_filter(filt_sig, lf, hf, fs, 'bandpass')
            axes[j][0].plot(tiempo[desde:hasta], filt_sig, label = f"Ch{chanels[j]}", color = color[j])
            axes[j][0].set_ylim(-Escala, Escala)
            N=len(tiempo[desde:hasta])
            norma= 1/N
            Transformada = rfft(filt_sig)*norma
            Frecuencias = fftfreq(N, 1/250)
            axes[j][1].plot(Frecuencias[:N//2], Transformada[:N//2])
            axes[j][1].set_xlim(5,30)
            axes[j][1].grid()
            for i in range(Inicio, Fin+1):
                axes[j][0].axvline(Markers["TimeStamp"][i], ls="--", color="black")
            fig.legend()
        plt.show()
        


Datos2, offset2 = importar_archivos(r"C:\Users\dell\Desktop\Facu Fisica\labo6\Medicion3\Medicion3")
Markers2 = pd.read_csv(r"C:\Users\dell\Desktop\Facu Fisica\labo6\Medicion3/Medicion3_Marker.csv", delimiter ="," )
Markers2["TimeStamp"] = Markers2["TimeStamp"] - offset2

Analizar_Archivos(Datos2, Markers2)

