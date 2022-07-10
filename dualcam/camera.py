import cv2
import numpy as np


def gstreamer_pipeline(sensor_id, capture_width=3280, capture_height=2464, display_width=1280, display_height=720, framerate=21, flip_method=0) :   
    return ('nvarguscamerasrc sensor-id=%d ! ' 
    'video/x-raw(memory:NVMM), '
    'width=(int)%d, height=(int)%d, '
    'format=(string)NV12, framerate=(fraction)%d/1 ! '
    'nvvidconv flip-method=%d ! '
    'video/x-raw, width=(int)%d, height=(int)%d, format=(string)BGRx ! '
    'videoconvert ! '
    'video/x-raw, format=(string)BGR ! appsink'  % (sensor_id, capture_width, capture_height, framerate, flip_method, display_width, display_height))


def process_frame(img, size=(512, 512), mirror=False):
    img = cv2.resize(img, (512, 512))
    if mirror: 
        img = cv2.flip(img, 1)
    return img
        

def show_webcam(mirror=False):
    caml = cv2.VideoCapture(gstreamer_pipeline(0, 512, 512, 512, 512), cv2.CAP_GSTREAMER)
    camr = cv2.VideoCapture(gstreamer_pipeline(1, 512, 512, 512, 512), cv2.CAP_GSTREAMER)
    while True:
        _, imgl = caml.read()
        _, imgr = camr.read()
        imgl = process_frame(imgl)
        imgr = process_frame(imgr)

        img = np.concatenate([imgl, imgr], axis=1)
        cv2.imshow("shape: " + str(img.shape), img)
        if cv2.waitKey(1) == 27: 
            break  # esc to quit

    caml.release()
    camr.release()
    cv2.destroyAllWindows()
    


def main():
    show_webcam(mirror=True)


if __name__ == '__main__':
    main()

