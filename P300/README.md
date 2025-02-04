# P300

Están acá todos los códigos relacionados al experimento P300 que replicamos con el EEG del laboratorio. Muchos de los códigos los sacamos del github de mentalab, pero igualmente nos pareció que, por completitud, correspondía agregarlos acá también.

## P300.py

Este es el código que sirve para realizar la medición. Toma el control de la pantalla y muestra, en una proporción de 4 a 1, rectángulos azules y círculos rojos, replicando el experimento 'oddball'. Todo esto mientras mide la señal del EEG (que antes de ejecutar el código debería estar conectado y ajustado.)

## Analisis-P300(-8Canales).py

Estos códigos son para el analisis de los resultados medidos con el código anterior. Ambos aislarán la señal de los canales correspondientes en el caso de los círculos o los rectángulos y mostrarán en pantalla los resultados, donde se podrá ver claramente el pico P3 o P300. La única diferencia entre los códigos es la cantidad de canales que analizan. (4 u 8).
