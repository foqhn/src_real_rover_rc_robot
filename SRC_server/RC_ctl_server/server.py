from flask import Flask, request, jsonify, render_template, Response
from PCA9685 import PCA9685
import numpy as np
import cv2

import time

app = Flask(__name__)
cam = cv2.VideoCapture(0)

pwm = PCA9685(0x40, debug=False)
pwm.setPWMFreq(50)


class MotorDriver():
    def __init__(self):
        self.PWMA = 0
        self.AIN1 = 3
        self.AIN2 = 4
        self.PWMB = 5
        self.BIN1 = 1
        self.BIN2 = 2

    def MotorRun(self,leftspeed,rightspeed):
        maxspeed = 90
        if leftspeed > maxspeed:
            leftspeed = maxspeed
        if leftspeed < -maxspeed:
            leftspeed = -maxspeed
        if rightspeed > maxspeed:
            rightspeed = maxspeed
        if rightspeed < -maxspeed:
            rightspeed = -maxspeed
            
        if leftspeed >= 0:
            pwm.setDutycycle(self.PWMA, leftspeed)
            pwm.setLevel(self.AIN1, 0)
            pwm.setLevel(self.AIN2, 1)
        else:
            pwm.setDutycycle(self.PWMA, abs(leftspeed))
            pwm.setLevel(self.AIN1, 1)
            pwm.setLevel(self.AIN2, 0)

        if rightspeed >= 0:
            pwm.setDutycycle(self.PWMB, rightspeed)
            pwm.setLevel(self.BIN1, 0)
            pwm.setLevel(self.BIN2, 1)
        else:
            pwm.setDutycycle(self.PWMB, abs(rightspeed))
            pwm.setLevel(self.BIN1, 1)
            pwm.setLevel(self.BIN2, 0)
            
    def MotorStop(self):
        pwm.setDutycycle(self.PWMA, 0)
        pwm.setLevel(self.AIN1, 0)
        pwm.setLevel(self.AIN2, 0)
        pwm.setDutycycle(self.PWMB, 0)
        pwm.setLevel(self.BIN1, 0)
        pwm.setLevel(self.BIN2, 0)
        

        
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
MD=MotorDriver()
L=50
R=50

# ルートページを表示
@app.route('/')
def index():
    return render_template('index.html')

# メッセージを受け取るエンドポイント
@app.route('/send_message', methods=['POST'])
def send_message():
    data = request.get_json()
    message = data.get('message', '')
    print(f"Received message: {message}")
    motor_ctl(message)
    return jsonify({"status": "success", "message": message})


@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


def motor_ctl(cmd):
    global L,R
    if cmd=='front':
        MD.MotorRun(L,R)
    elif cmd=='back':
        MD.MotorRun(-L,-R)
    elif cmd=='left':
        MD.MotorRun(-L,R)
    elif cmd=='right':
        MD.MotorRun(R,-L)
    elif cmd=='stop':
        MD.MotorStop()
    elif cmd=='vup':
        R*=1.1
        L*=1.1
    elif cmd=='vdown':
        R/=1.1
        L/=1.1
        
    else:
        print('Unknown command')

            
if __name__ == '__main__':
    
    try:
        app.run(host='raspy1.local', port=8080)
    except KeyboardInterrupt:
        cam.release()
        print('Exiting')
        exit()
        
        