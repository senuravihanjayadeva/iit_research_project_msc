Before
---------
Download the model file and add it under backend folder

Steps
---------
1) Create a GPU Droplet  - Digital Ocean
2) Access to VM by ssh - ssh root@public-ip
3) mkdir projects to create a folder 
4) From Local Machine Terminal use this command to copy files ( Not From VM )
   scp -r backend root@public-ip:/root/projects/
5) Go to vm root. Then give command -> apt install python3-pip
6) pip install "fastapi[standard]"
7) pip install torch torchaudio torchvision
8) pip install git+https://github.com/facebookresearch/detectron2.git
9) Now go to projects/backend and run this -> pip install -r requirements.txt
10) Now run -> python3 download_from_space.py
10) To Run project -> uvicorn main:app --host 0.0.0.0 --port 8000



