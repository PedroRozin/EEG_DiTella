import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import butter, filtfilt, resample, hilbert, correlate
from sklearn.cross_decomposition import CCA
from scipy.stats import pearsonr
import os
from tqdm import tqdm
from scipy.interpolate import CubicSpline



def custom_filter(signal, lf, hf, fs, ftype):
    """
    Aplica un filtro personalizado a la señal.
    """
    N = 4
    b, a = butter(N, [lf / (fs / 2), hf / (fs / 2)], ftype)
    return filtfilt(b, a, signal)

def butter_lowpass(cutoff, fs, order=3):
    """
    Diseña un filtro de paso bajo.
    """
    nyq = 0.5 * fs
    normal_cutoff = cutoff / nyq
    b, a = butter(order, normal_cutoff, btype='low', analog=False)
    return b, a

def butter_lowpass_filter(data, cutoff, fs, order=3):
    """
    Aplica un filtro de paso bajo a la señal.
    """
    b, a = butter_lowpass(cutoff, fs, order=order)
    return filtfilt(b, a, data)

def resample_signal(signal, original_fs, target_fs):
    """
    Realiza el remuestreo de una señal.
    """
    num_samples = int(len(signal) * target_fs / original_fs)
    return resample(signal, num_samples)

def obtener_envolvente(signal, fs, cutoff=45):
    """
    Obtiene la envolvente de una señal y su derivada utilizando un filtro de paso bajo.
    
    Args:
        signal (array): Señal de entrada.
        fs (float): Frecuencia de muestreo.
        cutoff (float): Frecuencia de corte para el filtro de paso bajo.
        cutoff2 (float, opcional): Frecuencia de corte para el filtro adicional (comentado por defecto).
    
    Returns:
        tuple: Amplitud envolvente filtrada y su derivada.
    """
    # Transformada de Hilbert y cálculo de la envolvente
    analytic_signal = hilbert(signal)
    amplitud_envolvente = np.abs(analytic_signal)
    
    # Filtro de paso bajo
    b, a = butter(3, cutoff / (0.5 * fs), btype='low')
    envolvente_filtrada = filtfilt(b, a, amplitud_envolvente)
    
    return envolvente_filtrada

def butter_highpass(cutoff, fs, order=3):
    nyquist = 0.5 * fs  # Frecuencia de Nyquist
    normal_cutoff = cutoff / nyquist  # Frecuencia de corte normalizada
    b, a = butter(order, normal_cutoff, btype='high', analog=False)
    return b, a

def butter_highpass_filter(data, cutoff, fs, order=3):
    b, a = butter_highpass(cutoff, fs, order=order)
    y = filtfilt(b, a, data)
    return y

def remove_outliers(data, threshold=1.5):
    """
    Elimina outliers de una señal utilizando el rango intercuartil (IQR).
    También maneja bloques de NaN seguidos mediante interpolación spline y relleno de extremos.
    """
    # Calcular los cuartiles 1 (Q1) y 3 (Q3)
    Q1 = np.percentile(data, 25)
    Q3 = np.percentile(data, 75)
    
    # Calcular el rango intercuartil (IQR)
    IQR = Q3 - Q1
    
    # Definir los límites para detectar outliers
    lower_bound = Q1 - threshold * IQR
    upper_bound = Q3 + threshold * IQR
    
    # Reemplazar los valores fuera de los límites con NaN
    signal_clean = np.where((data < lower_bound) | (data > upper_bound), np.nan, data)
    
    # Interpolar usando CubicSpline (puedes ajustarlo a tus necesidades)
    # Asegúrate de no tener NaNs al principio o al final antes de aplicar la interpolación
    valid_data = ~np.isnan(signal_clean)
    x_valid = np.where(valid_data)[0]
    y_valid = signal_clean[valid_data]
    
    if len(x_valid) > 1:  # Verifica que haya suficientes puntos no NaN para la interpolación
        spline = CubicSpline(x_valid, y_valid, bc_type='natural')
        signal_clean = spline(np.arange(len(signal_clean)))
    else:
        # Si no hay suficientes puntos para hacer una interpolación spline, rellenar con valores extremos o la mediana
        median_value = np.nanmedian(signal_clean)
        signal_clean = np.nan_to_num(signal_clean, nan=median_value)

    # Reemplazar NaN por un valor de la mediana (opcional)
    signal_clean = np.nan_to_num(signal_clean, nan=np.nanmedian(signal_clean))
    
    return signal_clean



