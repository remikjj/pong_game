#pong_RP2.py
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
    # TRYB NASLUCHIWANIA - czekaj na odbior pilki od RP1
    if xball == -1:
        try:
            client.settimeout(0.1)
            data, _ = client.recvfrom(1024)
            xball, yball, dx, dy = map(int, data.decode().split(','))
            
            if dx == 1:
                xball = 0	# RP2 odebira z lewej
            elif dx == -1:
                xball = 7	# RP1 odbiera z prawej
        except socket.timeout:
            return -1, -1, dx, dy
    
    else: # TRYB ROZGRYWKI - pika znajduje sie na polu
        if 0 <= xball <=7 and 0 <= yball <=7:
            if xball == 0 and dx == -1: # Wyslanie pilki
                data = f"{7},{yball},{dx},{dy}".encode()
                client.sendto(data, server_address)
                sense.set_pixel(xball, yball, black) # Zgaszenie starej pozycji pilki
                xball = -1 # Pilka znika - przelaczenie w tryb nasluchiwania 
            else:
                 # Ruch pilki
                sense.set_pixel(xball, yball, black) # Zgaszenie starej pozycji pilki
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
                if xball == xpaddle - 1:  # Bo paddle na prawo
                    if xball == xpaddle - 1 and ypaddle <= yball <= ypaddle + 1:
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
                    
    # Rysowanie piłki w nowym miejscu
    if 0 <= xball < 8 and 0 <= yball< 8:
        sense.set_pixel(xball, yball, ball_color)

    return xball, yball, dx, dy

def new_game():
    sense.clear()
    xpaddle, ypaddle = 7, 3
    draw_paddle(xpaddle, ypaddle)

    xball, yball = -1, -1
    dx, dy = 1,0
    
    return xpaddle, ypaddle, xball, yball, dx, dy

# Główna pętla
xpaddle, ypaddle, xball, yball, dx, dy = new_game()

while True:
    for event in sense.stick.get_events():
        xpaddle, ypaddle = move_paddle(event, xpaddle, ypaddle)
        
    xball, yball, dx, dy = bounce_ball(xball, yball, dx, dy, xpaddle, ypaddle)
    time.sleep(0.3)