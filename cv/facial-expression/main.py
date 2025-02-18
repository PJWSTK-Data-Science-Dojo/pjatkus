import cv2
import numpy as np
from tensorflow.keras.models import Sequential, model_from_json
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Dropout, Flatten, Dense, InputLayer

model = Sequential([
    InputLayer(input_shape=(48, 48, 1)),
    Conv2D(128, kernel_size=(3, 3), activation='relu'),
    MaxPooling2D(pool_size=(2, 2)),
    Dropout(0.4),

    Conv2D(256, kernel_size=(3, 3), activation='relu'),
    MaxPooling2D(pool_size=(2, 2)),
    Dropout(0.4),

    Conv2D(512, kernel_size=(3, 3), activation='relu'),
    MaxPooling2D(pool_size=(2, 2)),
    Dropout(0.4),

    Conv2D(512, kernel_size=(3, 3), activation='relu'),
    MaxPooling2D(pool_size=(2, 2)),
    Dropout(0.4),

    Flatten(),
    Dense(512, activation='relu'),
    Dropout(0.4),
    Dense(256, activation='relu'),
    Dropout(0.3),
    Dense(7, activation='softmax')  # 7 classes for facial expressions
])


json_file = open('facialemotionmodel.json', 'r')
model_json = json_file.read()
json_file.close()

model = model_from_json(model_json, custom_objects={"Sequential": Sequential})
model.load_weights('facialemotionmodel.h5')

haar_file = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
face_cascade = cv2.CascadeClassifier(haar_file)

def extract_features(image):
    feature = np.array(image).reshape(1, 48, 48, 1)
    return feature / 255.0

cap = cv2.VideoCapture(1)
labels = {0: 'angry', 1: 'disgust', 2: 'fear', 3: 'happy', 4: 'neutral', 5: 'sad', 6: 'surprise'}

while True:
    ret, frame = cap.read()
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(frame, 1.3, 5)
    if not ret:
        break

    for (p, q, r, s) in faces:
        image = cv2.resize(gray[q:q+s, p:p+r], (48, 48))
        pred = model.predict(extract_features(image))
        prediction_label = labels[pred.argmax()]
        cv2.rectangle(frame, (p, q), (p+r, q+s), (255, 0, 0), 2)
        cv2.putText(frame, '% s' % (prediction_label), (p-10, q-10),
                    cv2.FONT_HERSHEY_COMPLEX_SMALL, 2, (0, 0, 255))
    cv2.imshow('Output', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()