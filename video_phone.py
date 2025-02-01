import cv2
import torch
import pyttsx3
import threading

# Load YOLO model from Ultralytics
model = torch.hub.load("ultralytics/yolov5", "yolov5s")
device = "cuda" if torch.cuda.is_available() else "cpu"
model.to(device)


# ===================================================
# 1. EpocCam Configuration (USB Connection)
# ===================================================
def find_epoccam_index():
    """Automatically detect EpocCam's camera index"""
    for index in [1, 2, 3]:  # Common camera indices
        cap = cv2.VideoCapture(index)
        if cap.isOpened():
            ret, _ = cap.read()
            cap.release()
            if ret:
                return index
    return -1  # Not found


epoccam_index = find_epoccam_index()
if epoccam_index == -1:
    print("Error: EpocCam not found. Ensure:")
    print("- iPhone is connected via USB")
    print("- EpocCam app is running in USB mode")
    print("- EpocCam drivers are installed")
    exit()

print(f"EpocCam detected at index: {epoccam_index}")
cap = cv2.VideoCapture(epoccam_index)

# ===================================================
# 2. Distance Calculation Parameters
# ===================================================
focal_length = 600.0  # Calibrate for your setup
real_widths = {
    "person": 0.5,
    "car": 1.8,
    "chair": 0.6,
    "can": 0.1,
    "dining table": 0.5,
    "stop sign": 0.4,
    "traffic light": 0.2,
    "laptop": 0.4,
    "bottle": 0.1,
    "couch": 1.0,
    "box": 0.8,
}


def calculate_distance(bbox, class_label, focal_length, real_widths):
    x1, y1, x2, y2 = bbox
    pixel_width = x2 - x1
    if pixel_width <= 0:
        return float("inf")
    real_width = real_widths.get(class_label, 1.0)
    return (real_width * focal_length) / pixel_width


# ===================================================
# 3. TTS Configuration (English Voice)
# ===================================================
tts_engine = pyttsx3.init()
tts_engine.setProperty("rate", 150)
tts_engine.setProperty("volume", 1.0)

# Force English voice
for voice in tts_engine.getProperty("voices"):
    if "english" in voice.name.lower():
        tts_engine.setProperty("voice", voice.id)
        break


def play_audio_warning(message):
    def _play_audio():
        tts_engine.say(message)
        tts_engine.runAndWait()

    threading.Thread(target=_play_audio, daemon=True).start()


# ===================================================
# 4. Main Processing Loop
# ===================================================
warned_objects = set()

while True:
    # Read frame from iPhone
    ret, frame = cap.read()
    if not ret:
        print("Error reading frame from iPhone")
        break

    # Object detection
    results = model(frame)
    detections = results.xyxy[0].cpu().numpy()

    current_frame_objects = set()

    for det in detections:
        x1, y1, x2, y2, conf, cls = det
        label = model.names[int(cls)]

        if label in real_widths:
            # Distance calculation
            distance = calculate_distance(
                (x1, y1, x2, y2), label, focal_length, real_widths
            )

            # Warning logic
            if distance < 1.0:
                current_frame_objects.add(label)
                color = (0, 0, 255)  # Red
                if label not in warned_objects:
                    warning = f"Warning: {label} at {distance:.2f} meters!"
                    print(warning)
                    play_audio_warning(warning)
                    warned_objects.add(label)
            else:
                color = (0, 255, 0)  # Green

            # Draw bounding box
            cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), color, 2)
            cv2.putText(
                frame,
                f"{label}: {distance:.2f}m",
                (int(x1), int(y1) - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                color,
                2,
            )

    # Cleanup warned objects
    warned_objects = warned_objects.intersection(current_frame_objects)

    # Display frame
    cv2.imshow("iPhone Camera Feed", frame)

    # Key controls
    key = cv2.waitKey(1) & 0xFF
    if key == ord("p") or key == ord("P"):
        cv2.imwrite("captured.png", frame)
        print("Snapshot saved!")
    if key == ord("q"):
        break

# Cleanup
cap.release()
cv2.destroyAllWindows()
