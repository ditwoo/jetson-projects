import Jetson.GPIO as GPIO
import time
import pygame



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

    def left_rotate(self):
        self.state[0] -= 1
        self.state[1] += 1
        self.update()

    def right(self, val=1):
        self.state[0] += val
        self.update()

    def right_rotate(self):
        self.state[0] += 1
        self.state[1] -= 1
        self.update()

    def stop(self):
        self.state = [0, 0]
        self.forward(0, 0)


def main():
    print("Jetson info:", GPIO.JETSON_INFO)
    print("    version:", GPIO.VERSION)

    GPIO.setwarnings(False)
    # set pin numbers to the board's
    GPIO.setmode(GPIO.BOARD)

    pygame.init()
    j = pygame.joystick.Joystick(0)
    j.init()

    try:
        with Motor(ena=37, in1=35, in2=33) as rmoto, Motor(ena=36, in1=38, in2=40) as lmoto:
            tank = Tank(lmoto, rmoto)
            print("Tank is ready for the action!")
            
            while True:
                events = pygame.event.get()
                for event in events:
                    if event.type == pygame.JOYAXISMOTION:
                        print(event.dict, event.joy, event.axis, event.value)
                    elif event.type == pygame.JOYBALLMOTION:
                        print(event.dict, event.joy, event.ball, event.rel)
                    elif event.type == pygame.JOYBUTTONDOWN:
                        print(event.dict, event.joy, event.button, 'pressed')
                    elif event.type == pygame.JOYBUTTONUP:
                        print(event.dict, event.joy, event.button, 'released')
                    elif event.type == pygame.JOYHATMOTION:
                        print(event.dict, event.joy, event.hat, event.value)

            # while True:
            #     key = keyboard.read_key()
            #     if key == "w" or keyboard.is_pressed("w"):
            #         tank.forward()

            #     if key == "s" or keyboard.is_pressed("s"):
            #         tank.backward()
                
            #     if key == "a" or keyboard.is_pressed("a"):
            #         tank.left()

            #     if key == "d" or keyboard.is_pressed("d"):
            #         tank.right()

            #     if key == "space" or keyboard.is_pressed("space"):
            #         tank.stop()

    except KeyboardInterrupt:
        print("\nShut down!")
        j.quit()


    GPIO.cleanup()

if __name__ == "__main__":
    main()
