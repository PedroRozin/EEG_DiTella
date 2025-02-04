import numpy as np
import explorepy as exp
import matplotlib.pyplot as plt
import pandas as pd
import msvcrt
import time

def main():
    EEG = exp.Explore()
    EEG.connect("Explore_8575")
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
main()
