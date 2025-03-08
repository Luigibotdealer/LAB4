from pico_car import Motor,IR, I2cLcd
from machine import I2C, Pin
import time

motor = Motor()
PIN = 22;
irm = IR(PIN)


DEFAULT_I2C_ADDR = 0x27
i2c = I2C(0,sda=Pin(20),scl=Pin(21),freq=400000)
lcd = I2cLcd(i2c, DEFAULT_I2C_ADDR, 2, 16)

info = ''
lcd_print = ''
speed = 50
# Infrared reception interval time.
IR_delay_time = 0.11
mark = 1
mark_ir = ''

def IR_move():
    global info, lcd_print, mark_ir, mark
    
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
        if IR_re[0] != None and mark!= -999:
            mark = -999
            
        elif IR_re[1] == "up":
            motor.move(1, "forward", speed)
            lcd_print = "Forward"
        elif IR_re[1] == "down":
            motor.move(1, "backward", speed)
            lcd_print = "Backward"
        elif IR_re[1] == "left":
            motor.move(1, "left", speed)
            lcd_print = "Left"
        elif IR_re[1] == "right":
            motor.move(1, "right", speed)
            lcd_print = "Right"
        elif IR_re[1] == "1":
            motor.move(1, "left_forward", speed)
            lcd_print = "Left Forward"
        elif IR_re[1] == "3":
            motor.move(1, "right_forward", speed)
            lcd_print = "Right Forward"
        elif IR_re[1] == "7":
            motor.move(1, "left_backward", speed)
            lcd_print = "Left Backward"
        elif IR_re[1] == "9":
            motor.move(1, "right_backward", speed)
            lcd_print = "Right Backward"
        elif IR_re[1] == "4":
            motor.move(1, "turn_left", speed)
            lcd_print = "Turn Left"
        elif IR_re[1] == "6":
            motor.move(1, "turn_right", speed)
            lcd_print = "Turn Right"
        else:
            pass
        
    else:
        motor.motor_stop()
    if info != lcd_print:
        lcd.clear()
        lcd.putstr(lcd_print)
        info = lcd_print

if __name__ =="__main__":
    try:
        while True:
            IR_move()
            time.sleep(IR_delay_time)
    except KeyboardInterrupt:
        motor.motor_stop()
