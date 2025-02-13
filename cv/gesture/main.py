import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

base_options = python.BaseOptions(model_asset_path='cv/gesture/gesture_recognizer.task')
options = vision.GestureRecognizerOptions(base_options=base_options, num_hands=2)
recognizer = vision.GestureRecognizer.create_from_options(options)

# mp_hands = mp.solutions.hands
# mp_drawing = mp.solutions.drawing_utils
# hands = mp_hands.Hands(min_detection_confidence=0.5, min_tracking_confidence=0.5)

cap = cv2.VideoCapture(1)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # result_hands = hands.process(rgb_frame)
    # if result_hands.multi_hand_landmarks:
    #     for hand_landmarks in result_hands.multi_hand_landmarks:
    #         mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
    result_gesture = recognizer.recognize(mp_image)

    left_hand_gesture = "Unknown"
    right_hand_gesture = "Unknown"
    seen_left = False
    seen_right = False

    if result_gesture.gestures and result_gesture.handedness:
        for i in range(len(result_gesture.gestures)):
            for j in range(len(result_gesture.handedness[i])):
                hand_label = result_gesture.handedness[i][j].category_name
                gesture_name = result_gesture.gestures[i][j].category_name
                if hand_label == "Left" and not seen_left:
                    left_hand_gesture = gesture_name
                elif hand_label == "Right" and not seen_right:
                    right_hand_gesture = gesture_name

                if seen_right and seen_left:
                    break
    cv2.putText(frame, f"Left: {left_hand_gesture} | Right: {right_hand_gesture}",
                (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)

    cv2.imshow('Gesture Recognition', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
# hands.close()
