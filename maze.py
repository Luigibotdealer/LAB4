from pico_car import Motor, Ultrasonic, Servo, I2cLcd, Line_tracking
import time
from machine import I2C, Pin
#from pico_i2c_lcd import I2cLcd

# Define ultrasonic sensors
ultra_front = Ultrasonic(trigger_pin=3, echo_pin=2)
ultra_left = Ultrasonic(trigger_pin=5, echo_pin=4)
ultra_right = Ultrasonic(trigger_pin=7, echo_pin=6)

motor = Motor()

DEFAULT_I2C_ADDR = 0x27
i2c = I2C(0,sda=Pin(20),scl=Pin(21),freq=400000)
lcd = I2cLcd(i2c, DEFAULT_I2C_ADDR, 2, 16)

# Movement speeds
speed_high = 100
speed_low = 50

# Path storage for optimization
path = []

# Function to determine movement based on left-hand-on-wall algorithm
def navigate_maze():
    while True:
        dist_front = ultra_front.get_distance()
        dist_left = ultra_left.get_distance()
        dist_right = ultra_right.get_distance()

        lcd.clear()
        lcd.putstr(f"L:{dist_left} F:{dist_front} R:{dist_right}")

        if dist_left > 15:  # Prefer left turn if possible
            motor.move(1, "turn_left", speed_low)
            path.append("L")
            motor.move(1, "forward", speed_low)
            lcd_print = "forward_low"
            time.sleep(0.5)
        elif dist_right > 15:  # If right is clear, turn right
            if path[-1] == "B":
                motor.move(1, "forward", speed_high)
                path.append("S")
            else:
                motor.move(1, "turn_right", speed_low)
                path.append("R")
                motor.move(1, "forward", speed_low)
                lcd_print = "forward_low"
                time.sleep(0.5)            
        elif dist_front < 15 and dist_right < 15 and dist_left < 15:  # Dead-end, turn around
            motor.move(1, "backward", speed_high)
            time.sleep(1)
            motor.move(1, "right", speed_high)  # 180-degree turn
            path.append("B")
        else:
            motor.move(1, "forward", speed_high)

        
        time.sleep(0.5)

# Function to optimize path
def optimize_path(path):
    """ Continuously optimizes the path array until all 'B' terms are removed. """
    optimizations = {
        ('L', 'B', 'L'): 'S',
        ('L', 'B', 'R'): 'B',
        ('L', 'B', 'S'): 'R',
        ('R', 'B', 'L'): 'B',
        ('S', 'B', 'L'): 'R',
        ('S', 'B', 'S'): 'B',
    }

    while 'B' in path:  # Keep optimizing until no 'B' is left
        for i in range(len(path) - 2):  # Look at triplets
            triplet = (path[i], path[i+1], path[i+2])
            if triplet in optimizations:
                # Replace the triplet with its optimized version
                path[i:i+3] = [optimizations[triplet]]
                break  # Restart loop to apply new changes
        
    return path


# Start navigation
navigate_maze()