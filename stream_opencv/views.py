from django.views.decorators import gzip
from django.http import StreamingHttpResponse
from django.shortcuts import render
import uuid
import cv2
import threading


fourcc = cv2.VideoWriter_fourcc('M', 'P', 'E', 'G')
out = cv2.VideoWriter(f'{uuid.uuid1()}-output.mp4', fourcc, 25.0, (640, 480) )


class VideoCamera:
    def __init__(self):
        self.video = cv2.VideoCapture(0)
        (self.grabbed, self.frame) = self.video.read()
        threading.Thread(target=self.update, args=()).start()

    def __del__(self):
        self.video.release()
    
    def get_frame(self):
        image = self.frame
        _, jpeg = cv2.imencode('.jpg', image)
        return jpeg.tobytes()

    def get_save_frame(self):
        return self.frame

    def update(self):
        while True:
            (self.grabbed, self.frame) = self.video.read()
            out.write(self.frame)


def gen(camera):
    while True:
        frame = camera.get_frame()
        # outwrite(camera.get_save_frame()).
        yield(b'--frame\r\n'
              b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')


@gzip.gzip_page
def livefe(request):
    try:
        cam = VideoCamera()

        return StreamingHttpResponse(gen(cam), content_type="multipart/x-mixed-replace;boundary=frame")
    except:
        pass
