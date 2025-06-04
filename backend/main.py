from fastapi import FastAPI, UploadFile, File, Form
from typing import Optional
from uuid import uuid4
import uvicorn
import numpy as np
from PIL import Image
import io
from detectron2.config import get_cfg
from detectron2.engine import DefaultPredictor
from detectron2 import model_zoo
from detectron2.utils.visualizer import Visualizer, ColorMode
import boto3
from fastapi.middleware.cors import CORSMiddleware
from detectron2.structures import Instances

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

# Load Mask R-CNN Model 1
cfg1 = get_cfg()
cfg1.merge_from_file(model_zoo.get_config_file("COCO-InstanceSegmentation/mask_rcnn_R_50_FPN_3x.yaml"))
cfg1.MODEL.WEIGHTS = "model_final.pth"  # Path to trained weights
cfg1.MODEL.ROI_HEADS.SCORE_THRESH_TEST = 0.5
cfg1.MODEL.ROI_HEADS.NUM_CLASSES = 3  # Adjust based on your dataset
predictor = DefaultPredictor(cfg1)

# Load Mask R-CNN Model 2
cfg2 = get_cfg()
cfg2.merge_from_file(model_zoo.get_config_file("COCO-InstanceSegmentation/mask_rcnn_R_50_FPN_3x.yaml"))
cfg2.MODEL.WEIGHTS = "model2_final.pth"  # Path to trained weights
cfg2.MODEL.ROI_HEADS.SCORE_THRESH_TEST = 0.5
cfg2.MODEL.ROI_HEADS.NUM_CLASSES = 6  # Adjust based on your dataset
predictor2 = DefaultPredictor(cfg2)

# Load Mask R-CNN Model 3
cfg3 = get_cfg()
cfg3.merge_from_file(model_zoo.get_config_file("COCO-InstanceSegmentation/mask_rcnn_R_50_FPN_3x.yaml"))
cfg3.MODEL.WEIGHTS = "model3_final.pth"  # Path to trained weights
cfg3.MODEL.ROI_HEADS.SCORE_THRESH_TEST = 0.5
cfg3.MODEL.ROI_HEADS.NUM_CLASSES = 5  # Adjust based on your dataset
predictor3 = DefaultPredictor(cfg3)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Replace with your frontend URL
    allow_credentials=True,
    allow_methods=["*"],  # Allows all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # Allows all headers
)

def map_categories_to_diseases(category_ids):
    disease_map = {
        0: "Healthy Tooth",  # Example: Replace with your actual categories
        1: "Cavity",
        2: "Implant",
        3: "Infected Teeth",
        4: "Filling",
        5: "Impacted Tooth"
    }
    diseases = [disease_map.get(int(cat), "Unknown") for cat in category_ids]
    return diseases

@app.post("/predict/model1")
async def predictModel1(file: UploadFile = File(...)):
    """Accepts an image file, processes it through Mask R-CNN, and returns the result without labels."""
    image_bytes = await file.read()
    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    image_np = np.array(image)

    outputs = predictor(image_np)
    instances = outputs["instances"].to("cpu")
    category_ids = outputs["instances"].pred_classes.to("cpu").numpy()
    predicted_diseases = map_categories_to_diseases(category_ids)
    print(f"Predicted diseases: {predicted_diseases}")  # For debugging
    # Send diseases to LLM for treatment recommendations
    disease_string = ', '.join(predicted_diseases)
    # 🔇 Remove labels and scores
    instances.remove("pred_classes")
    instances.remove("scores")

    # 🖼️ Visualize only boxes/masks
    v = Visualizer(image_np[:, :, ::-1], scale=1, instance_mode=ColorMode.IMAGE_BW)
    out = v.draw_instance_predictions(instances)
    result_image = Image.fromarray(out.get_image()[:, :, ::-1])

    # 💾 Save locally
    local_path = f"{uuid4()}.jpg"
    result_image.save(local_path)

    # ☁️ Upload to DigitalOcean Spaces
    s3_client.upload_file(local_path, DO_SPACES_BUCKET, local_path, ExtraArgs={"ACL": "public-read"})

    # 🔗 Generate public URL
    result_url = f"{DO_SPACES_CDN_URL}/{local_path}"

    return {"message": "Prediction complete", "result_image_url": result_url, "diseases": disease_string}

