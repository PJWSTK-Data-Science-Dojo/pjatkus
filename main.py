import time
from cv.people_count.people_detector import PeopleDetector
from nlp.speech_recognizer import SpeechRecognizer

if __name__ == "__main__":
    people_detector = PeopleDetector(capture_device=1)
    speech_recognizer = SpeechRecognizer()

    people_detector.start_detection()
    speech_recognizer.start_listening()

    try:
        while True:
            count = people_detector.get_people_count()
            speech = speech_recognizer.get_latest_speech()

            output = f"People Count: {count}"
            if speech:
                output += f" | Speech: {speech}"
            print(output)

            time.sleep(0.5)
    except KeyboardInterrupt:
        print("\nExiting...")
    finally:
        people_detector.stop_detection()
        speech_recognizer.stop_listening()
