import time
from machine import Pin, I2C
from pico_car import Motor, I2cLcd, Line_tracking, IR

DEFAULT_I2C_ADDR = 0x27
i2c = I2C(0, sda=Pin(20), scl=Pin(21), freq=400000)
lcd = I2cLcd(i2c, DEFAULT_I2C_ADDR, 2, 16)

line_tracking = Line_tracking()
motor = Motor()
speed = 40
speed_low = 35
info = ''
lcd_print = ''
lt = []
turn_time = 0.4

PIN = 22;
irm = IR(PIN)

# Infrared reception interval time.
IR_delay_time = 0.11

mark = 1
mark_ir = ''

# Path storage for optimization
path = []

j = 0

def IR_control():
    global info, lcd_print, mark_ir, mark, lt
    IR_re = irm.scan()
    if IR_re != mark_ir:
        print(IR_re)
        mark_ir = IR_re
    if(IR_re[0]==False):
        #print("_____________")
        mark = 1
    if(IR_re[0]==True and IR_re[1]!=None):
        # remove the first possibly wrong command.
        # 删除第一个可能错误的指令
        if IR_re[1] is not None and mark != -999:
            mark = -999
            
        elif IR_re[1] == "*":
            try:
                while True:
                    navigate_maze()
                    IR_re = irm.scan()
                    if IR_re[1] == "ok":
                        break
            except KeyboardInterrupt:
                line_track_stop()
        elif IR_re[1] == "#":
            optimize_path(path)
            try:
                while True:
                    solve_maze()
                    IR_re = irm.scan()
                    if  IR_re[1] == "ok":
                        break
            except KeyboardInterrupt:
                line_track_stop()
    else:
        line_track_stop()

def navigate_maze():
    global info, lcd_print, lt
    line_track_value = line_tracking.get_ir_value()
    
    if lt != line_track_value:
        print(line_track_value)
        lt = line_track_value
    
    if line_track_value[:2] == [1, 0]:
        motor.move(1, "turn_right", speed_low)
        lcd_print = "Turning right"
        path.append("R")
        start_time = time.time()
        #Minimum of 0.2 of turn
        time.sleep(0.2)
        while time.time() - start_time < 3:
            if line_tracking.get_ir_value() != line_track_value:
                break  # Stop early if the condition changes

    elif line_track_value[:2] == [0, 1]:
        motor.move(1, "turn_left", speed_low)
        lcd_print = "left left sensor"
        path.append("L")
        start_time = time.time()
        #Minimum of 0.2 of turn
        time.sleep(0.2)
        while time.time() - start_time < 3:
            if line_tracking.get_ir_value() != line_track_value:
                break  # Stop early if the condition changes

    elif line_track_value[:2] == [0, 0]:
        motor.move(1, "turn_left", speed_low)
        lcd_print = "left both 0"
        path.append("L")
        start_time = time.time()
        #Min 0.1
        time.sleep(0.1)
        while time.time() - start_time < 3:
            if line_tracking.get_ir_value() != line_track_value:
                break  # Stop early if the condition changes

    elif line_track_value[:2] == [1, 1]:  # Only check the first two values
    
        if line_track_value[-3:] == [1, 1, 0]:  # Follow the line
            motor.move(1, "forward", speed)
            lcd_print = "forward"
            path.append("F")

        elif line_track_value[-3:] == [0, 1, 1]:  # Slight left correction
            motor.move(1, "left_forward", speed)
            lcd_print = "left_forward"

        elif line_track_value[-3:] == [1, 1, 0]:  # Slight right correction
            motor.move(1, "right_forward", speed)
            lcd_print = "right forward"

        elif line_track_value[-3:] == [0, 0, 1]:  # Forward
            motor.move(1, "forward", speed)
            lcd_print = "forward"
            path.append("F")
            start_time = time.time()
            while time.time() - start_time < 4:
                if line_tracking.get_ir_value() != line_track_value:
                    break  # Stop early if the condition changes

        elif line_track_value[-3:] == [1, 0, 0]:  # Forward
            motor.move(1, "forward", speed)
            lcd_print = "forward"
            path.append("F")
            start_time = time.time()
            while time.time() - start_time < 4:
                if line_tracking.get_ir_value() != line_track_value:
                    break  # Stop early if the condition changes

        elif line_track_value[-3:] == [0, 0, 0]:  # Junction detected
            motor.move(1, "forward", speed_low)
            lcd_print = "forward"
            path.append("F")
            start_time = time.time()
            while time.time() - start_time < 4:
                if line_tracking.get_ir_value() != line_track_value:
                    break  # Stop early if the condition changes

        elif line_track_value[-3:] == [1, 1, 1]:  # No line detected, dead end
            motor.move(1, "turn_left", speed_low)
            lcd_print = "Dead end"
            path.append("L")
            start_time = time.time()
            #
            while time.time() - start_time < 3:
                if line_tracking.get_ir_value() != line_track_value:
                    break  # Stop early if the condition changes
                
        if info != lcd_print:
            lcd.clear()
            lcd.putstr("Line Tracking\n" + lcd_print)
            info = lcd_print

