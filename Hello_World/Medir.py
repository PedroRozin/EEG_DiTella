import numpy as np
import explorepy as exp #la biblio de mentalab que se usa siempre para comunicarse con el EEG 
import matplotlib.pyplot as plt
import pandas as pd
import msvcrt
import time

def main():
    EEG = exp.Explore() #creo el objeto EEG
    EEG.connect("Explore_8575") #lo conecto por bluetooth con su nombre (Explore_8575 es el del labo)
    T_inicial=time.monotonic()
    print(T_inicial)
    EEG.record_data(file_name=r"C:\Users\iandersen\Documents\Python Scripts\Delay\Delay", do_overwrite=True) #acá empieza el record
    Conectado = True
    while(Conectado == True):
        print('Ingrese comando')
        Entrada=input()
        if Entrada == "Off":
            EEG.stop_recording() #acá se frena el recording
            T_final=time.monotonic()
            print(T_final)
            EEG.disconnect() #acá se desconecta el bluetooth
            Conectado = False
            break
        if Entrada == "Markers": #creo el "Modo markers".
            i=1
            print("Presione 'Space' para colocar un marker y 'Esc' para salir del modo Markers")
            key = None
            while key != '\x1b': #'\x1b' == Esc.
                key = msvcrt.getwch()
                if key == ' ': #" '= Space
                    EEG.set_marker(i) #comando para agregar el marker i-ésimo
                    EEG.set_external_marker(EEG.stream_processor._get_sw_marker_time(), 'Custom')
                    i=i+1
                if key == '\x1b':
                    print('Saliste del modo Markers')
                    break
main()
