import time
from machine import Pin,I2C
from pico_car import Motor, Ultrasonic, Servo, I2cLcd, Line_tracking


DEFAULT_I2C_ADDR = 0x27
i2c = I2C(0,sda=Pin(20),scl=Pin(21),freq=400000)
lcd = I2cLcd(i2c, DEFAULT_I2C_ADDR, 2, 16)

line_tracking = Line_tracking()
motor = Motor()
speed = 50
speed_low = 30
info = ''
lcd_print = ''
lcd_print2 = ''
mark = 1
lt = []

def line_track():
    global info, lcd_print, lcd_print2, mark, lt
    line_track_value = line_tracking.get_ir_value()
    if lt != line_track_value:
        print(line_track_value)
        lt = line_track_value
    if line_track_value == [0, 1, 0]:
        
        motor.move(1, "forward", speed)
        lcd_print = "forward"
        lcd_print2 = "[0, 1, 0]"
        mark = 1
    elif line_track_value == [1, 1, 0]:
        '''
        添加后退指令
        if mark != 2:
        motor.move(1, "backward", 30)
        time.sleep(0.03)
        需要测试
        '''
    
        motor.move(1, "left_forward", speed_low)
        lcd_print = "left_forward"
        lcd_print2 = "[1, 1, 0]"
        mark = 2
    elif line_track_value == [1, 0, 0]:
        motor.move(1, "left_forward", speed)
        lcd_print = "left"
        lcd_print2 = "[1, 0, 0]"
        mark = 3
        
        
    elif line_track_value == [0, 1, 1]:
        motor.move(1, "right_forward", speed_low)
        lcd_print = "right_forward"
        lcd_print2 = "[0, 1, 1]"
        mark = 4
    elif line_track_value == [0, 0, 1]:
        motor.move(1, "right_forward", speed)
        lcd_print = "right"
        lcd_print2 = "[0, 0, 1]"
        mark = 5
    
      
    elif line_track_value == [1, 1, 1]:
        motor.move(0, "forward", 30)
        lcd_print = "Can Not judge"
        lcd_print2 = "[1, 1, 1]"
        
        
    elif line_track_value == [0, 0, 0] and info != lcd_print:
        motor.move(0, "turn_right", speed)
        lcd_print = "Not detected"
        lcd_print2 = "[0, 0, 0]"
        '''
        if lcd_print == "left_forward":
            motor.move(1, "right_forward", speed)
        elif lcd_print == "right_forward":
            motor.move(1, "left_forward", speed)
        elif lcd_print == "left":        
            motor.move(1, "right", speed)
        elif lcd_print == "right":        
            motor.move(1, "left", speed)
        time.sleep(0.5)
        motor.move(0, "forward", speed)
     #   pass
     '''
    if info != lcd_print:
        lcd.clear()
        lcd.putstr("Line Tracking")
        lcd.putstr("\n")
        lcd.putstr(lcd_print)
        info = lcd_print
        #print("??????")
        #lcd.putstr("\n")
        #lcd.putstr(lcd_print2)

def line_track_stop():
    motor.move(0, "forward", speed)
    lcd.clear()
    
def test():
    value = get_ir_value()
    print("left: {}, middle: {}, right: {}" .format(value[0], value[1], value[2]))

if   __name__ == '__main__':
    try:
        while True:
            line_track()
            #time.sleep_ms(300)
    except KeyboardInterrupt:
        line_track_stop()