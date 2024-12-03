import cv2
import numpy as np

# Replace with your IP Webcam URL
url = "http://192.168.0.176:8080/video"

# Screen size of your laptop (in pixels)
# Update with your actual screen resolution
screen_width, screen_height = 1920, 1080

# Open video stream
cap = cv2.VideoCapture(url)

if not cap.isOpened():
    print("Error: Could not connect to the camera.")
    exit()

# Initialize a canvas for drawing
canvas = np.zeros((screen_height, screen_width, 3), dtype=np.uint8)

# Define HSV color range for detecting the pen tip (adjust as necessary)
# Adjust Saturation (S) and Value (V) for your use case
lower_color = np.array([100, 120, 70])
upper_color = np.array([130, 255, 255])

previous_position = None  # To track the pen's position

while True:
    ret, frame = cap.read()
    if not ret:
        print("Error: Failed to capture frame.")
        break

    # Resize frame for consistency
    frame_height, frame_width = frame.shape[:2]

    # Convert to HSV color space
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Mask for the pen tip
    mask = cv2.inRange(hsv, lower_color, upper_color)

    # Find contours of the pen tip
    contours, _ = cv2.findContours(
        mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if contours:
        # Find the largest contour (assuming it's the pen tip)
        largest_contour = max(contours, key=cv2.contourArea)

        # Get the position of the pen tip
        (x, y), radius = cv2.minEnclosingCircle(largest_contour)
        x, y = int(x), int(y)

        # Scale the position to the laptop screen
        scaled_x = int((x / frame_width) * screen_width)
        scaled_y = int((y / frame_height) * screen_height)

        # Draw on the canvas
        if previous_position:
            cv2.line(canvas, previous_position,
                     (scaled_x, scaled_y), (0, 255, 0), 5)
        previous_position = (scaled_x, scaled_y)

        # Visualize detection on the frame
        cv2.circle(frame, (x, y), int(radius), (0, 255, 0), 2)
        cv2.putText(frame, f"Tip: ({scaled_x}, {scaled_y})", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    else:
        previous_position = None

    # Show the frame and canvas
    cv2.imshow("Camera Feed", frame)
    cv2.imshow("Drawing Canvas", canvas)

    if cv2.waitKey(1) & 0xFF == ord('q'):  # Press 'q' to exit
        break

cap.release()
cv2.destroyAllWindows()
