from fastapi import FastAPI, UploadFile, File
import uvicorn
import numpy as np
from PIL import Image
import io
from detectron2.config import get_cfg
from detectron2.engine import DefaultPredictor
from detectron2 import model_zoo
from detectron2.utils.visualizer import Visualizer, ColorMode
import boto3

app = FastAPI()

# DigitalOcean Spaces Configuration
DO_SPACES_KEY = ""
DO_SPACES_SECRET = ""
DO_SPACES_REGION = "tor1"  # Example: "nyc3"
DO_SPACES_BUCKET = "iitresearchsenura"
DO_SPACES_CDN_URL = "https://iitresearchsenura.tor1.digitaloceanspaces.com"  # Example: https://your-bucket.nyc3.cdn.digitaloceanspaces.com

# Initialize Spaces client
s3_client = boto3.client(
    "s3",
    endpoint_url=f"https://{DO_SPACES_REGION}.digitaloceanspaces.com",
    aws_access_key_id=DO_SPACES_KEY,
    aws_secret_access_key=DO_SPACES_SECRET,
)

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

    # Visualize Predictions
    v = Visualizer(image_np[:, :, ::-1], scale=1, instance_mode=ColorMode.IMAGE_BW)
    out = v.draw_instance_predictions(outputs["instances"].to("cpu"))
    result_image = Image.fromarray(out.get_image()[:, :, ::-1])

    # Save locally
    local_path = "result.jpg"
    result_image.save(local_path)

    # Upload to DigitalOcean Spaces
    s3_client.upload_file(local_path, DO_SPACES_BUCKET, local_path, ExtraArgs={"ACL": "public-read"})

    # Generate public URL
    result_url = f"{DO_SPACES_CDN_URL}/{local_path}"

    return {"message": "Prediction complete", "result_image_url": result_url}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
