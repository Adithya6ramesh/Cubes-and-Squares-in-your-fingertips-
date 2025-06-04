from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import cv2
import mediapipe as mp
import math
import time
import base64
import numpy as np
from threading import Lock
import json

app = Flask(__name__)
CORS(app)

# Global variables for hand detection
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7)
mp_drawing = mp.solutions.drawing_utils

# Thread-safe variables
calculation_lock = Lock()
current_data = {
    'entered_number': '',
    'square': 0,
    'cube': 0,
    'current_fingers': 0,
    'message': ''
}

last_detection_time = time.time()
delay_seconds = 2

def calculate_distance(point1, point2):
    return math.sqrt((point1.x - point2.x) ** 2 + (point1.y - point2.y) ** 2)

def is_c_gesture(landmarks):
    thumb_tip = landmarks[4]
    thumb_ip = landmarks[3]
    thumb_mcp = landmarks[2]
    
    index_tip = landmarks[8]
    index_dip = landmarks[7]
    index_pip = landmarks[6]

    # Check thumb curve and proximity to index finger
    thumb_curved = thumb_tip.x < thumb_ip.x < thumb_mcp.x
    thumb_near_index = calculate_distance(thumb_tip, index_tip) < 0.1

    # Check index finger curved shape
    index_curved = index_tip.y > index_dip.y > index_pip.y

    # Check for a fist shape
    if thumb_curved and thumb_near_index and index_curved:
        return True
    return False

def process_hand_frame(frame):
    global last_detection_time, current_data
    
    total_fingers = 0
    message = ''
    
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(frame_rgb)

    if results.multi_hand_landmarks:
        current_time = time.time()
        
        for hand_landmarks in results.multi_hand_landmarks:
            # Draw landmarks on frame
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            if is_c_gesture(hand_landmarks.landmark):
                with calculation_lock:
                    current_data['entered_number'] = ""
                    current_data['square'] = 0
                    current_data['cube'] = 0
                    current_data['message'] = 'Number Cleared'
                continue

            # Extract the required landmarks for finger detection
            landmarks = hand_landmarks.landmark
            
            # Calculate finger states
            finger_states = []
            for i in [8, 12, 16, 20]:  # Index, Middle, Ring, Pinky
                if landmarks[i].y < landmarks[i - 2].y:
                    finger_states.append(1)
                else:
                    finger_states.append(0)
            
            # Thumb detection
            thumb_is_up = 0
            thumb_tip = landmarks[4]
            thumb_mcp = landmarks[2]
            index_finger_mcp = landmarks[5]

            thumb_is_below_mcp = thumb_tip.y > thumb_mcp.y
            thumb_is_near_index = calculate_distance(thumb_tip, index_finger_mcp) < 0.05

            if not thumb_is_below_mcp and not thumb_is_near_index:
                thumb_is_up = 1
            
            finger_states.append(thumb_is_up)
            fingers_up = sum(finger_states)

            if fingers_up > 0:
                total_fingers += fingers_up
            else:
                total_fingers = 0

        # Check if the delay period has passed
        if current_time - last_detection_time > delay_seconds:
            if total_fingers > 0:
                with calculation_lock:
                    current_data['entered_number'] += str(total_fingers)
                    
                    try:
                        num = int(current_data['entered_number'])
                        current_data['square'] = num ** 2
                        current_data['cube'] = num ** 3
                        current_data['message'] = f'Added {total_fingers}'
                    except ValueError:
                        pass
                
                last_detection_time = current_time

    with calculation_lock:
        current_data['current_fingers'] = total_fingers
    
    return frame

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/process_frame', methods=['POST'])
def process_frame():
    try:
        data = request.get_json()
        image_data = data['image'].split(',')[1]  # Remove data:image/jpeg;base64,
        
        # Decode base64 image
        nparr = np.frombuffer(base64.b64decode(image_data), np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        # Process the frame
        processed_frame = process_hand_frame(frame)
        
        # Encode processed frame back to base64
        _, buffer = cv2.imencode('.jpg', processed_frame)
        processed_image = base64.b64encode(buffer).decode('utf-8')
        
        with calculation_lock:
            response_data = current_data.copy()
        
        response_data['processed_image'] = f"data:image/jpeg;base64,{processed_image}"
        
        return jsonify(response_data)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/calculate', methods=['POST'])
def calculate():
    try:
        data = request.get_json()
        number = int(data['number'])
        
        with calculation_lock:
            current_data['entered_number'] = str(number)
            current_data['square'] = number ** 2
            current_data['cube'] = number ** 3
            current_data['message'] = 'Manual calculation'
        
        return jsonify({
            'number': number,
            'square': number ** 2,
            'cube': number ** 3
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/clear', methods=['POST'])
def clear():
    with calculation_lock:
        current_data['entered_number'] = ''
        current_data['square'] = 0
        current_data['cube'] = 0
        current_data['current_fingers'] = 0
        current_data['message'] = 'Cleared manually'
    
    return jsonify({'message': 'Cleared successfully'})

@app.route('/api/status', methods=['GET'])
def get_status():
    with calculation_lock:
        return jsonify(current_data.copy())

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True) 