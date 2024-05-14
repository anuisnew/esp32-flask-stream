from flask import Flask, Response, request, render_template_string
import cv2
import numpy as np

app = Flask(__name__)

video_writer = None

@app.route('/upload', methods=['POST'])
def upload():
    global video_writer
    if video_writer is None:
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        video_writer = cv2.VideoWriter('received_stream.avi', fourcc, 20.0, (640, 480))

    file = request.files['video']
    nparr = np.frombuffer(file.read(), np.uint8)
    frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    video_writer.write(frame)
    return 'Received', 200

def generate_frames():
    cap = cv2.VideoCapture('received_stream.avi')
    while True:
        success, frame = cap.read()
        if not success:
            break
        else:
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/')
def index():
    return render_template_string('''
    <html>
        <head>
            <title>ESP32-CAM Stream</title>
        </head>
        <body>
            <h1>ESP32-CAM Stream</h1>
            <img src="{{ url_for('video_feed') }}">
        </body>
    </html>''')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
