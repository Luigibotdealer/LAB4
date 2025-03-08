import time
from machine import Pin, I2C
from pico_car import Motor, I2cLcd, Line_tracking

DEFAULT_I2C_ADDR = 0x27
i2c = I2C(0, sda=Pin(20), scl=Pin(21), freq=400000)
lcd = I2cLcd(i2c, DEFAULT_I2C_ADDR, 2, 16)

line_tracking = Line_tracking()
motor = Motor()
speed = 50
speed_low = 30
info = ''
lcd_print = ''
lt = []

# Path storage for optimization
path = []

j = 0

# Button setup (assume it's connected to GP15)
button = Pin(15, Pin.IN, Pin.PULL_UP)
mode = "navigate"  # Start in navigation mode

def navigate_maze():
    global info, lcd_print, lt

    line_track_value = line_tracking.get_ir_value()
    
    if lt != line_track_value:
        print(line_track_value)
        lt = line_track_value
    
    if line_track_value == [1, 0, 1]:  # Follow the line
        motor.move(1, "forward", speed)
        lcd_print = "[1,0,1] forward"
    
    elif line_track_value == [0, 1, 1]:  # Slight left correction
        motor.move(1, "left_forward", speed)
        lcd_print = "[0,1,1] left forward"
    
    elif line_track_value == [1, 1, 0]:  # Slight right correction
        motor.move(1, "right_forward", speed)
        lcd_print = "[1,1,0] right forward"
    
    elif line_track_value == [0, 0, 1]:  # Left bias turn
        # if path and path[-1] == "B":
        #     motor.move(1, "forward", speed)
        #     lcd_print = "forward biased [1,1,1]"
        #     path.append("S")
        #     time.sleep(0.5)
        # else:
            motor.move(1, "turn_left", speed_low)
            lcd_print = "left turn [0,0,1]"
            path.append("L")
            time.sleep(0.5)
    
    elif line_track_value == [1, 0, 0]:  # Right bias turn
        # if path and path[-1] == "B":
        #     motor.move(1, "forward", speed)
        #     lcd_print = "forward [0,1,1]"
        #     path.append("S")
        #     time.sleep(0.5)
        # else:
            motor.move(1, "turn_right", speed_low)
            lcd_print = "right turn [1,0,0]"
            path.append("R")
            time.sleep(0.5)
    
    elif line_track_value == [0, 0, 0]:  # Junction
        motor.move(1, "turn_left", speed_low)
        lcd_print = "left turn [0,0,0]"
        path.append("L")
        time.sleep(0.5)
    
    elif line_track_value == [1, 1, 1]:
        # Instead of stopping or turning, keep rolling forward slowly
        motor.move(1, "backward", speed_low)
        lcd_print = "no line going backwards [1,1,1]"
        # Omit path.append("B") so we don’t treat it as a dead end


    # Print lcd only if changed
    if info != lcd_print:
        # Print to the Thonny shell
        print("Lcd print" + lcd_print)

        # Update the LCD
        lcd.clear()
        lcd.putstr("Line Tracking\n" + lcd_print)
        info = lcd_print

    


# def solve_maze():
#     global info, lcd_print, lt, j
#     line_track_value = line_tracking.get_ir_value()
    
#     if lt != line_track_value:
#         print(line_track_value)
#         lt = line_track_value
    
#     if line_track_value == [0, 1, 0]:  # Follow the line
#         motor.move(1, "forward", speed)
#         lcd_print = "forward"
    
#     elif line_track_value == [0, 0, 1]:  # Slight left correction
#         motor.move(1, "left_forward [1,0,0]", speed)
#         lcd_print = "left"
    
#     elif line_track_value == [1, 0, 0]:  # Slight right correction
#         motor.move(1, "right_forward [0,0,1]", speed)
#         lcd_print = "right"
    
#     else:
#         # Follow instructions from path if any remain
#         if j < len(path):
#             step = path[j]
#             if step == "S":
#                 motor.move(1, "forward", speed)
#                 lcd_print = "forward"
#                 time.sleep(0.5)
#             elif step == "L":
#                 motor.move(1, "turn_left", speed_low)
#                 lcd_print = "left turn"
#                 time.sleep(0.5)
#             elif step == "R":
#                 motor.move(1, "turn_right", speed_low)
#                 lcd_print = "right turn"
#                 time.sleep(0.5)
#             j += 1



def line_track_stop():
    motor.move(0, "stop", 0)
    lcd.clear()


button_pressed_flag = False  # Global flag

def button_pressed(pin):
    global button_pressed_flag
    button_pressed_flag = True  # Just set a flag


# Attach button interrupt (rising edge detects button press)
button.irq(trigger=Pin.IRQ_RISING, handler=button_pressed)


# def optimize_path(path):
#     """Continuously optimize the path array until all 'B' terms are removed."""
#     optimizations = {
#         ('L', 'B', 'L'): 'S',
#         ('L', 'B', 'R'): 'B',
#         ('L', 'B', 'S'): 'R',
#         ('R', 'B', 'L'): 'B',
#         ('S', 'B', 'L'): 'R',
#         ('S', 'B', 'S'): 'B',
#     }
#     while 'B' in path:  # Keep optimizing until no 'B' left
#         for i in range(len(path) - 2): 
#             triplet = (path[i], path[i+1], path[i+2])
#             if triplet in optimizations:
#                 path[i:i+3] = [optimizations[triplet]]
#                 break
#     return path


if __name__ == '__main__':
    try:
        while True:
            # Continuously run the appropriate line-tracking method
            if mode == "navigate":
                navigate_maze()
            elif mode == "solve":
                solve_maze()
            
            # Check if the button was pressed to toggle modes
            if button_pressed_flag:
                button_pressed_flag = False
                line_track_stop()

                # if mode == "navigate":
                #     # 1) Remove the "Path saved!\nPress to solve" lines:
                #     # lcd.clear()
                #     # lcd.putstr("Path saved!\nPress to solve")
                    
                #     #path = optimize_path(path)
                #     mode = "solve"
                # else:
                #     # 2) Remove the "Navigating...\nPress to pause" lines if you want:
                #     # lcd.clear()
                #     # lcd.putstr("Navigating...\nPress to pause")
                    
                #     j = 0
                #     mode = "navigate"

    except KeyboardInterrupt:
        line_track_stop()

