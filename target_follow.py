from pico_car import Motor, Ultrasonic, Servo, I2cLcd, Line_tracking
import time
from machine import I2C, Pin

servo = Servo()
motor = Motor()
ultra = Ultrasonic(3,2)

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
Distance_Reference = 25
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
    global Ultra_Max_Angle, Ultra_Min_Angle, ultra_angle, ultra_step
    if angle > 180:
        angle = 180
    elif angle < 0:
        angle = 0
    Ultra_Max_Angle = int(angle/2)
    Ultra_Min_Angle =  -Ultra_Max_Angle
    # Let the ultrasound start to detect from the beginning/tail.
    # A set of data obtained.
    if ultra_step < 0:
        ultra_step = Angle_Step
        ultra_angle = Ultra_Min_Angle
    elif ultra_step > 0:
        ultra_step = -Angle_Step
        ultra_angle = Ultra_Max_Angle
    servo.set_angle(7, ultra_angle)
    
# Set the critical value to judge whether the distance of ultrasonic detection reaches the set value.
def get_threshold_status(distance):
    if distance > Distance_Reference:
        return 1
    elif distance <= Distance_Reference and distance > 10:
        return 0
    else:
        return 2
def ultra_scan():
    global scan_data
    angle, distance = get_distance_angle()
    status = get_threshold_status(distance)
    scan_data.append(status)
    if angle == Ultra_Max_Angle or angle == Ultra_Min_Angle:
        if ultra_step < 0: # Data detected from the tail needs to be reversed.
            scan_data.reverse()
        print(scan_data)
        temporary_data = scan_data.copy()
        scan_data = []
        return temporary_data
    else:
        return status
        
def target_follow():
    ultra_data = ultra_scan()
    if isinstance(ultra_data, list):
        ultra_data = [str(i) for i in ultra_data]
        ultra_data = ''.join(ultra_data)
        targets = ultra_data.split('1')
        length_value = []
        for target in targets:
            length_value.append(len(target))
        #if max(length_value) == 0:
        if max(length_value) >= len(ultra_data)-2:
            motor.motor_stop()
        else:
            i = length_value.index(max(length_value))
            position = ultra_data.index(targets[i])
            position +=(len(targets[i]) -1) / 2
            reference = len(ultra_data) / 3
            if position < reference:
                motor.move(1, 'left_forward', speed_low)
            elif position > reference*2:
                motor.move(1, 'right_forward', speed_low)
            else:
                motor.move(1, 'forward', speed_low)
            
            
if __name__ == "__main__":
    try:
        set_detection_range(90)
        while True:
            target_follow()
    except KeyboardInterrupt:
        motor.motor_stop()
            
    
    
    