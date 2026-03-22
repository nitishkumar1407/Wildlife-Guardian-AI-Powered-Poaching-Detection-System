# Wildlife Guardian – AI Powered Poaching Detection

An AI-based wildlife protection system that detects potential poachers and identifies individuals using **computer vision and face recognition**.
The project combines **YOLO object detection**, **FaceNet face recognition**, and a **Streamlit interface** to analyze uploaded images and assist wildlife surveillance.

---

## Features

* AI-based **poacher detection**
* **Face recognition** using FaceNet
* **Object detection** using YOLO
* Image upload and analysis
* Interactive **Streamlit dashboard**

---

## Tech Stack

* Python
* PyTorch
* YOLO (Ultralytics)
* FaceNet + MTCNN
* OpenCV
* NumPy
* Scikit-learn
* Streamlit

---

## Project Structure

```
Wildlife-Guardian-AI-Powered-Poaching-Detection-System
│
├── app.py                # Streamlit application
├── model/                # AI models and detection logic
├── backend/              # backend processing
├── known_faces/          # dataset of known individuals
├── uploads/              # uploaded images
├── build_db.py           # face database builder
├── requirements.txt
└── README.md
```

---

## Installation

Clone the repository

```
git clone https://github.com/nitishkumar1407/Wildlife-Guardian-AI-Powered-Poaching-Detection-System.git
```

```
cd Wildlife-Guardian-AI-Powered-Poaching-Detection-System
```

Create virtual environment

```
python -m venv venv
```

Activate environment

Mac / Linux

```
source venv/bin/activate
```

Install dependencies

```
pip install -r requirements.txt
```

---

## Run the Application

```
streamlit run app.py
```

The app will start at:

```
http://localhost:8501
```

---

## Face Database

Images of known individuals should be stored in:

```
known_faces/
```

Generate embeddings using:

```
python build_db.py
```

---

## Future Improvements

* Real-time CCTV monitoring
* Drone-based wildlife surveillance
* Weapon detection integration
* Automated alert system




