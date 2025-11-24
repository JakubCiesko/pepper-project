import asyncio
import base64
import io
import logging
import random

from fastapi import APIRouter
from fastapi import UploadFile
from fastapi.responses import JSONResponse
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

from app.services.detection import DetectionService
from app.services.ws_manager import ws_manager

logger = logging.getLogger(__name__)
router = APIRouter()
detection_service = DetectionService()


def get_color_encoding(objects: list[dict]) -> dict[str, str]:
    logger.info("Running color encoding, computing unique colors for labels...")
    unique_labels = list({obj["label"] for obj in objects})
    colors = {
        label: tuple(random.choices(range(50, 256), k=3)) for label in unique_labels
    }
    logger.info(f"{len(colors)} colors assigned")
    return colors


def annotate_image(
    img_bytes: bytes, objects: list[dict], colors: dict[str, str]
) -> str:
    logger.info(f"Annotating image with {len(objects)} objects")
    img = Image.open(io.BytesIO(img_bytes)).convert("RGB")
    draw = ImageDraw.Draw(img)
    w, h = img.size
    num_objects = max(1, len(objects))
    font_size = max(10, int(h * 0.05 / (num_objects**0.5)))  # bulharske konstanty
    font = ImageFont.load_default(font_size)
    rect_width = max(2, int(h * 0.005))
    for obj in objects:
        x1, y1, x2, y2 = obj["bbox"]
        label = obj["label"]
        conf = obj["confidence"]
        color = colors[label]
        draw.rectangle([x1, y1, x2, y2], outline=color, width=rect_width)
        text = f"{label} {conf:.2f}"
        bbox = font.getbbox(text)
        text_w, text_h = bbox[2] - bbox[0], bbox[3] - bbox[1]

        text_bg = [x1, y1 - text_h - 2, x1 + text_w + 2, y1]
        draw.rectangle(text_bg, fill=color)
        draw.text((x1 + 1, y1 - text_h - 1), text, fill="black", font=font)

    buffered = io.BytesIO()
    img.save(buffered, format="JPEG")
    return base64.b64encode(buffered.getvalue()).decode("utf-8")


@router.post("/detect")
async def detect(image: UploadFile) -> JSONResponse:
    img_bytes = await image.read()
    try:
        logger.info("Running detection endpoint...")
        response = detection_service.detect(img_bytes)
        response_dict = response.model_dump()
        colors = get_color_encoding(response_dict["objects"])
        annotated_image_b64 = annotate_image(
            img_bytes, response_dict["objects"], colors
        )
        broadcast_message = {
            "objects": response_dict["objects"],
            "image": annotated_image_b64,
            "colors": colors,
        }
        asyncio.create_task(ws_manager.broadcast(broadcast_message))
        return JSONResponse(status_code=200, content=response_dict)
    except Exception as e:
        logger.error(f"Detection failed: {e}")
        return JSONResponse(content={"error": "Inference failed", "detail": str(e)})
