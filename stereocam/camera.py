import cv2
import numpy as np


def gstreamer_pipeline(
    sensor_id,
    capture_width=3280,
    capture_height=2464,
    display_width=1280,
    display_height=720,
    framerate=21,
    flip_method=0,
):
    template = (
        'nvarguscamerasrc sensor-id=%d ! ' 
        'video/x-raw(memory:NVMM), '
        'width=(int)%d, height=(int)%d, '
        'format=(string)NV12, framerate=(fraction)%d/1 ! '
        'nvvidconv flip-method=%d ! '
        'video/x-raw, width=(int)%d, height=(int)%d, format=(string)BGRx ! '
        'videoconvert ! '
        'video/x-raw, format=(string)BGR ! appsink drop=1'
    )
    return template  % (sensor_id, capture_width, capture_height, framerate, flip_method, display_width, display_height)


def process_frame(img, size=None, flip=None):
    if size is not None:
        img = cv2.resize(img, size)

    if flip is not None: 
        img = cv2.flip(img, flip)

    return img
        

def show_webcam(mirror=False):
    img_h, img_w = 384, 384
    caml = cv2.VideoCapture(gstreamer_pipeline(0, img_w, img_h, img_w, img_h, framerate=10), cv2.CAP_GSTREAMER)
    camr = cv2.VideoCapture(gstreamer_pipeline(1, img_w, img_h, img_w, img_h, framerate=10), cv2.CAP_GSTREAMER)

    stereo = cv2.StereoBM_create(numDisparities=48, blockSize=11)
    stereo.setPreFilterType(1)
    stereo.setMinDisparity(0)
    stereo.setNumDisparities(48)
    stereo.setTextureThreshold(0)
    stereo.setUniquenessRatio(1)
    stereo.setSpeckleRange(2)
    stereo.setSpeckleWindowSize(2)
    
    img_stereo_rgb = np.empty((img_h, img_w, 3), dtype=np.uint8)
    while True:
        _, imgl = caml.read()
        _, imgr = camr.read()

        imgl = process_frame(imgl, size=(img_h, img_w), flip=0)
        imgr = process_frame(imgr, size=(img_h, img_w), flip=0)

        gray_l = cv2.cvtColor(imgl, cv2.COLOR_BGR2GRAY)
        gray_r = cv2.cvtColor(imgr, cv2.COLOR_BGR2GRAY)

        img_stereo_gray = stereo.compute(gray_l, gray_r)
        img_stereo_gray = cv2.dilate(img_stereo_gray, None, iterations=1)
        img_stereo_gray = (img_stereo_gray.astype(np.float16) - img_stereo_gray.min()) / (img_stereo_gray.max() - img_stereo_gray.min()) 
        img_stereo_gray = (img_stereo_gray * 255).astype(np.uint8)
        img_stereo_rgb[:, :, 0] = img_stereo_gray
        img_stereo_rgb[:, :, 1] = img_stereo_gray
        img_stereo_rgb[:, :, 2] = img_stereo_gray

        img = np.concatenate([imgl, img_stereo_rgb, imgr], axis=1)
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

