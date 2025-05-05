from sense_emu import SenseHat
import time
import socket

sense = SenseHat()

#Połączenie UDP
server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server.bind(("100.103.1.17", 5000)) # RP1 obiera tu dane

client_address = ("100.103.1.192", 5001) # adrdes RP2

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
    # TRYB NASLUCHIWANIA - czekaj na odbior pilki od RP2
    if xball == -1:
        try:
            server.settimeout(0.1)
            data, _ = server.recvfrom(1024)
            xball, yball, dx, dy = map(int, data.decode().split(','))
            
            if dx == 1:
                xball = 0 # RP2 odbiera z lewej
            elif dx == -1:
                xball = 7 # odbiera z prawej
        except socket.timeout:
            return -1, -1, dx, dy
            
    else: # TRYB ROZGRYWKI - pilka znajduje sie na polu
        if 0 <= xball <= 7 and 0 <= yball <= 7:
            if xball == 7 and dx == 1: # Koniec pola - pora wyslac pilke
                data = f"{0},{yball},{dx},{dy}".encode()
                server.sendto(data, client_address)
                sense.set_pixel(xball, yball, black)
                xball = -1 # Pilka znika - przelaczenie w tryb nasluchu
            else:
                # Ruch pilki
                sense.set_pixel(xball, yball, black)
                xball += dx
                yball += dy
                
                # Odbicie od gory/dolu
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
                    else:	# KONIEC GRY
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
    xpaddle, ypaddle = 0, 3
    draw_paddle(xpaddle, ypaddle)

    xball, yball = 7, 4
    dx, dy = -1, 0  # kierunek

    return xpaddle, ypaddle, xball, yball, dx, dy

# Główna pętla
xpaddle, ypaddle, xball, yball, dx, dy = new_game()

while True:
    for event in sense.stick.get_events():
        xpaddle, ypaddle = move_paddle(event, xpaddle, ypaddle)
        
    xball, yball, dx, dy = bounce_ball(xball, yball, dx, dy, xpaddle, ypaddle)
    time.sleep(0.3)