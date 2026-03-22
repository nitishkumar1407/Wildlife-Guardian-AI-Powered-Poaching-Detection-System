import torch
from ultralytics import YOLO
from facenet_pytorch import MTCNN, InceptionResnetV1
from PIL import Image
import numpy as np
import cv2
from sklearn.metrics.pairwise import cosine_similarity
import os

# ===================================================
# PATH SETTINGS
# ===================================================
BASE_DIR = os.path.dirname(__file__)                         # /Project/model
MODEL_WEIGHTS = os.path.join(BASE_DIR, "best.pt")            # /Project/model/best.pt
EMB_PATH = os.path.join(BASE_DIR, "known_embeddings.npy")    # /Project/model/known_embeddings.npy

# ===================================================
# DEVICE + MODELS
# ===================================================
device = torch.device("cpu")

# Load YOLO model from same folder
yolo_model = YOLO(MODEL_WEIGHTS)

# Load MTCNN + FaceNet
mtcnn = MTCNN(image_size=160, margin=20, keep_all=True)
facenet = InceptionResnetV1(pretrained="vggface2").eval().to(device)

# ===================================================
# LOAD KNOWN EMBEDDINGS
# ===================================================
known_db = np.load(EMB_PATH, allow_pickle=True).item()


# ===================================================
# FACE EMBEDDING FUNCTION
# ===================================================
def get_embedding(face_img):
    face = mtcnn(face_img)
    if face is None:
        return None

    if face.ndim == 3:
        face = face.unsqueeze(0)

    with torch.no_grad():
        emb = facenet(face.to(device)).cpu().numpy()

    emb = emb / np.linalg.norm(emb)
    return emb


# ===================================================
# FACE IDENTIFICATION
# ===================================================
def recognize_face(face_img):
    emb = get_embedding(face_img)
    if emb is None:
        return "Unknown", 0.0

    best_name = "Unknown"
    best_score = -1
    best_dist = 999

    for name, ref_emb in known_db.items():
        sim = cosine_similarity(emb, ref_emb.reshape(1, -1))[0][0]
        dist = 1 - sim

        if dist < best_dist:
            best_dist = dist
            best_score = sim
            best_name = name

    # decision threshold
    if best_dist > 0.35:
        return "Unknown", best_score

    return best_name, best_score


# ===================================================
# PROCESS IMAGE (JSON OUTPUT FOR FLASK)
# ===================================================
def process_image_json(img_path):
    img = Image.open(img_path).convert("RGB")
    results = yolo_model(img_path)[0]
    class_map = yolo_model.names

    humans = []
    weapons = []
    vehicles = []
    animals = []

    # Collect object detections
    for box in results.boxes:
        cls_id = int(box.cls.cpu().numpy())
        label = class_map[cls_id]
        x1, y1, x2, y2 = map(int, box.xyxy[0].cpu().numpy())

        if label == "human":
            humans.append((x1, y1, x2, y2))
        elif label == "weapon":
            weapons.append((x1, y1, x2, y2))
        elif label == "vehicle":
            vehicles.append((x1, y1, x2, y2))
        elif label == "animal":
            animals.append((x1, y1, x2, y2))

    # Recognize faces
    final_results = []
    for (x1, y1, x2, y2) in humans:
        person_crop = img.crop((x1, y1, x2, y2))
        name, score = recognize_face(person_crop)
        final_results.append({"name": name, "score": float(score)})

    # Alert conditions
    unknown_found = any(r["name"] == "Unknown" for r in final_results)
    known_found = any(r["name"] != "Unknown" for r in final_results)
    weapon_found = len(weapons) > 0

    alert_level = "LOW"
    alert_reason = "Normal"

    if unknown_found and weapon_found:
        alert_level = "HIGH"
        alert_reason = "Unknown person WITH weapon detected!"
    elif unknown_found:
        alert_level = "MEDIUM"
        alert_reason = "Unknown person detected."
    elif weapon_found and known_found:
        alert_level = "MEDIUM"
        alert_reason = "Weapon detected near known ranger."
    elif weapon_found:
        alert_level = "MEDIUM"
        alert_reason = "Weapon detected."

    return {
        "alert_level": alert_level,
        "reason": alert_reason,
        "humans": final_results,
        "weapons": len(weapons),
        "vehicles": len(vehicles),
        "animals": len(animals)
    }


# ===================================================
# MAIN (optional)
# ===================================================
if __name__ == "__main__":
    print("Model loaded successfully.")
