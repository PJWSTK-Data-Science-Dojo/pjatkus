import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

hand_positions = {'Left': [], 'Right': []}
last_directions = {'Left': None, 'Right': None}
direction_changes = {'Left': 0, 'Right': 0}

def is_waving(positions, hand, last_dir, changes,
              movement_threshold=0.005,
              no_movement_threshold=0.003,
              required_changes=3):
    if len(positions) < 2:
        return False, last_dir, changes

    x_diff = positions[-1][0] - positions[-2][0]
    direction = None
    if x_diff > movement_threshold:
        direction = 'right'
    elif x_diff < -movement_threshold:
        direction = 'left'

    if direction and direction != last_dir:
        last_dir = direction
        changes += 1

    if abs(x_diff) < no_movement_threshold:
        changes = max(0, changes - 1)

    wave_detected = (changes >= required_changes)
    if wave_detected:
        changes = 1

    return wave_detected, last_dir, changes

base_options = python.BaseOptions(model_asset_path='cv/gesture/gesture_recognizer.task')
options = vision.GestureRecognizerOptions(base_options=base_options, num_hands=2)
recognizer = vision.GestureRecognizer.create_from_options(options)

cap = cv2.VideoCapture(1)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
    result_gesture = recognizer.recognize(mp_image)

    left_hand_gesture = "Unknown"
    right_hand_gesture = "Unknown"
    seen_left = False
    seen_right = False

    if result_gesture.gestures and result_gesture.handedness:
        for i in range(len(result_gesture.gestures)):
            hand_label = result_gesture.handedness[i][0].category_name
            gesture_name = result_gesture.gestures[i][0].category_name
            hand_landmarks = result_gesture.hand_landmarks[i]

            if hand_label == "Left" and not seen_left:
                if len(hand_positions['Left']) >= 10:
                    hand_positions['Left'].pop(0)
                hand_positions['Left'].append((hand_landmarks[0].x, hand_landmarks[0].y))

                if gesture_name == "Open_Palm":
                    waving, new_dir, new_changes = is_waving(
                        hand_positions['Left'], 'Left',
                        last_directions['Left'], direction_changes['Left']
                    )
                    left_hand_gesture = "Waving" if waving else "Open_Palm"
                    last_directions['Left'] = new_dir
                    direction_changes['Left'] = new_changes
                else:
                    left_hand_gesture = gesture_name

                seen_left = True

            elif hand_label == "Right" and not seen_right:
                if len(hand_positions['Right']) >= 10:
                    hand_positions['Right'].pop(0)
                hand_positions['Right'].append((hand_landmarks[0].x, hand_landmarks[0].y))

                # Only detect wave if gesture is Open_Palm
                if gesture_name == "Open_Palm":
                    waving, new_dir, new_changes = is_waving(
                        hand_positions['Right'], 'Right',
                        last_directions['Right'], direction_changes['Right']
                    )
                    right_hand_gesture = "Waving" if waving else "Open_Palm"
                    last_directions['Right'] = new_dir
                    direction_changes['Right'] = new_changes
                else:
                    right_hand_gesture = gesture_name

                seen_right = True

    cv2.putText(frame, f"Left: {left_hand_gesture} | Right: {right_hand_gesture}",
                (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)

    cv2.imshow('Waving Detection', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()