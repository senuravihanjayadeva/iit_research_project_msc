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
from detectron2.structures import Instances, Boxes
from detectron2.data import MetadataCatalog
import torch

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
cfg1.MODEL.WEIGHTS = "model_final.pth"
cfg1.MODEL.ROI_HEADS.SCORE_THRESH_TEST = 0.5
cfg1.MODEL.ROI_HEADS.NUM_CLASSES = 3
predictor = DefaultPredictor(cfg1)
cfg2 = get_cfg()
cfg2.merge_from_file(model_zoo.get_config_file("COCO-InstanceSegmentation/mask_rcnn_R_50_FPN_3x.yaml"))
cfg2.MODEL.WEIGHTS = "model2_final.pth"
cfg2.MODEL.ROI_HEADS.SCORE_THRESH_TEST = 0.3
cfg2.MODEL.ROI_HEADS.NUM_CLASSES = 6
predictor2 = DefaultPredictor(cfg2)
cfg3 = get_cfg()
cfg3.merge_from_file(model_zoo.get_config_file("COCO-InstanceSegmentation/mask_rcnn_R_50_FPN_3x.yaml"))
cfg3.MODEL.WEIGHTS = "model3_final.pth"
cfg3.MODEL.ROI_HEADS.SCORE_THRESH_TEST = 0.5
cfg3.MODEL.ROI_HEADS.NUM_CLASSES = 5
predictor3 = DefaultPredictor(cfg3)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Replace with your frontend URL
    allow_credentials=True,
    allow_methods=["*"],  # Allows all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # Allows all headers
)

def map_categories_to_diseases(category_ids, selected_category_id):
    disease_map = {
        0: "Healthy Tooth",
        1: "Cavity",
        2: "Fillings",
        3: "Impacted Tooth",
        4: "Implant",
        5: "Infected-teeth"
    }

    # Filter only category_ids that match the selected one
    filtered_ids = [int(cat) for cat in category_ids if int(cat) == selected_category_id]

    # Map to disease names
    diseases = [disease_map.get(cat, "Unknown") for cat in filtered_ids]
    return diseases

def map_categories_to_diseases_normal(category_ids, selected_category_id):
    disease_map = {
        0: "Healthy Tooth",
        1: "Caries",
        2: "Cavity",
    }

    # Filter only category_ids that match the selected one
    filtered_ids = [int(cat) for cat in category_ids if int(cat) == selected_category_id]

    # Map to disease names
    diseases = [disease_map.get(cat, "Unknown") for cat in filtered_ids]
    return diseases


@app.post("/predict/model1")
async def predictModel1(file: UploadFile = File(...)):
    """Accepts an image file, processes it through Mask R-CNN, and returns top 2 results without labels."""
    image_bytes = await file.read()
    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    image_np = np.array(image)

    outputs = predictor(image_np)
    instances = outputs["instances"].to("cpu")

    if "scores" in instances.get_fields():
        scores = instances.scores
        topk = torch.topk(scores, k=min(2, len(scores))).indices
        instances = instances[topk]

    category_ids = instances.pred_classes.numpy()
    predicted_diseases = map_categories_to_diseases(category_ids, 1)
    print(f"Predicted diseases: {predicted_diseases}")
    disease_string = ", ".join(predicted_diseases)
    if "pred_classes" in instances.get_fields():
        instances.remove("pred_classes")
    if "scores" in instances.get_fields():
        instances.remove("scores")
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

    return {
        "message": "Prediction complete (Top 2, no labels)",
        "result_image_url": result_url,
        "diseases": disease_string
    }

# Your disease map
disease_map = {
    0: "Healthy Tooth",
    1: "Cavity",
    2: "Fillings",
    3: "Impacted Tooth",
    4: "Implant",
    5: "Infected-teeth"
}

def get_disease_labels(category_ids):
    return [disease_map.get(int(cid), "Unknown") for cid in category_ids]

@app.post("/predict/model2")
async def predictModel2(file: UploadFile = File(...)):
    image_bytes = await file.read()
    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    image_np = np.array(image)

    # Run both models
    outputs1 = predictor(image_np)
    outputs2 = predictor2(image_np)

    instances1 = outputs1["instances"].to("cpu")
    instances2 = outputs2["instances"].to("cpu")

    # Top 2 from Model 1
    scores1 = instances1.scores
    topk_indices = torch.topk(scores1, k=min(2, len(scores1))).indices
    instances1 = instances1[topk_indices]
    keep_mask = ~((instances2.pred_classes == 3) | (instances2.pred_classes == 4))
    instances2 = instances2[keep_mask]
    instances1.remove("scores")
    instances2.remove("scores")

    # Merge
    merged_instances = Instances(image_np.shape[:2])
    merged_instances.pred_boxes = Boxes.cat([instances1.pred_boxes, instances2.pred_boxes])
    merged_instances.pred_classes = torch.cat([instances1.pred_classes, instances2.pred_classes])
    merged_instances.pred_masks = torch.cat([instances1.pred_masks, instances2.pred_masks])

    # Disease label mapping
    merged_class_ids = merged_instances.pred_classes.numpy()
    disease_labels = get_disease_labels(merged_class_ids)

    # Custom Metadata
    custom_metadata = MetadataCatalog.get("custom_dataset")
    num_classes = max(disease_map.keys()) + 1
    full_labels = [disease_map.get(i, f"Class {i}") for i in range(num_classes)]
    custom_metadata.thing_classes = full_labels

    # Visualize
    v = Visualizer(image_np[:, :, ::-1], metadata=custom_metadata, scale=1, instance_mode=ColorMode.IMAGE_BW)
    out = v.draw_instance_predictions(merged_instances)
    result_image = Image.fromarray(out.get_image()[:, :, ::-1])

    # Save and Upload
    local_path = f"{uuid4()}.jpg"
    result_image.save(local_path)
    s3_client.upload_file(local_path, DO_SPACES_BUCKET, local_path, ExtraArgs={"ACL": "public-read"})
    result_url = f"{DO_SPACES_CDN_URL}/{local_path}"

    disease_string = ", ".join(disease_labels)

    return {
        "message": "Merged prediction complete (Top 2 from Model1 + Filtered Model2)",
        "result_image_url": result_url,
        "diseases": disease_string
    }

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
    predicted_diseases = map_categories_to_diseases(category_ids, category_id)
    print(f"Predicted diseases: {predicted_diseases}")  # For debugging
    # Send diseases to LLM for treatment recommendations
    disease_string = ', '.join(predicted_diseases)
    # 🔍 Filter predictions by category
    mask = instances.pred_classes == category_id
    category_instances = instances[mask]

    # 📊 Sort by score and keep top 3
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
    predicted_diseases = map_categories_to_diseases_normal(category_ids, category_id)
    print(f"Predicted diseases: {predicted_diseases}")  # For debugging
    # Send diseases to LLM for treatment recommendations
    disease_string = ', '.join(predicted_diseases)
    # 🔍 Filter predictions by category
    mask = instances.pred_classes == category_id
    category_instances = instances[mask]

    # 📊 Sort by score and keep top 3
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
