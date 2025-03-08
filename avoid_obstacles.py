from pico_car import Motor, Ultrasonic, Servo, I2cLcd, Line_tracking
import time
from machine import I2C, Pin
#from pico_i2c_lcd import I2cLcd

servo = Servo()
motor = Motor()
ultra = Ultrasonic(3,2)
line_tracking = Line_tracking()

DEFAULT_I2C_ADDR = 0x27
i2c = I2C(0,sda=Pin(20),scl=Pin(21),freq=400000)
lcd = I2cLcd(i2c, DEFAULT_I2C_ADDR, 2, 16)

Ultra_Max_Angle = 90
Ultra_Min_Angle = -90
Angle_Step = 10
ultra_angle = 0
ultra_step = -Angle_Step
scan_data = []
info = ""

speed_high = 50
speed_low = 30

# Get distance in a certain direction.
def get_ultra_distance(angle):
    servo.set_angle(7, angle) # set pin7 servo angle.
    time.sleep(0.05)
    distance = ultra.get_distance()
    return distance


# Get the ultrasonic detection distance of the corresponding angle.
def get_distance_angle():
    global ultra_angle, ultra_step
    ultra_angle += ultra_step
    if ultra_angle >= Ultra_Max_Angle:
        ultra_angle = Ultra_Max_Angle
        ultra_step = - Angle_Step
    elif ultra_angle <= Ultra_Min_Angle:
        ultra_angle = Ultra_Min_Angle
        ultra_step = Angle_Step
    distance = get_ultra_distance(ultra_angle)
    return[ultra_angle, distance]

# Set the ultrasonic scan angle range.
def set_detection_range(angle):
    global Ultra_Max_Angle, Ultra_Min_Angle
    Ultra_Max_Angle = int(angle/2)
    Ultra_Min_Angle =  -Ultra_Max_Angle
    
# 
def avoid_obstacles():
    global scan_data, info
    angle, distance = get_distance_angle()
    if distance >=50:
        
        motor.move(1, "forward", speed_high)
        lcd_print = "forward_high"
    elif distance >= 25 and distance < 50:
        motor.move(1, "forward", speed_low)
        lcd_print = "forward_low"
    elif distance >= 10 and distance < 25:
        if angle > 15:
            motor.move(1, "left", speed_low)
            lcd_print = "left"
            time.sleep(0.5)
            motor.motor_stop()
            time.sleep(0.1)
        elif angle < -10:
            motor.move(1, "right", speed_low)
            lcd_print = "right"
            time.sleep(0.5)
            motor.motor_stop()
            time.sleep(0.1)
            
        else:
            motor.move(1, "left", speed_low)
            lcd_print = "left"
            time.sleep(0.5)
            motor.motor_stop()
            time.sleep(0.1)
            
    elif distance < 10:
            motor.move(1, "backward", speed_low)
            time.sleep(0.5)
            lcd_print = "backward"
            motor.motor_stop()
            time.sleep(0.1)
    
    if info != lcd_print:
        lcd.clear()
        lcd.putstr("Avoid Obstacles")
        lcd.putstr("\n")
        lcd.putstr(lcd_print)
        # After avoiding obstacles, the car stop for 1.5s.
        if lcd_print !="forward_high" and lcd_print != "forward_low": 
            time.sleep(1.5)
        info = lcd_print
     
def test():
    set_detection_range(40) # set ultrasonic detection angle range.
    avoid_obstacles()
    
if __name__ == "__main__":
    
    try:
        while True:
            test()
            #time.sleep(0.05)
    except KeyboardInterrupt:
        motor.motor_stop()
        lcd.clear()
    