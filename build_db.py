import os
import numpy as np
from PIL import Image
import torch
from facenet_pytorch import MTCNN, InceptionResnetV1

# =====================================
# MODELS
# =====================================
device = torch.device("cpu")
mtcnn = MTCNN(image_size=160, margin=20)
facenet = InceptionResnetV1(pretrained="vggface2").eval().to(device)

KNOWN_DIR = "known_faces"   # folder that contains ranger folders

# =====================================
# FUNCTION TO GET EMBEDDING
# =====================================
def get_embedding(img):
    face = mtcnn(img)
    if face is None:
        return None
    if face.ndim == 3:
        face = face.unsqueeze(0)

    with torch.no_grad():
        emb = facenet(face.to(device)).cpu().numpy()

    emb = emb / np.linalg.norm(emb)
    return emb.reshape(-1)

# =====================================
# BUILD DATABASE
# =====================================
db = {}

for person in os.listdir(KNOWN_DIR):
    person_folder = os.path.join(KNOWN_DIR, person)

    if not os.path.isdir(person_folder):
        continue

    embeddings = []

    for file in os.listdir(person_folder):
        if file.lower().endswith((".jpg", ".jpeg", ".png")):
            img_path = os.path.join(person_folder, file)
            img = Image.open(img_path).convert("RGB")

            emb = get_embedding(img)
            if emb is not None:
                embeddings.append(emb)

    if len(embeddings) > 0:
        db[person] = np.mean(embeddings, axis=0)

# =====================================
# SAVE DATABASE
# =====================================
np.save("known_embeddings.npy", db)

print("DONE! known_embeddings.npy created successfully.")
