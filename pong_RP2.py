from sense_emu import SenseHat
import time
import socket

# Polaczenie UDP
client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
client.bind(("100.103.1.192", 5001)) # RP2 odbiera tu dane

server_address = ("100.103.1.17", 5000) # adres RP1

sense = SenseHat()

# Kolory globalnie
green = (0, 255, 0)
black = (0, 0, 0)
ball_color = (255, 255, 255)

def draw_paddle(xpaddle, ypaddle):
    sense.set_pixel(xpaddle, ypaddle, green)
    sense.set_pixel(xpaddle, ypaddle + 1, green)

def clear_paddle(xpaddle, ypaddle):
    sense.set_pixel(xpaddle, ypaddle, black)
    sense.set_pixel(xpaddle, ypaddle + 1, black)
    
def move_paddle(event, xpaddle, ypaddle):
    if event.action in ("pressed", "held"):
        clear_paddle(xpaddle, ypaddle)
        
        if event.direction == "up" and ypaddle > 0:
            ypaddle -=1
        elif event.direction == "down" and ypaddle < 6:
            ypaddle += 1
            
    draw_paddle(xpaddle, ypaddle)
        
    return xpaddle, ypaddle

def bounce_ball(xball, yball, dx, dy, xpaddle, ypaddle):
    # Zgaszenie starej pozycji piłki
    if 0 <= xball < 8 and 0 <= yball < 8:
        sense.set_pixel(xball, yball, black)

    # Przesunięcie piłki
    xball += dx
    yball += dy

    # Odbicie od góry / dołu
    if yball < 0:
        yball = 0
        dy = -dy
    elif yball > 7:
        yball = 7
        dy = -dy

    # Sprawdzenie odbicia od paletki
    if xball == xpaddle + 1:  # Bo paddle na lewo
        if yball == ypaddle or yball == ypaddle + 1:
            dx = -dx
            dy = 1 if yball == ypaddle + 1 else -1
        else:
            # KONIEC GRY
            sense.set_pixel(xball, yball, ball_color)
            time.sleep(0.3)
            sense.set_pixel(xball, yball, black)
            sense.set_pixel(xball + dx, yball + dy, ball_color)
            time.sleep(0.3)
            sense.clear()
            sense.show_message("GAME OVER", text_colour=(255, 0, 0))
            exit()

    # Odbicie od prawej/lewej krawędzi
    elif xball > 7:
        xball = 7
        dx = -dx
    elif xball == 0 and dx == -1:  
        #xball = 0
        #dx = -dx
        data = f"{0},{yball},{dx},{dy}".encode()
        server.sendto(data, server_address)
        xball = -1

        

    # Rysowanie piłki w nowym miejscu
    if 0 <= xball < 8 and 0 <= yball< 8:
        sense.set_pixel(xball, yball, ball_color)

    return xball, yball, dx, dy

def new_game():
    sense.clear()
    xpaddle, ypaddle = 7, 3
    draw_paddle(xpaddle, ypaddle)

    return xpaddle, ypaddle

# Główna pętla
xpaddle, ypaddle = new_game()

while True:
    while True:
    # Odbierz dane od RP1 (jeśli są)
        try:
            data, _ = client.recvfrom(1024)
            xball, yball, dx, dy = map(int, data.decode().split(','))
            xball = 0  # Piłka pojawia się po lewej stronie
            dx = 1     # Kierunek w prawo
        except BlockingIOError:
            pass  # Brak danych

        for event in sense.stick.get_events():
            xpaddle, ypaddle = move_paddle(event, xpaddle, ypaddle)
        
        xball, yball, dx, dy = bounce_ball(xball, yball, dx, dy, xpaddle, ypaddle)
        time.sleep(0.3)