def verificar_nan(signal, mensaje="Aguante Central"):
    if np.any(np.isnan(signal)):
        print(f"Advertencia: NaN detectado {mensaje}")
    if np.any(np.isinf(signal)):
        print(f"Advertencia: Inf detectado {mensaje}")

def limpiar_datos(Archivo):
    """
    Limpia y filtra las señales EEG y de audio.

    Parámetros:
    - datos: Diccionario o DataFrame con las señales EEG.
    - markers: Diccionario o DataFrame con los marcadores de tiempo.
    - audio: Diccionario o DataFrame con las señales de audio.
    - channels: Lista con los nombres de los canales EEG.

    Devuelve:
    - amp_audio: Señal de audio procesada y remuestreada.
    - matriz_señales_eeg: Lista de señales EEG procesadas.
    """
    Tiempo = Archivo.iloc[:,0]
    Tiempo = Tiempo - Tiempo[0]
    fs=int(len(Tiempo[Tiempo <= 1]))
    Datos = Archivo.iloc[:,1]
    señal = butter_lowpass_filter(Datos, 45, fs, order = 3)
    señal = butter_highpass_filter(señal, 0.5, fs, order = 3)
    señal = remove_outliers(señal)
    señal = señal / max(abs(señal))
    
    return señal, fs
    
def order(Numero_Sujeto):
    file_path = f'./Sujetos/Sujeto_{Numero_Sujeto}/Info.csv'
    orden_audios= []
    with open(file_path, 'r') as file:
        for _, line in enumerate(file):
            if "Messi_Es_Un_Perro_" in line:
                orden = int(line.split(".")[0].split("_")[-1])
                orden_audios.append(orden)
    return orden_audios

def obtener_lags(fs_eeg=250, max_lag_s= 1):
    max_lag = int(fs_eeg * max_lag_s)

    lags = np.arange(-max_lag, max_lag + 1)
    return lags

def CrossCorr(canal, envolvente, lags= obtener_lags()):
    'correlaciona el array de la señal medida en el canal_i con la envolvente ya resampleada y filtrada'
    correlacion=correlate(canal, envolvente, mode='full')
    mid_point = len(correlacion) // 2
    max_lag= max(lags)
    cross_corr = correlacion[mid_point - max_lag:mid_point + max_lag + 1]
    return cross_corr

def importar_archivos(nombre): 
    df = pd.read_csv(str(f'{nombre}'), delimiter =",")
    return df

