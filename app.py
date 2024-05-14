from flask import Flask, Response, request, render_template_string
import cv2
import numpy as np

app = Flask(__name__)

# Global variable to store the latest frame
latest_frame = None

@app.route('/upload', methods=['POST'])
def upload():
    global latest_frame
    try:
        nparr = np.frombuffer(request.data, np.uint8)
        latest_frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        return 'Received', 200
    except Exception as e:
        print(f"Error: {e}")
        return 'Bad Request', 400

def generate_frames():
    global latest_frame
    while True:
        if latest_frame is not None:
            ret, buffer = cv2.imencode('.jpg', latest_frame)
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
