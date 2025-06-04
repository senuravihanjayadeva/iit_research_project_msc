import boto3
import os

# DigitalOcean Spaces credentials and settings
DO_SPACES_KEY = "DO00UXDWZZ8E9G4CU6BM"
DO_SPACES_SECRET = "zIAE1vRUKw7d2zbZ8on6/G935949XLI/VpTyVmAQmL0"
DO_SPACES_REGION = "tor1"  # Example: "nyc3"
DO_SPACES_BUCKET = "iitresearchsenura"
DO_SPACES_CDN_URL = "https://iitresearchsenura.tor1.digitaloceanspaces.com"  # Example: https://your-bucket.nyc3.cdn.digitaloceanspaces.com
DO_SPACES_FOLDER = "models/"  # Folder inside the bucket to download from
LOCAL_DOWNLOAD_DIR = "/root/projects/backend"  # Destination on your VM

# Initialize the S3 client (Spaces is S3-compatible)
s3 = boto3.client(
    's3',
    region_name=DO_SPACES_REGION,
    endpoint_url=f"https://{DO_SPACES_REGION}.digitaloceanspaces.com",
    aws_access_key_id=DO_SPACES_KEY,
    aws_secret_access_key=DO_SPACES_SECRET
)

# Ensure the local directory exists
os.makedirs(LOCAL_DOWNLOAD_DIR, exist_ok=True)

# List and download all files in the folder
response = s3.list_objects_v2(Bucket=DO_SPACES_BUCKET, Prefix=DO_SPACES_FOLDER)

if "Contents" not in response:
    print(f"No files found in folder: {DO_SPACES_FOLDER}")
else:
    for item in response["Contents"]:
        key = item["Key"]
        if key.endswith("/"):  # skip subfolders or empty keys
            continue

        file_name = os.path.basename(key)
        local_path = os.path.join(LOCAL_DOWNLOAD_DIR, file_name)
        print(f"✅ local_path: {local_path}")
        try:
            s3.download_file(DO_SPACES_BUCKET, key, local_path)
            print(f"✅ Downloaded: {file_name}")
        except Exception as e:
            print(f"❌ Failed to download {file_name}: {e}")
