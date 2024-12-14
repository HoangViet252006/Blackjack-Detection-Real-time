from ultralytics import YOLO
import cv2
from src.config import *
import pickle

class Card_detections():
    def __init__(self, model_path):
        self.model = YOLO(model_path)

    def detections(self, frames, is_stub=False, stub_path=None):
        card_detection = []
        if is_stub and stub_path is not None:
            with open(stub_path, 'rb') as f:
                card_detection = pickle.load(f)
                return card_detection
        for frame in frames:
            card_detection.append(self.detection(frame))

        if stub_path is not None:
            with open(stub_path, 'wb') as f:
                pickle.dump(card_detection, f)
        return card_detection

    def detection(self, frame):
        # Predict bounding boxes
        results = self.model.predict(source = frame, save = False, conf=0.5)
        boxes = list(results[0].boxes)
        boxes = sorted(boxes, reverse=False, key=lambda x: x.xyxy[0][1])

        card_detection = {}
        class_pred = set()
        for box in boxes:
            class_id = int(box.cls[0])  # Get class ID
            if class_id in class_pred:  # Avoid duplicate classes
                continue
            class_name = self.model.names[class_id]
            bbox = box.xyxy.tolist()[0]
            card_detection[class_name] = bbox
            class_pred.add(class_id)

        return card_detection

    def drawing_bounding_box(self, frame, card_dict):
        for cls_name, bbox in card_dict.items():
            x1, y1, x2, y2 = map(int, bbox)
            color = BLUE_COLOR
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            label = f"{cls_name}"
            cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
        return frame

