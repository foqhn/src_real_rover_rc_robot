# display the camera feed on the web page
from flask import Flask, request, jsonify, render_template, Response
import numpy as np
import cv2


app = Flask(__name__)
cam = cv2.VideoCapture(0)

def gen_frames():
    while True:
        success, frame = cam.read()
        if not success:
            break
        else:
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            
            


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')



if __name__ == '__main__':
    try:
        app.run(debug=True,host='raspy1.local', port=8080)
    except KeyboardInterrupt:
        cam.release()
        exit()
    