def solve_maze():

    global info, lcd_print, lt, j
    line_track_value = line_tracking.get_ir_value()
    
    if lt != line_track_value:
        print(line_track_value)
        lt = line_track_value
    
    if line_track_value == [1, 0, 1]:  # Follow the line
        motor.move(1, "forward", speed)
        lcd_print = "forward"
    
    elif line_track_value == [0, 1, 1]:  # Slight left correction
        motor.move(1, "left_forward", speed)
        lcd_print = "left"
    
    elif line_track_value == [1, 1, 0]:  # Slight right correction
        motor.move(1, "right_forward", speed)
        lcd_print = "right"
    
    else:
        if j < len(path):
            if path[j] == "S":
                motor.move(1, "forward", speed)
                lcd_print = "forward"
                start_time = time.time()
                while time.time() - start_time < 0.5:
                    if line_tracking.get_ir_value() != line_track_value:
                        break  # Stop early if the condition changes
            elif path[j]  == "L":
                motor.move(1, "turn_left", speed_low)
                lcd_print = "left turn"
                start_time = time.time()
                while time.time() - start_time < 0.5:
                    if line_tracking.get_ir_value() != line_track_value:
                        break  # Stop early if the condition changes
            elif path[j]  == "R":
                motor.move(1, "turn_right", speed_low)
                lcd_print = "right turn"
                start_time = time.time()
                while time.time() - start_time < 0.5:
                    if line_tracking.get_ir_value() != line_track_value:
                        break  # Stop early if the condition changes
            j += 1
    
    if info != lcd_print:
        lcd.clear()
        lcd.putstr("Solving Maze\n" + lcd_print)
        info = lcd_print

def line_track_stop():
    motor.move(0, "stop", 0)
    lcd.clear()

def optimize_path(path): # Function to optimize path
    """ Continuously optimizes the path array until all 'B' terms are removed. """
    optimizations = {
        ('L', 'B', 'L'): 'S',
        ('L', 'B', 'R'): 'B',
        ('L', 'B', 'S'): 'R',
        ('R', 'B', 'L'): 'B',
        ('S', 'B', 'L'): 'R',
        ('S', 'B', 'S'): 'B',
    }

    optimized = True
    while optimized:
        optimized = False
        for i in range(len(path) - 2):
            triplet = (path[i], path[i+1], path[i+2])
            if triplet in optimizations:
                path[i:i+3] = [optimizations[triplet]]
                optimized = True  # Re-run optimization if changes occur
                break
        
    return path

if __name__ == '__main__':
    try:
        while True:
            IR_control()
            time.sleep(IR_delay_time)

    except KeyboardInterrupt:
        line_track_stop()

