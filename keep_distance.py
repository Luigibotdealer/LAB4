from pico_car import Motor, Ultrasonic, Servo, I2cLcd
import time
from machine import I2C, Pin

servo = Servo()
motor = Motor()
ultra = Ultrasonic(3,2)

DEFAULT_I2C_ADDR = 0x27
i2c = I2C(0,sda=Pin(20),scl=Pin(21),freq=400000)
lcd = I2cLcd(i2c, DEFAULT_I2C_ADDR, 2, 16)

lcd_print = ''
info = ''
speed_low = 40
def get_ultra_distance():
    distance = ultra.get_distance()
    return distance

def keep_distance():
    global lcd_print, info
    distance = get_ultra_distance()
    if distance > 0:
        if distance >= 20:
            motor.move(1, 'forward', speed_low)
            lcd_print = 'Forward'
        elif distance <= 10:
            motor.move(1, 'backward', speed_low)
            lcd_print = 'Backward'
        else:
            motor.motor_stop()
            lcd_print = 'Stop'
    if info != lcd_print:
        lcd.clear()
        lcd.putstr("Keep Distance")
        lcd.putstr("\n")
        lcd.putstr(str(lcd_print))
        info = lcd_print

def test():
    servo.set_angle(7, 0) # set pin7 servo angle.
    time.sleep(0.05)
    while True:
        keep_distance()
            
if __name__ == "__main__":
    try:
        test()
    except KeyboardInterrupt:
        motor.motor_stop()
            