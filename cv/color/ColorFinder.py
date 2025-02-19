import cv2
import numpy
from ultralytics import YOLO
from PIL import Image


class ColorFinder:

    def __init__(self):
        self.cameraWebcam = cv2.VideoCapture(0)
        self.cameraWebcam.set(3, 640)  # magic numbers
        self.cameraWebcam.set(4, 480)

        self.hsv_ranges = {
            'red': ([0, 100, 100], [10, 255, 255], [170, 100, 100], [180, 255, 255]),
            'blue': ([90, 50, 50], [130, 255, 255]),
            'green': ([35, 50, 50], [80, 255, 255]),
            'black': ([0, 0, 0], [180, 255, 40]),
            'white': ([0, 0, 200], [180, 30, 255])
        }

        self.model = YOLO('../yolov8n.pt')

    def findColor(self, imageWebCam):
        if imageWebCam.size == 0:
            return "brak"

        hsv = cv2.cvtColor(imageWebCam, cv2.COLOR_BGR2HSV)
        avgColor = numpy.mean(hsv, axis=(0, 1))

        if avgColor[2] < 50:
            return "black"
        if avgColor[1] < 40 and avgColor[2] > 200:
            return "white"

        # HSV
        for name, ranges in self.hsv_ranges.items():
            for z in ranges:
                if all(z[0] <= avgColor[i] <= z[1] for i in range(3)):
                    return name
        return "inne"


    # --------------- this needs to be fixed ----------------
    # - the problem is that it doesn't work as intended and maybe there is a way to combine these two functions
    """bs from deepseek but it returns the color name instead of the color range HSV, RGB"""
    def findColorWithPIL(self, imageWebCam):
        """Znajduje nazwę koloru na podstawie HSV zamiast RGB"""
        try:
            if imageWebCam.size == 0:
                return "unknown"

            # Pobierz dominujący kolor
            img = Image.fromarray(cv2.cvtColor(imageWebCam, cv2.COLOR_BGR2RGB))
            img = img.resize((20, 20))  # mniejszy rozmiar = mniej kolorów
            colors = img.getcolors(10000) or []
            if not colors:
                return "unknown"

            _, dominant_color = max(colors, key=lambda x: x[0])

            # Konwersja RGB do HSV
            bgr_color = [dominant_color[2], dominant_color[1], dominant_color[0]]
            hsv = cv2.cvtColor(numpy.array([[bgr_color]], dtype=numpy.uint8), cv2.COLOR_BGR2HSV)[0][0]

            # Sprawdź w zdefiniowanych zakresach HSV
            for color_name, ranges in self.hsv_ranges.items():
                # Dla kolorów z wieloma zakresami (jak czerwony)
                for i in range(0, len(ranges), 2):
                    lower = numpy.array(ranges[i])
                    upper = numpy.array(ranges[i + 1])
                    if (lower[0] <= hsv[0] <= upper[0] and
                            lower[1] <= hsv[1] <= upper[1] and
                            lower[2] <= hsv[2] <= upper[2]):
                        return color_name

            # Jeśli nie pasuje do żadnego zakresu
            return "other"

        except Exception as e:
            return "error"
            print(f"Błąd: {e}")


    # ----------- this one too -----

    # def findColorWithPIL(self, imageWebCam):
    #     """Hybrydowe wykrywanie koloru"""
    #     try:
    #         if imageWebCam.size == 0:
    #             return "empty"
    #
    #         # Próba prostego wykrycia przez średnią
    #         try:
    #             hsv = cv2.cvtColor(imageWebCam, cv2.COLOR_BGR2HSV)
    #             avg = numpy.mean(hsv, axis=(0, 1))
    #             if avg[2] < 50: return "black"
    #             if avg[1] < 40 and avg[2] > 200: return "white"
    #         except:
    #             pass
    #
    #         # Próba z PIL z mniejszą rozdzielczością
    #         try:
    #             small_img = cv2.resize(imageWebCam, (50, 50))
    #             img = Image.fromarray(small_img)
    #             colors = img.getcolors(5000)  # większy limit
    #             if colors:
    #                 return max(colors, key=lambda x: x[0])[1]
    #         except:
    #             pass
    #
    #         # Ostatecznie zwróć pierwszy piksel
    #         return tuple(imageWebCam[0, 0].tolist())
    #     except Exception as e:
    #         return "error"
    #         print(e)

    def processFrame(self, frame):
        """YOLO i OpenCV"""
        scores = self.model(frame)

        for score in scores:
            # cpu ?
            boxes = score.boxes.xyxy.cpu().numpy()
            for box in boxes:
                x1, y1, x2, y2 = map(int, box[:4])
                x1 = max(0, x1)
                y1 = max(0, y1)
                x2 = min(frame.shape[1], x2)
                y2 = min(frame.shape[0], y2)

                if x2 <= x1 or y2 <= y1:
                    continue

                # Obszar koszulki (na sztywno)
                # dividing frames ?
                koszulka = frame[y1:y1 + int((y2 - y1) * 0.4), x1:x2]
                # kolor_koszulki = self.findColor(koszulka)
                kolor_koszulki = self.findColorWithPIL(koszulka)


                # Obszar spodni
                spodnie = frame[y1 + int((y2 - y1) * 0.4):y1 + int((y2 - y1) * 0.7), x1:x2]
                # kolor_spodni = self.findColor(spodnie)
                kolor_spodni = self.findColorWithPIL(spodnie)


                # Rysuj wyniki
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(frame, f'Shirt: {kolor_koszulki}', (x1 + 5, y1 + 20),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
                cv2.putText(frame, f'Pants: {kolor_spodni}', (x1 + 5, y1 + 50),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

        return frame

    def runDetection(self):
        while True:
            ret, frame = self.cameraWebcam.read()
            if not ret:
                print("cameraWebcam problem")
                break

            result = self.processFrame(frame)

            cv2.imshow('test', result)
            if cv2.waitKey(25) == 27:  # ESC
                break

        self.cameraWebcam.release()
        cv2.destroyAllWindows()


if __name__ == '__main__':
    demo = ColorFinder()
    demo.runDetection()