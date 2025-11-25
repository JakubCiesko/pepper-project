import io
import logging
import random
import sys
import time

from conversation import Conversation
from naoqi import ALProxy
from PIL import Image
import requests

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logger = logging.getLogger(__name__)

ROBOT_IP = "127.0.0.1"
ROBOT_PORT = 35417

SERVER_URL = "http://0.0.0.0:8000"
DASHBOARD_URL = SERVER_URL + "/dashboard"
DETECT_URL = SERVER_URL + "/api/detect"


class PepperClient:
    def __init__(self):
        logger.info("Initializing PepperClient")
        try:
            self.tts = ALProxy("ALTextToSpeech", ROBOT_IP, ROBOT_PORT)
            self.video = ALProxy("ALVideoDevice", ROBOT_IP, ROBOT_PORT)
            self.conversation = Conversation(memory_length=50, language="cs")
            self.confidence_threshold = 0.30

        except Exception, e:
            logger.error("[ERROR] Connection failed: %s", str(e))
            sys.exit(1)

        self.camera_handle = None

    def start(self):
        # Index 0 = Top Camera, Res 2 = 640x480, Color 11 = RGB, FPS 10
        logger.info("Starting camera called: PepperYOLO, resolution 640x480, RGB color, 10 FPS")
        self.camera_handle = self.video.subscribeCamera("PepperYOLO", 0, 2, 11, 10)
        logger.info("Camera started")

    def loop(self):
        logger.info("Starting detection  loop")
        try:
            while True:
                logger.info("Taking picture")
                nao_img = self.video.getImageRemote(self.camera_handle)

                if nao_img is None:
                    continue

                width = nao_img[0]
                height = nao_img[1]
                raw_data = nao_img[6]
                logger.info("Photo taken")

                image = Image.frombytes("RGB", (width, height), raw_data)


                img_buffer = io.BytesIO()
                image.save(img_buffer, format="JPEG")
                img_jpeg_bytes = img_buffer.getvalue()

                pic = random.choice([
                    "/home/jakub-ciesko/Desktop/rezen.jpg",
                    "/home/jakub-ciesko/Desktop/kiri-mala.jpeg",
                    "/home/jakub-ciesko/Desktop/test-imgs/dogs.jpg",
                    "/home/jakub-ciesko/Desktop/test-imgs/oktober.jpg",
                    "/home/jakub-ciesko/Desktop/test-imgs/ja.jpg"
                ])
                image = Image.open(pic)
                img_buffer = io.BytesIO()
                image.save(img_buffer, format="JPEG")
                img_jpeg_bytes = img_buffer.getvalue()
                try:
                    files = {
                        "image": ("capture.jpg", img_jpeg_bytes, "image/jpeg")
                    }
                    response = requests.post(DETECT_URL, files=files, timeout=5)
                    if response.status_code == 200:
                        data = response.json()
                        self.handle_results(data)
                    else:
                        logger.warn(
                        "Server returned %d",  response.status_code)
                except Exception, e:
                    logger.error(
                    "Network Request failed: %s" ,str(e))
                # Sleep to control FPS (e.g., check every 2 seconds)
                time.sleep(2.0)

        except KeyboardInterrupt:
            logger.info("Keyboard interrupt, stopping...")
        finally:
            self.cleanup()

    def handle_results(self, data):
        objects = data.get("objects", [])
        if not objects:
            return

        labels = [obj["label"] for obj in objects if obj.get("confidence", 0) > self.confidence_threshold]
        if not labels:
            return

        sentence = self.conversation.observe(labels)
        logger.info("[ROBOT]: %s", sentence)
        self.tts.say(sentence)

    def cleanup(self):
        logger.info("Cleaning up")
        if self.camera_handle:
            self.video.unsubscribe(self.camera_handle)
        # self.tablet.hideWebview()
        logger.info("Cleaned up")


if __name__ == "__main__":
    client = PepperClient()
    client.start()
    client.loop()