@app.post("/predict/model2")
async def predictModel2(file: UploadFile = File(...)):
    """Accepts an image file, processes it through Mask R-CNN, and returns the result."""
    image_bytes = await file.read()
    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    image_np = np.array(image)

    outputs = predictor2(image_np)


    # Get category IDs and map them to diseases
    category_ids = outputs["instances"].pred_classes.to("cpu").numpy()
    predicted_diseases = map_categories_to_diseases(category_ids)
    
    print(f"Predicted diseases: {predicted_diseases}")  # For debugging

    # Send diseases to LLM for treatment recommendations
    disease_string = ', '.join(predicted_diseases)

    # Visualize Predictions with scores
    v = Visualizer(image_np[:, :, ::-1], scale=1, instance_mode=ColorMode.IMAGE_BW)
    out = v.draw_instance_predictions(outputs["instances"].to("cpu"))

    result_image = Image.fromarray(out.get_image()[:, :, ::-1])

    # Save locally
    local_path = f"{uuid4()}.jpg"
    result_image.save(local_path)

    # Upload to DigitalOcean Spaces
    s3_client.upload_file(local_path, DO_SPACES_BUCKET, local_path, ExtraArgs={"ACL": "public-read"})

    # Generate public URL
    result_url = f"{DO_SPACES_CDN_URL}/{local_path}"

    return {"message": "Prediction complete", "result_image_url": result_url, "diseases": disease_string}

@app.post("/predict/model2/custom")
async def predictModel2Custom(
    file: UploadFile = File(...),
    category_id: Optional[int] = Form(1)  # Default to 1 if not provided
):
    """Accepts an image and category ID, returns only the top 2 predictions for that category."""
    image_bytes = await file.read()
    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    image_np = np.array(image)

    outputs = predictor2(image_np)
    instances = outputs["instances"].to("cpu")
    category_ids = outputs["instances"].pred_classes.to("cpu").numpy()
    predicted_diseases = map_categories_to_diseases(category_ids)
    print(f"Predicted diseases: {predicted_diseases}")  # For debugging
    # Send diseases to LLM for treatment recommendations
    disease_string = ', '.join(predicted_diseases)
    # 🔍 Filter predictions by category
    mask = instances.pred_classes == category_id
    category_instances = instances[mask]

    # 📊 Sort by score and keep top 2
    if len(category_instances) > 2:
        top2_indices = category_instances.scores.argsort(descending=True)[:2]
        category_instances = category_instances[top2_indices]

    # Remove the class labels and confidence scores
    category_instances.remove("pred_classes")
    category_instances.remove("scores")

    # 🎨 Visualize top 2 predictions
    v = Visualizer(image_np[:, :, ::-1], scale=1, instance_mode=ColorMode.IMAGE_BW)
    
    out = v.draw_instance_predictions(category_instances) 

    result_image = Image.fromarray(out.get_image()[:, :, ::-1])

    # 💾 Save locally
    local_path = f"{uuid4()}.jpg"
    result_image.save(local_path)

    # ☁️ Upload to DigitalOcean Spaces
    s3_client.upload_file(local_path, DO_SPACES_BUCKET, local_path, ExtraArgs={"ACL": "public-read"})

    # 🔗 Generate public URL
    result_url = f"{DO_SPACES_CDN_URL}/{local_path}"

    return {
        "message": "Prediction complete (Top 2 shown)",
        "filtered_category_id": category_id,
        "result_image_url": result_url,
        "diseases": disease_string
    }

@app.post("/predict/model3/custom")
async def predictModel3Custom(
    file: UploadFile = File(...),
    category_id: Optional[int] = Form(1)  # Default to 1 if not provided
):
    """Accepts an image and category ID, returns only the top 2 predictions for that category."""
    image_bytes = await file.read()
    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    image_np = np.array(image)

    outputs = predictor3(image_np)
    instances = outputs["instances"].to("cpu")
    category_ids = outputs["instances"].pred_classes.to("cpu").numpy()
    predicted_diseases = map_categories_to_diseases(category_ids)
    print(f"Predicted diseases: {predicted_diseases}")  # For debugging
    # Send diseases to LLM for treatment recommendations
    disease_string = ', '.join(predicted_diseases)
    # 🔍 Filter predictions by category
    mask = instances.pred_classes == category_id
    category_instances = instances[mask]

    # 📊 Sort by score and keep top 2
    if len(category_instances) > 2:
        top2_indices = category_instances.scores.argsort(descending=True)[:2]
        category_instances = category_instances[top2_indices]

    # Remove the class labels and confidence scores
    category_instances.remove("pred_classes")
    category_instances.remove("scores")

    # 🎨 Visualize top 2 predictions
    v = Visualizer(image_np[:, :, ::-1], scale=1, instance_mode=ColorMode.IMAGE_BW)
    
    out = v.draw_instance_predictions(category_instances) 

    result_image = Image.fromarray(out.get_image()[:, :, ::-1])

    # 💾 Save locally
    local_path = f"{uuid4()}.jpg"
    result_image.save(local_path)

    # ☁️ Upload to DigitalOcean Spaces
    s3_client.upload_file(local_path, DO_SPACES_BUCKET, local_path, ExtraArgs={"ACL": "public-read"})

    # 🔗 Generate public URL
    result_url = f"{DO_SPACES_CDN_URL}/{local_path}"

    return {
        "message": "Prediction complete (Top 2 shown)",
        "filtered_category_id": category_id,
        "result_image_url": result_url,
        "diseases": disease_string
    }


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
