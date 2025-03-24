import cv2
import numpy as np
import threading
import time

class PeopleDetector:
    def __init__(self, yolo_cfg="yolov3.cfg", yolo_weights="yolov3.weights", coco_names="coco.names", capture_device=1):
        self.net = cv2.dnn.readNet(yolo_weights, yolo_cfg)
        self.layer_names = self.net.getLayerNames()
        unconnected_out_layers = self.net.getUnconnectedOutLayers()
        self.output_layers = [self.layer_names[i - 1] for i in unconnected_out_layers]

        with open(coco_names, "r") as f:
            self.classes = [line.strip() for line in f.readlines()]

        self.capture_device = capture_device
        self.num_people = 0
        self.running = False
        self.lock = threading.Lock()

    def _background_detect(self):
        cap = cv2.VideoCapture(self.capture_device)
        if not cap.isOpened():
            print("Error: Could not open video capture device.")
            self.running = False
            return

        while self.running:
            ret, frame = cap.read()
            if not ret:
                print("Failed to grab frame")
                continue

            height, width, channels = frame.shape

            blob = cv2.dnn.blobFromImage(frame, 0.00392, (416, 416), (0, 0, 0), True, crop=False)
            self.net.setInput(blob)
            outs = self.net.forward(self.output_layers)

            boxes = []
            confidences = []
            class_ids = []

            for out in outs:
                for detection in out:
                    scores = detection[5:]
                    class_id = np.argmax(scores)
                    confidence = scores[class_id]
                    # class_id equal 0 is person
                    if class_id == 0 and confidence > 0.5:
                        center_x = int(detection[0] * width)
                        center_y = int(detection[1] * height)
                        w = int(detection[2] * width)
                        h = int(detection[3] * height)
                        x = int(center_x - w / 2)
                        y = int(center_y - h / 2)
                        boxes.append([x, y, w, h])
                        confidences.append(float(confidence))
                        class_ids.append(class_id)

            indexes = cv2.dnn.NMSBoxes(boxes, confidences, 0.5, 0.4)
            num_people = len(indexes)

            with self.lock:
                self.num_people = num_people

            time.sleep(0.02)

        cap.release()
        cv2.destroyAllWindows()

    def start_detection(self):
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self._background_detect, daemon=True)
            self.thread.start()
            print("PeopleDetector started.")

    def stop_detection(self):
        self.running = False
        if hasattr(self, "thread"):
            self.thread.join()
            print("PeopleDetector stopped.")

    def get_people_count(self):
        with self.lock:
            return self.num_people