from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings
import torch


class YOLOSettings(BaseSettings):
    model_name: str = Field("yolov8n.pt", description="YOLO model name")
    model_url: str = Field(
        "https://ultralytics.com/assets/yolov8n.pt", description="YOLO model url"
    )
    fuse_model: bool = Field(
        True, description="boolean flag whether to fuse model or not"
    )
    device: str | None = Field(
        None,
        description="device for loading and using model, default to cuda if not set and available",
    )
    imgsz: int = Field(576 // 2, description="image size")

    @property
    def device_actual(self):
        return self.device or ("cuda" if torch.cuda.is_available() else "cpu")

    @property
    def model_path(self) -> Path:
        # server_code_path / detection_models / model_name
        server_code_path = Path(__file__).parent.parent.parent
        return server_code_path / "detection_models" / self.model_name