def cross_corr_sujeto(Numero_Sujeto: int):
    Canales=[1,2,3,4,7,8]
    Info = importar_archivos(f'./Sujetos/Sujeto_{Numero_Sujeto}/Info.csv')
    Modos = [Info["Modos_Shuffled"][0], Info["Modos_Shuffled"][1]]
    df_audio=pd.DataFrame()
    df_juego=pd.DataFrame()
    for modo in Modos:
        for i in tqdm(Canales):
            Corr_Canal=[]
            for j in range(10):
                Orden = order(Numero_Sujeto)
                Archivo = importar_archivos(f'./Sujetos/Sujeto_{Numero_Sujeto}/medicion1_{modo}_{j}_ExG.csv')
                Audio = importar_archivos(f'./Audios_Digitalizados/Audio_Messi_{int(Orden[j])}.csv')
                _Audio_Filt, fs_audio = limpiar_datos(Audio)
                df_auxiliar = pd.DataFrame(columns=["Tiempo", "Audio"])
                df_auxiliar["Tiempo"] = Archivo["TimeStamp"]
                df_auxiliar["Audio"] = Archivo[f"ch{i}"]
                Señal_Filt, fs_eeg = limpiar_datos(df_auxiliar)
                Audio_Resampleado=resample_signal(Audio["Amplitud"], fs_audio, fs_eeg)
                Envolvente_Audio=obtener_envolvente(Audio_Resampleado, fs_eeg)
                Envolvente_Audio=Envolvente_Audio/max(Envolvente_Audio)
                Corr_Canal.append(CrossCorr(Señal_Filt, Envolvente_Audio)/max(correlate(Envolvente_Audio, Envolvente_Audio, mode='full')))
            Corr=np.array(Corr_Canal)
            Corr_Promedio = np.mean(Corr, axis=0)
            if modo == "audio":
                df_audio[f"CorrCanal_{i}"] = Corr_Promedio
            else:
                df_juego[f"CorrCanal_{i}"] = Corr_Promedio
    diccionario_df = {
    "lags" : obtener_lags(),
    "audio": df_audio,
    "juego": df_juego
    }
    return diccionario_df

def main():
    Canales=[1,2,3,4,7,8]
    Labels_Canales = ["FP1", "FP2", "T3", "T4", "C3", "C4"]
    N = 18 #cantidad de sujetos
    audio_total=[]
    juego_total=[]
    M=1
    sujetos= [f"Sujeto_{i}" for i in range(1,M)]
    
    for k in tqdm(range(1,M+1)):
        #tarda aprox 2min por sujeto
        print(f"Sujeto_{k}")
        diccionario=cross_corr_sujeto(k)
        lags=diccionario["lags"]  
        audio=diccionario["audio"]
        juego=diccionario["juego"]
        audio_total.append(audio)
        juego_total.append(juego)
    # Configuración del layout de subplots
    
    audio_total=np.array(audio_total)
    juego_total=np.array(juego_total)
    # print(np.size(juego_total))
    audio_promedio=sum(audio_total)/len(audio_total)
    juego_promedio=sum(juego_total)/len(juego_total)
    fig, axes = plt.subplots(nrows=6, ncols=2, figsize=(10, 13), sharex= True)  # 6 filas, 2 columnas
    modo = audio_promedio.T, juego_promedio.T
    axes[0, 0].set_title("Audio")
    axes[0, 1].set_title("Juego")
    # Crear una lista para almacenar los datos de cada subplot
    dataframes = []
    # Generar datos de ejemplo y graficar en cada subplot
    for i in range(6):  # Filas
        for j in range(2):  # Columnas
            mask = (lags >= 0)
            ax = axes[i, j]  # Acceder al subplot correspondiente
            x = lags/250
            y = modo[j][i]  # Ejemplo de datos para graficar
            # y= y/max(y)
            # Agregar línea punteada en el máximo
            max_idx = np.argmax(y[mask])  # Índice del máximo en y
            max_x = x[mask][max_idx]  # Valor correspondiente en x
            ax.axvline(max_x, linestyle='--', color='red', alpha=0.7, label=f'Máximo: {max_x:.2f}s')
            ax.plot(x, y)
            if j == 0:  # Etiquetar las filas solo en la primera columna
                ax.set_ylabel(Labels_Canales[i])
            ax.grid(True)
            # Guardar los datos x e y en un DataFrame
            df = pd.DataFrame({'x': x, 'y': y})
            df['Canal'] = Labels_Canales[i]
            df['Tipo'] = 'Audio' if j == 0 else 'Juego'
            dataframes.append(df)

    # Combinar todos los DataFrames en uno solo
    result_df = pd.concat(dataframes, ignore_index=True)
    result_df.to_csv(f"./Correlaciones/{M}_Sujetos_Derivada.csv", index=False)

    # Ajustar el layout para evitar solapamientos
    plt.tight_layout()
    plt.show()    
       
if __name__ == '__main__':
    main()
