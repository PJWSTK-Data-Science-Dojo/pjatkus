import threading
import speech_recognition as sr
import queue


class SpeechRecognizer:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.audio_queue = queue.Queue()
        self.running = False

    def _background_listen(self):
        with sr.Microphone() as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
            while self.running:
                try:
                    print("Listening for speech...")
                    audio = self.recognizer.listen(source)
                    text = self.recognizer.recognize_google(audio, language="pl-PL")
                    self.audio_queue.put(text)
                except sr.UnknownValueError:
                    continue
                except sr.RequestError:
                    self.audio_queue.put("ERROR: Speech recognition request failed.")
                    break

    def start_listening(self):
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self._background_listen, daemon=True)
            self.thread.start()
            print("Speech recognition started in the background.")

    def stop_listening(self):
        self.running = False
        if hasattr(self, "thread"):
            self.thread.join()
            print("Speech recognition stopped.")

    def get_latest_speech(self):
        try:
            return self.audio_queue.get_nowait()
        except queue.Empty:
            return None
