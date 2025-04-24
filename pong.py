from sense_emu import SenseHat
import time

def move_up(x, y):
    sense.set_pixel(0, y, black)
    sense.set_pixel(0, y+1, black) #Zgaszenie paletki
    y = y-1 # Zmiana pozycji
    y = max(0, y) # Ograniczenie 1-6
    sense.set_pixel(0, y, player)
    sense.set_pixel(0, y+1, player) # Zapalenie paletki
    
    return y
    
def move_down(x, y):
    sense.set_pixel(0, y, black)
    sense.set_pixel(0, y+1, black)
    y = y+1
    y = min(6, y)
    sense.set_pixel(0, y, player)
    sense.set_pixel(0, y+1, player)
    
    return y
    
sense = SenseHat()
player = (0, 255, 0)
black  = (0, 0, 0)

y = 3
y = max(0, min(6, y))
sense.set_pixel(0, y, player)
sense.set_pixel(0, y+1, player)


while True:
    for event in sense.stick.get_events():
        print(event.direction, event.action)
        
        if event.action in ("pressed", "held"):
            if event.direction == "up":
                y = move_up(0, y)
            elif event.direction == "down":
                y = move_down(0, y)
                
                
        

        
