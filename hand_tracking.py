import cv2
import mediapipe as mp
import socket


# Send commands to Webots on this computer
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
webots_address = ("127.0.0.1", 5005)

# Initialize MediaPipe hand tracking
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    model_complexity=0,
    min_detection_confidence=0.6,
    min_tracking_confidence=0.6
)

# Open the default webcam
camera = cv2.VideoCapture(0)

if not camera.isOpened():
    print("Could not access the webcam.")
    raise SystemExit

print("GestureBot hand tracking started.")
print("Press Q to quit.")

#previous_x = None
#previous_y = None

#candidate_direction = "WAITING"
#stable_direction = "WAITING"
#candidate_count = 0

#STABLE_FRAMES = 3
while True:
    success, frame = camera.read()

    if not success:
        print("Could not read from webcam.")
        break

    # Mirror the image for a natural webcam view
    frame = cv2.flip(frame, 1)

    # MediaPipe expects RGB images
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Detect the hand
    results = hands.process(rgb_frame)

    direction = "STOP"
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:

            # Draw all 21 hand landmarks
            mp_drawing.draw_landmarks(
                frame,
                hand_landmarks,
                mp_hands.HAND_CONNECTIONS
            )

            # Landmark 8 is the index fingertip
            fingertip = hand_landmarks.landmark[8]

            height, width, _ = frame.shape

            x = int(fingertip.x * width)
            y = int(fingertip.y * height)

            """
            current_x = x
            current_y = y
            if previous_x is not None and previous_y is not None:
                
                dx = current_x - previous_x
                dy = current_y - previous_y
                print(f"dx: {dx}, dy: {dy}")
                THRESHOLD = 2

                if abs(dx) <= THRESHOLD and abs(dy) <= THRESHOLD:
                    direction = "STATIONARY"
                elif abs(dx) > abs(dy):
                    direction = "RIGHT" if dx > THRESHOLD else "LEFT"
                else:
                    direction = "DOWN" if dy > THRESHOLD else "UP"

                if direction == candidate_direction:
                    candidate_count += 1
                else:
                    candidate_direction = direction
                    candidate_count = 1

                if candidate_count >= STABLE_FRAMES:
                    stable_direction = candidate_direction

                cv2.putText(
                    frame,
                    f"Direction: {stable_direction}",
                    (20, 80),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.8,
                    (0, 255, 0),
                    2
                )    
            """
            # Select a command from the fingertip's screen position
            if x < width * 0.35:
                direction = "LEFT"
            elif x > width * 0.65:
                direction = "RIGHT"
            elif y < height * 0.35:
                direction = "UP"
            elif y > height * 0.65:
                direction = "DOWN"
            else:
                direction = "STOP" 

            cv2.putText(
                frame,
                f"Direction: {direction}",
                (20, 80),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0, 255, 0),
                2
            ) 
            #previous_x = current_x
            #previous_y = current_y
            # Highlight the fingertip
            cv2.circle(
                frame,
                (x, y),
                12,
                (0, 255, 0),
                -1
            )

            cv2.putText(
                frame,
                f"Index: ({x}, {y})",
                (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 255, 0),
                2
            )
    sock.sendto(direction.encode("utf-8"), webots_address)
    cv2.imshow("GestureBot - Hand Tracking", frame)

    # Press Q to exit
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

camera.release()
sock.close()
hands.close()
cv2.destroyAllWindows()