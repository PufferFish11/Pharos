import cv2
import torch
import pyttsx3  # For direct TTS output
import threading  # For running TTS in a separate thread

# Load YOLO model from Ultralytics
model = torch.hub.load("ultralytics/yolov5", "yolov5s")
device = "cuda" if torch.cuda.is_available() else "cpu"
model.to(device)

# Assume the focal length (in pixels) is determined via camera calibration.
focal_length = 600.0  # Example value; replace with your calibrated focal length

# Define real-world object widths in meters for different classes.
real_widths = {
    "person": 0.5,  # Approximate shoulder width of a person
    "car": 1.8,  # Typical width of a car
    "chair": 0.6,  # Approximate width of a chair
    "can": 0.1,
    "dining table": 0.5,
    "stop sign": 0.4,
    "traffic light": 0.2,
    "bottle": 0.1,
    "couch": 1.0,
    "box": 0.8,
}


def calculate_distance(bbox, class_label, focal_length, real_widths):
    """
    Calculate distance to an object using the pinhole camera model.
    :param bbox: Tuple (x1, y1, x2, y2) representing the bounding box in pixels.
    :param class_label: Detected object class (string).
    :param focal_length: Camera focal length in pixels.
    :param real_widths: Dictionary mapping class names to real-world widths (meters).
    :return: Estimated distance in meters.
    """
    x1, y1, x2, y2 = bbox
    pixel_width = x2 - x1  # Width of the bounding box in pixels
    if pixel_width <= 0:
        return float("inf")  # Avoid division by zero or invalid width

    # Get the real-world width of the object (default to 1.0 if unknown)
    real_width = real_widths.get(class_label, 1.0)

    # Calculate distance using the formula: distance = (real_width * focal_length) / pixel_width
    distance = (real_width * focal_length) / pixel_width

    # Debugging: Print calculated distance
    print(
        f"Class: {class_label}, Pixel Width: {pixel_width}, Real Width: {real_width}, Distance: {distance:.2f} m"
    )

    return distance


# Initialize the TTS engine
tts_engine = pyttsx3.init()

# Set TTS properties (optional)
tts_engine.setProperty("rate", 175)  # Speed of speech
tts_engine.setProperty("volume", 1.0)  # Volume level (0.0 to 1.0)

# Set the TTS voice to English
voices = tts_engine.getProperty("voices")
for voice in voices:
    if "english" in voice.name.lower():  # Find an English voice
        tts_engine.setProperty("voice", voice.id)
        break


def play_audio_warning(message):
    """
    Generate and play an audio warning using TTS in a separate thread.
    :param message: The warning message to be spoken.
    """

    def _play_audio():
        tts_engine.say(message)
        tts_engine.runAndWait()  # Blocking call to play the audio

    # Start a new thread for TTS playback
    threading.Thread(target=_play_audio, daemon=True).start()


# Open the video stream from the camera.
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Error: Could not open camera.")
    exit()

# Set to track objects that have already triggered a warning
warned_objects = set()

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Perform object detection using YOLO.
    results = model(frame)
    detections = results.xyxy[0].cpu().numpy()  # Each row: [x1, y1, x2, y2, conf, cls]

    # Reset the warned_objects set for each frame
    current_frame_objects = set()

    for det in detections:
        x1, y1, x2, y2, conf, cls = det
        label = model.names[int(cls)]
        if label in real_widths:
            distance = calculate_distance(
                (x1, y1, x2, y2), label, focal_length, real_widths
            )

            # If the object is within 1 meter, provide a warning
            if distance < 1.0:
                current_frame_objects.add(
                    label
                )  # Track the object in the current frame
                if label not in warned_objects:
                    warning_message = f"Warning: {label} detected!"
                    print(warning_message)
                    play_audio_warning(
                        warning_message
                    )  # Play audio in a separate thread
                    warned_objects.add(label)  # Mark the object as warned

                # Draw the bounding box in RED for objects within 1 meter
                color = (0, 0, 255)  # Red in BGR format
            else:
                # Draw the bounding box in GREEN for objects outside 1 meter
                color = (0, 255, 0)  # Green in BGR format

            # Draw the bounding box and the distance label on the frame.
            cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), color, 2)
            cv2.putText(
                frame,
                f"{label}: {distance:.2f} m",
                (int(x1), int(y1) - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.9,
                color,
                2,
            )

    # Remove objects that are no longer in the 1-meter range
    warned_objects = warned_objects.intersection(current_frame_objects)

    # Display the frame
    cv2.imshow("Distance Detection", frame)

    # Check for key press
    key = cv2.waitKey(1) & 0xFF

    # Save the current frame as "captured.png" if "P" is pressed
    if key == ord("p") or key == ord("P"):
        cv2.imwrite("captured.png", frame)
        print("Image saved as captured.png")

    # Exit on 'q' key press
    if key == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
