import io
import logging
from pathlib import Path
import urllib.request

from PIL import Image
from ultralytics import YOLO

from app.models.detection_result import DetectionObject
from app.models.detection_result import DetectionResponse
from app.models.detection_settings import YOLOSettings

logger = logging.getLogger(__name__)


def download_model(model_url: str, model_path: Path):
    logger.info(f"Downloading model from {model_url} to {model_path}")
    model_path.parent.mkdir(parents=True, exist_ok=True)
    urllib.request.urlretrieve(model_url, model_path)


class DetectionService:
    def __init__(self, settings: YOLOSettings = None):
        self.settings = settings or YOLOSettings()
        self.model_path: Path = self.settings.model_path
        self.device = self.settings.device_actual
        self.imgsz = self.settings.imgsz
        self.model = self.load_model()

    def load_model(self):
        if not self.model_path.exists():
            download_model(self.settings.model_url, self.model_path)
        model = YOLO(str(self.model_path))
        logger.info(f"Loaded model from {self.model_path}")
        if self.settings.fuse_model:
            logger.info("Fusing model")
            model.fuse()
        model.to(self.device)
        logger.info(f"Model fully loaded to device: {self.device}")
        return model

    def detect(self, image_bytes: bytes) -> DetectionResponse:
        logger.info("Running detection on image")
        img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        results = self.model.predict(
            img, device=self.device, imgsz=self.imgsz, verbose=False
        )
        objects = []
        for r in results:
            for box, cls, conf in zip(
                r.boxes.xyxy, r.boxes.cls, r.boxes.conf, strict=True
            ):
                objects.append(
                    DetectionObject(
                        label=self.model.names[int(cls)],
                        confidence=float(conf),
                        bbox=[float(x) for x in box],
                    )
                )
        logger.info(f"Found {len(objects)} objects in provided image.")
        return DetectionResponse(objects=objects)
