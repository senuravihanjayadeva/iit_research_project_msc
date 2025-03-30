from fastapi import FastAPI, UploadFile, File
import uvicorn
import numpy as np
import cv2
import torch
from PIL import Image
import io
from detectron2.config import get_cfg
from detectron2.engine import DefaultPredictor
from detectron2 import model_zoo
from detectron2.utils.visualizer import Visualizer, ColorMode

app = FastAPI()

# Load Mask R-CNN Model
cfg = get_cfg()
cfg.merge_from_file(model_zoo.get_config_file("COCO-InstanceSegmentation/mask_rcnn_R_50_FPN_3x.yaml"))
cfg.MODEL.WEIGHTS = "model_final.pth"  # Path to trained weights
cfg.MODEL.ROI_HEADS.SCORE_THRESH_TEST = 0.5
cfg.MODEL.ROI_HEADS.NUM_CLASSES = 3  # Adjust based on your dataset
predictor = DefaultPredictor(cfg)

@app.post("/predict/")
async def predict(file: UploadFile = File(...)):
    """Accepts an image file, processes it through Mask R-CNN, and returns the result."""
    image_bytes = await file.read()
    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    image_np = np.array(image)

    outputs = predictor(image_np)

    v = Visualizer(image_np[:, :, ::-1], scale=1, instance_mode=ColorMode.IMAGE_BW)
    out = v.draw_instance_predictions(outputs["instances"].to("cpu"))
    result_image = Image.fromarray(out.get_image()[:, :, ::-1])

    result_path = "result.jpg"
    result_image.save(result_path)
    return {"message": "Prediction complete", "result_image": "/result.jpg"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
