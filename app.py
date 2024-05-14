from flask import Flask, Response, request, render_template_string
import cv2
import numpy as np

app = Flask(__name__)

@app.route('/upload', methods=['POST'])
def upload():
    try:
        nparr = np.frombuffer(request.data, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        cv2.imwrite('received_image.jpg', img)  # Save the image for verification
        return 'Received', 200
    except Exception as e:
        print(f"Error: {e}")
        return 'Bad Request', 400

def generate_frames():
    while True:
        # Read the saved image
        img = cv2.imread('received_image.jpg')
        if img is not None:
            ret, buffer = cv2.imencode('.jpg', img)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        else:
            continue

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/')
def index():
    return render_template_string('''
    <html>
        <head>
            <title>MACHINESense Labs</title>
        </head>
        <body>
            <h1>ESP32-CAM LiveStream</h1>
            <img src="{{ url_for('video_feed') }}">
        </body>
    </html>''')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
