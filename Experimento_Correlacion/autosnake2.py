import pygame
import random
import time
import argparse
import numpy as np
import explorepy as exp
import tkinter as tk
import os
import pandas as pd
# Configuración del juego Snake
root = tk.Tk()
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
root.destroy()
snake_speed = 140
window_x = screen_width
window_y = screen_height
black = pygame.Color(0, 0, 0)
white = pygame.Color(255, 255, 255)
red = pygame.Color(255, 0, 0)
green = pygame.Color(0, 255, 0)

# Variable para almacenar el puntaje más alto
top_score = 0

# Variable para cambiar el modo de juego
auto_play = True  # Cambiar a False para el modo jugador

# Función para mostrar el puntaje y el top_score
def show_score(game_window, score, top_score, color, font, size):
    score_font = pygame.font.SysFont(font, size)
    score_surface = score_font.render(f'Score: {score}', True, color)
    top_score_surface = score_font.render(f'Top Score: {top_score}', True, color)
    game_window.blit(score_surface, (10, 10))  # Score a la izquierda
    game_window.blit(top_score_surface, (window_x - top_score_surface.get_width() - 10, 10))  # Top score a la derecha

# Función para reiniciar el juego tras una pausa al perder
def reset_game():
    # Estado inicial de la serpiente y fruta
    snake_position = [400, 50]
    i=0
    j=0
    snake_body = [[400-i*10, 50] for i in range(1, 40)]
    fruit_position = [random.randrange(1, (window_x // 10)) * 10, random.randrange(1, (window_y // 10)) * 10]
    direction = 'RIGHT'
    score = 0
    return snake_position, snake_body, fruit_position, direction, score

def show_question(screen, question, font_size=50):
    screen.fill(black)
    font = pygame.font.SysFont('times new roman', font_size)
    question_surface = font.render(question, True, white)
    screen.blit(question_surface, (window_x // 2 - question_surface.get_width() // 2, window_y // 2))
    pygame.display.update()
    time.sleep(3)  # Mostrar la pregunta durante 10 segundos

# Función de IA para mover la serpiente hacia la fruta
def ai_move(snake_position, fruit_position, direction):
    if snake_position[0] < fruit_position[0] and direction != 'LEFT':
        return 'RIGHT'
    elif snake_position[0] > fruit_position[0] and direction != 'RIGHT':
        return 'LEFT'
    elif snake_position[1] < fruit_position[1] and direction != 'UP':
        return 'DOWN'
    elif snake_position[1] > fruit_position[1] and direction != 'DOWN':
        return 'UP'
    return direction

def preguntas_juego():
    lista= ['¿Cuántas frutas comió la serpiente en la primer "vida"?',
             '¿Cuál fue la cantidad máxima de frutas que la serpiente llegó a comer?',
             '¿Cuántas frutas comió la serpiente en la última "vida"?',
             '¿Cuántas vidas se llegaron a jugar antes de que termine el audio?',
             '¿Cuántas veces la serpiente comió más de 6 frutas?',
             '¿Cuántas veces la serpiente comió menos de 6 frutas?',
             '¿Cuántas veces la serpiente comió más de 3 frutas?',
             '¿Cuántas veces la serpiente comió menos de 3 frutas?']
    return lista

def pause_screen(screen, font_size=50):
    screen.fill(black)  # Llena la pantalla de negro
    font = pygame.font.SysFont('times new roman', font_size)
    message = "Presione SPACE para continuar"
    message_surface = font.render(message, True, white)
    screen.blit(message_surface, (window_x // 2 - message_surface.get_width() // 2, window_y // 2))
    pygame.display.update()  # Actualiza la pantalla

    paused = True
    while paused:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:  # Detecta si se presionó Space
                paused = False  # Sale del bucle cuando se presiona Space

def preguntas_audio():
    lista= ['¿Dijo la palabra "Messi" en este fragmento?',
            '¿Dijo la palabra "perro" en este fragmento?',
            '¿Dijo la palabra "animal" en este fragmento?',
            '¿Dijo la palabra "pelota" en este fragmento?',
            '¿Dijo la palabra "juguete" en este fragmento?',
            '¿Dijo la palabra "esponja" en este fragmento?',
            '¿Dijo la palabra "normal" en este fragmento?',
            '¿Dijo la palabra "marciano" en este fragmento?']
    return lista

def get_user_input(screen, prompt, font_size=50):
    screen.fill(black)
    font = pygame.font.SysFont('times new roman', font_size)
    prompt_surface = font.render(prompt, True, white)
    screen.blit(prompt_surface, (window_x // 2 - prompt_surface.get_width() // 2, window_y // 2 - 50))
    pygame.display.update()

    user_input = ""
    input_active = True
    while input_active:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:  # Confirmar respuesta con Enter
                    input_active = False
                    time.sleep(2)
                elif event.key == pygame.K_BACKSPACE:  # Borrar el último caracter
                    user_input = user_input[:-1]
                else:  # Agregar el carácter escrito al input
                    user_input += event.unicode

        # Mostrar el texto ingresado por el usuario
        screen.fill(black)
        screen.blit(prompt_surface, (window_x // 2 - prompt_surface.get_width() // 2, window_y // 2 - 50))
        input_surface = font.render(user_input, True, white)
        screen.blit(input_surface, (window_x // 2 - input_surface.get_width() // 2, window_y // 2 + 50))
        pygame.display.update()

    return user_input  # Retorna la respuesta ingresada por el usuario


# Función principal que combina Snake y grabación EEG
def main():
    # Inicializar el parser para argumentos de dispositivo y archivo de EEG
    parser = argparse.ArgumentParser(description="EEG experiment with Snake game")
    parser.add_argument("-n", "--name", dest="name", type=str, help="Name of the EEG device.")
    parser.add_argument("-f", "--filename", dest="filename", type=str, help="Record file name")
    parser.add_argument("-s", "--sujeto", dest="sujeto", type=str, help="sujeto")

    args = parser.parse_args()

    # Conectar al dispositivo EEG
    device = exp.Explore()
    device.connect(device_name=args.name)
    global top_score, auto_play  # Indicamos que usaremos la variable global top_score y auto_play
    # Audios = ["./Audios/Messi_Es_Un_Perro_1.mp3", "./Audios/Messi_Es_Un_Perro_2.mp3"]
    Audios = './Audios_Messi'
    Modos = ['audio', 'juego']
    Audios_Shuffled = np.random.permutation(os.listdir(Audios))
    Modos_Shuffled = np.random.permutation(Modos)

    # Crear un DataFrame con los datos
    

    respuestas_A=[]
    respuestas_J=[]
    for modo in Modos_Shuffled:
        It = 0
        for audio in Audios_Shuffled:
            # Inicializar el audio
            pygame.mixer.init()
            pygame.mixer.music.load(f'{Audios}/{audio}')


            # Iniciar la grabación de EEG
            filename2 = f'./Sujetos/Sujeto_{args.sujeto}/{args.filename}_{modo}_{It}'
            device.record_data(file_name=filename2, file_type="csv")
            
            # Inicializar el juego
            pygame.init()
            pygame.display.set_caption('Neuro Snake')
            game_window = pygame.display.set_mode((window_x, window_y))
            if It == 0:
                show_question(game_window, f"Presta atención al {modo}")
                pause_screen(game_window, font_size=50)
            It = It+1
            fps = pygame.time.Clock()

            # Inicializar el estado del juego
            snake_position, snake_body, fruit_position, direction, score = reset_game()
            fruit_spawn = True
            change_to = direction

            # Iniciar la música y el temporizador
            pygame.mixer.music.play()
            start_time = time.time()

            # Bucle principal del juego
            running = True
            skip_question = False
            mode = 'A'
            
            while running and pygame.mixer.music.get_busy() and (time.time() - start_time < 20):
                for event in pygame.event.get():
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_q:  # Cambiar entre modos de juego
                            auto_play = not auto_play
                        if event.key == pygame.K_ESCAPE:  # Detener el juego
                            running = False
                            return
                        if event.key == pygame.K_DELETE:  # Detener el juego
                            running = False
                            skip_question = True
                        if not auto_play:
                            if event.key == pygame.K_w: change_to = 'UP'
                            elif event.key == pygame.K_s: change_to = 'DOWN'
                            elif event.key == pygame.K_a: change_to = 'LEFT'
                            elif event.key == pygame.K_d: change_to = 'RIGHT'

                # Modo de juego: IA o jugador
                if auto_play:
                    direction = ai_move(snake_position, fruit_position, direction)
                else:
                    # Evitar que la serpiente se desplace en dirección opuesta
                    if change_to == 'UP' and direction != 'DOWN': direction = 'UP'
                    if change_to == 'DOWN' and direction != 'UP': direction = 'DOWN'
                    if change_to == 'LEFT' and direction != 'RIGHT': direction = 'LEFT'
                    if change_to == 'RIGHT' and direction != 'LEFT': direction = 'RIGHT'

                # Mover la serpiente
                if direction == 'UP': snake_position[1] -= 10
                elif direction == 'DOWN': snake_position[1] += 10
                elif direction == 'LEFT': snake_position[0] -= 10
                elif direction == 'RIGHT': snake_position[0] += 10

                # Mecanismo de crecimiento
                snake_body.insert(0, list(snake_position))
                if snake_position == fruit_position:
                    score += 10
                    fruit_spawn = False
                else:
                    snake_body.pop()

                if not fruit_spawn:
                    fruit_position = [random.randrange(1, (window_x // 10)) * 10, random.randrange(1, (window_y // 10)) * 10]
                fruit_spawn = True

                game_window.fill(black)
                for pos in snake_body:
                    pygame.draw.rect(game_window, green, pygame.Rect(pos[0], pos[1], 10, 10))
                pygame.draw.rect(game_window, white, pygame.Rect(fruit_position[0], fruit_position[1], 10, 10))

                # Condiciones de fin de juego
                if snake_position[0] < 0 or snake_position[0] >= window_x or snake_position[1] < 0 or snake_position[1] >= window_y:
                    top_score = max(top_score, score)  # Actualiza el top_score si el score actual es mayor
                    # show_score(game_window, score, top_score, red, 'times new roman', 50)
                    pygame.display.update()
                    time.sleep(1)
                    snake_position, snake_body, fruit_position, direction, score = reset_game()
                    continue

                for block in snake_body[1:]:
                    if snake_position == block:
                        top_score = max(top_score, score)  # Actualiza el top_score si el score actual es mayor
                        # show_score(game_window, score, top_score, red, 'times new roman', 50)
                        pygame.display.update()
                        time.sleep(1)
                        snake_position, snake_body, fruit_position, direction, score = reset_game()
                        continue

                # show_score(game_window, score, top_score, white, 'times new roman', 20)
                pygame.display.update()
                fps.tick(snake_speed)
            pygame.mixer.quit()
            # Detener la grabación
            device.stop_recording()
            if modo == 'audio' and not skip_question:
                Preguntas = preguntas_audio()
            else:
                Preguntas = preguntas_juego()

            Pregunta = random.choice(Preguntas)
            respuesta = get_user_input(game_window, Pregunta)
            print(f"Ruesta del usuario: {respuesta}")
            if modo == 'audio':
                respuestas_A.append(respuesta)
            else:
                respuestas_J.append(respuesta)
    max_len = max(len(Audios_Shuffled), len(Modos_Shuffled))
    Audios_Shuffled = list(Audios_Shuffled) + [None] * (max_len - len(Audios_Shuffled))
    Modos_Shuffled = list(Modos_Shuffled) + [None] * (max_len - len(Modos_Shuffled))
    df = pd.DataFrame({"Audios_Shuffled": Audios_Shuffled, "Modos_Shuffled": Modos_Shuffled, "Rta. Audio": respuestas_A, "Rta. Juego": respuestas_J})
    # Guardar en un archivo CSV
    df.to_csv(f"./Sujetos/Sujeto_{args.sujeto}/Info.csv", index=False)
    pygame.quit()
    #Desconectar el dispositivo
    device.disconnect()
if __name__ == '__main__':
    main()
    
# python autosnake2.py -n Explore_8575 -f medicion1 -s n

