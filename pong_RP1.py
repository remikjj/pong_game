from sense_emu import SenseHat
import time

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

def bounce_ball(ball_x, ball_y, dx, dy, xpaddle, ypaddle):
    # Zgaszenie starej pozycji piłki
    if 0 <= ball_x < 8 and 0 <= ball_y < 8:
        sense.set_pixel(ball_x, ball_y, black)

    # Przesunięcie piłki
    ball_x += dx
    ball_y += dy

    # Odbicie od góry / dołu
    if ball_y < 0:
        ball_y = 0
        dy = -dy
    elif ball_y > 7:
        ball_y = 7
        dy = -dy

    # Sprawdzenie odbicia od paletki
    if ball_x == xpaddle + 1:  # Bo paddle na lewo
        if ball_y == ypaddle or ball_y == ypaddle + 1:
            dx = -dx
            dy = 1 if ball_y == ypaddle + 1 else -1
        else:
            # KONIEC GRY
            sense.clear()
            sense.show_message("GAME OVER", text_colour=(255, 0, 0))
            exit()

    # Odbicie od prawej krawędzi
    elif ball_x > 7:
        ball_x = 7
        dx = -dx
    elif ball_x < 0:
        ball_x = 0
        dx = -dx

    # Rysowanie piłki w nowym miejscu
    if 0 <= ball_x < 8 and 0 <= ball_y < 8:
        sense.set_pixel(ball_x, ball_y, ball_color)

    return ball_x, ball_y, dx, dy

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