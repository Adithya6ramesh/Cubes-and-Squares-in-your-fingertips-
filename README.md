# Hand Gesture Controlled Number Input and Calculation

This Python script uses OpenCV and MediaPipe to detect hand gestures from a webcam feed, allowing users to input numbers and see their squares and cubes calculated in real-time.

## Features

- **Real-time Hand Detection:** Utilizes MediaPipe Hands to detect and track hand landmarks.
- **Finger Counting:** Accurately counts the number of extended fingers on a detected hand. Special logic is included for robust thumb detection.
- **Gesture-based Number Input:**
    - Users can input digits by showing the corresponding number of fingers.
    - After a 2-second delay, the detected finger count is appended to form a multi-digit number.
    - For example, showing 2 fingers, then 5 fingers, will input the number "25".
- **Clear Gesture (right Fist):** Making a fist shape or a fist gesture clears the currently entered number and its calculated square and cube.
- **Real-time Calculations:** Displays the square and cube of the entered number.
- **Visual Feedback:**
    - Draws hand landmarks on the video feed.
    - Displays the current finger count, the entered number, its square, and its cube.
    - Shows a "Number Cleared" message upon detecting the clear gesture.

## How to Use

1.  **Prerequisites:**
    *   Python 3.x
    *   OpenCV (`cv2`)
    *   MediaPipe (`mediapipe`)
    *   NumPy (often a dependency of OpenCV and MediaPipe)

    Install the necessary libraries if you haven't already:
    ```bash
    pip install opencv-python mediapipe numpy
    ```

2.  **Run the Script:**
    Execute the `op.py` script from your terminal:
    ```bash
    python op.py
    ```

3.  **Interacting with the Application:**
    *   A window will open showing your webcam feed.
    *   **To input a digit:** Show the desired number of fingers (1-5). Hold the gesture for 2 seconds. The digit will be appended to the "Entered Number".
    *   **To input a multi-digit number:** Show fingers for the first digit, wait for it to register, then show fingers for the next digit, and so on.
    *   **To clear the entered number:** Make a "C" shape with your hand (thumb and index finger curved, meeting or close to each other, other fingers can be curled or extended) or a fist. The "Entered Number" will reset to empty.
    *   **To quit:** Press the 'q' key while the video window is active.

## Script Overview (`op.py`)

-   **Initialization:** Sets up MediaPipe Hands, OpenCV video capture, and variables for storing the entered number, calculation results, and timing for gesture input.
-   **`is_c_gesture(landmarks)` function:** Detects if the hand landmarks form a "C" or fist shape, used for clearing the input.
-   **`calculate_distance(point1, point2)` function:** A utility to calculate Euclidean distance between two landmark points.
-   **Main Loop:**
    1.  Reads frames from the webcam.
    2.  Flips the frame horizontally (for a mirror view).
    3.  Converts the frame to RGB for MediaPipe processing.
    4.  Processes the frame with MediaPipe Hands.
    5.  If hands are detected:
        *   Draws landmarks.
        *   Checks for the "C" gesture to clear input.
        *   Counts extended fingers, including specific logic for the thumb.
        *   Manages the 2-second delay for concatenating finger counts into `entered_number`.
        *   Calculates the square and cube of `entered_number` if it's a valid number.
    6.  Displays all relevant information (finger count, entered number, square, cube) on the frame.
    7.  Shows the frame in a window titled "Hand Tracking".
    8.  Exits if 'q' is pressed.
-   **Cleanup:** Releases the video capture and destroys OpenCV windows when the loop ends. 