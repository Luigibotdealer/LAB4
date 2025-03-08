from pico_car import Motor,IR, I2cLcd, Servo
from machine import I2C, Pin
import time
import avoid_obstacles
import line_tracking
import keep_distance

servo = Servo()
motor = Motor()
PIN = 22;
irm = IR(PIN)


DEFAULT_I2C_ADDR = 0x27
i2c = I2C(0,sda=Pin(20),scl=Pin(21),freq=400000)
lcd = I2cLcd(i2c, DEFAULT_I2C_ADDR, 2, 16)

info = ''
lcd_print = ''
lcd_print2 = ''
speed = 40
# Infrared reception interval time.
IR_delay_time = 0.11

mark = 1
mark_ir = ''


def IR_control():
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
            
        elif IR_re[1] == "*":
            try:
                while True:
                    avoid_obstacles.test()
                    IR_re = irm.scan()
                    if IR_re[1] == "ok":
                        servo.set_angle(7, 0)
                        break
            except KeyboardInterrupt:
                motor.motor_stop()
        elif IR_re[1] == "0":
            try:
                while True:
                    line_tracking.line_track()
                    IR_re = irm.scan()
                    if  IR_re[1] == "ok":
                        break
            except KeyboardInterrupt:
                motor.motor_stop()
        elif IR_re[1] == "#":
            try:
                servo.set_angle(7, 0)
                
                while True:
                    keep_distance.keep_distance()
                    IR_re = irm.scan()
                    if  IR_re[1] == "ok":
                        break
            except KeyboardInterrupt:
                motor.motor_stop()
        else:
            if IR_re[1] == "up":
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
            
            if info != lcd_print:
                lcd.clear()
                lcd.putstr(lcd_print)
                info = lcd_print
    else:
        motor.motor_stop()
        
if __name__ =="__main__":
    try:
        while True:
            IR_control()
            time.sleep(IR_delay_time)
    except KeyboardInterrupt:
        motor.motor_stop()