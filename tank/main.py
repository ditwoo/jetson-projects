import Jetson.GPIO as GPIO
import time
from pyPS4Controller.controller import Controller



class Motor:
    def __init__(self, ena, in1, in2):
        self.ena = ena
        self.in1 = in1
        self.in2 = in2

    def __enter__(self):
        GPIO.setup(self.ena, GPIO.OUT, initial=GPIO.LOW)
        GPIO.setup(self.in1, GPIO.OUT, initial=GPIO.LOW)
        GPIO.setup(self.in2, GPIO.OUT, initial=GPIO.LOW)

        GPIO.output(self.ena, GPIO.HIGH)
        GPIO.output(self.in1, GPIO.LOW)
        GPIO.output(self.in2, GPIO.LOW)

        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        GPIO.output(self.ena, GPIO.LOW)
        GPIO.output(self.in1, GPIO.LOW)
        GPIO.output(self.in2, GPIO.LOW)

    def stop(self):
        GPIO.output(self.in1, GPIO.LOW)
        GPIO.output(self.in2, GPIO.LOW)
    
    def forward(self):
        GPIO.output(self.in1, GPIO.LOW)
        GPIO.output(self.in2, GPIO.HIGH)

    def backward(self):
        GPIO.output(self.in1, GPIO.HIGH)
        GPIO.output(self.in2, GPIO.LOW)


class Tank:
    def __init__(self, left_motor, right_motor):
        self.l = left_motor
        self.r = right_motor
        self.state = [0, 0]
    
    def update(self):
        l, r = self.state

        if l > 0:
            self.l.forward()
        elif l < 0:
            self.l.backward()
        else:
            self.l.stop()
        
        if r > 0:
            self.r.forward()
        elif r < 0:
            self.r.backward()
        else:
            self.r.stop()

    def forward(self, val1=1, val2=None):
        if val2 is None:
            val2 = val1
        self.state[0] += val1
        self.state[1] += val2
        self.update()
    
    def backward(self):
        self.forward(-1)
    
    def left(self, val=1):
        self.state[1] += val
        self.update()

    def left_rotate(self, val=1):
        self.state[0] -= val
        self.state[1] += val
        self.update()

    def right(self, val=1):
        self.state[0] += val
        self.update()

    def right_rotate(self, val=1):
        self.state[0] += val
        self.state[1] -= val
        self.update()

    def stop(self):
        self.state = [0, 0]
        self.forward(0, 0)


class TankController(Controller):

    def __init__(self, tank, **kwargs):
        Controller.__init__(self, **kwargs)
        self.tank = tank
        self.inv = 1  # action inversion

    def on_up_arrow_press(self):
        self.tank.forward(self.inv)

    def on_up_down_arrow_release(self):
        self.tank.stop()

    def on_down_arrow_press(self):
        self.tank.forward(-self.inv)

    def on_left_arrow_press(self):
        self.tank.left_rotate(self.inv)

    def on_left_right_arrow_release(self):
        self.tank.stop()

    def on_right_arrow_press(self):
        self.tank.right_rotate(self.inv)
    
    def on_L1_press(self):
        self.tank.left_rotate(self.inv)

    def on_L1_release(self):
        self.tank.stop()

    def on_R1_press(self):
        self.tank.right_rotate(self.inv)

    def on_R1_release(self):
        self.tank.stop()

    def on_circle_press(self):
        self.inv = -1
    
    def on_circle_release(self):
        self.inv = 1
    
    def on_x_press(self):
        self.tank.stop()

    def on_triangle_press(self):
        self.tank.stop()

    def on_square_press(self):
        self.tank.stop()

    # -------------------------------------

    def on_R3_up(self, value):
        self.tank.left(self.inv)
    
    def on_R3_down(self, value):
        self.tank.left(self.inv)

    def on_R3_x_at_rest(self):
        self.tank.stop()

    def on_R3_right(self, value):
        self.tank.right(self.inv)
    
    def on_R3_left(self, value):
        self.tank.right(self.inv)

    def on_R3_y_at_rest(self):
        self.tank.stop()

def main():
    print("Jetson info:", GPIO.JETSON_INFO)
    print("    version:", GPIO.VERSION)

    GPIO.setwarnings(False)
    # set pin numbers to the board's
    GPIO.setmode(GPIO.BOARD)

    try:
        with Motor(ena=37, in1=35, in2=33) as rmoto, Motor(ena=36, in1=38, in2=40) as lmoto:
            tank = Tank(lmoto, rmoto)
            print("Tank is ready for the action!")
            
            controller = TankController(tank=tank, interface="/dev/input/js0", connecting_using_ds4drv=False)
            controller.listen()

    except KeyboardInterrupt:
        print("\nShut down!")


    GPIO.cleanup()

if __name__ == "__main__":
    main()
