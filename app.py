import streamlit as st
import requests
from PIL import Image
import io
import re

# ----------------------------------------------------
# PAGE CONFIG
# ----------------------------------------------------
st.set_page_config(page_title="Wildlife Guardian", layout="wide")

# ----------------------------------------------------
# CSS — PREMIUM STYLING
# ----------------------------------------------------
st.markdown("""
<style>
/* ---- Animated gradient background ---- */
body {
    background: linear-gradient(270deg, #0f0c29, #302b63, #24243e, #0f0c29);
    background-size: 800% 800%;
    animation: gradientBG 20s ease infinite;
    color: #e8ffe9;
    margin: 0;
}
@keyframes gradientBG {
    0%{background-position:0% 50%}
    50%{background-position:100% 50%}
    100%{background-position:0% 50%}
}

/* ---- GLASS CARD ---- */
.card {
    background: rgba(255, 255, 255, 0.05);
    border-radius: 25px;
    padding: 30px;
    border: 1px solid rgba(0,255,120,0.2);
    box-shadow: 0 8px 30px rgba(0,255,120,0.2);
    backdrop-filter: blur(15px);
    transition: all 0.3s ease;
    margin-bottom: 20px;
}
.card:hover {
    transform: translateY(-8px) scale(1.02);
    box-shadow: 0 12px 40px rgba(0,255,120,0.5);
}

/* ---- HEADER TEXT ---- */
.title-text {
    font-size: 70px !important;
    font-weight: 900 !important;
    background: linear-gradient(90deg, #00ff88, #00e676, #00bfa5, #00ff88);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    animation: shine 3s linear infinite;
    text-align: center;
    margin-bottom: 5px;
}
@keyframes shine {
    0%{background-position:0%}
    50%{background-position:100%}
    100%{background-position:0%}
}

/* ---- SUBHEADERS ---- */
h3, h2, .stMarkdown {
    color: #e8ffe9 !important;
    font-weight: 600 !important;
}

/* ---- FOOTER ---- */
.footer-text {
    color: #5aff78;
    font-weight: 600;
    text-align: center;
    font-size: 14px;
    margin-top: 50px;
}

/* ---- MODERN BUTTON ---- */
.stButton>button {
    background: linear-gradient(90deg, #00e676, #00c853);
    color: #000 !important;
    border-radius: 20px;
    padding: 16px 32px;
    font-size: 18px;
    font-weight: 700;
    border: none;
    cursor: pointer;
    transition: all 0.3s ease;
}
.stButton>button:hover {
    transform: scale(1.08);
    background: linear-gradient(90deg, #69f0ae, #00ff88);
    box-shadow: 0 0 20px #00ff88;
}
</style>
""", unsafe_allow_html=True)

# ----------------------------------------------------
# HEADER
# ----------------------------------------------------
st.markdown("<h1 class='title-text'>🦁 Wildlife Guardian</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; font-size:22px; color:#8aff9d; margin-top:0;'>AI-powered wildlife monitoring & threat detection</p>", unsafe_allow_html=True)

# ----------------------------------------------------
# LAYOUT — left: preview/output, right: upload
# ----------------------------------------------------
left, right = st.columns([2.5, 1.2], gap="large")

# ------------------- RIGHT PANEL -------------------
with right:
    st.markdown("### 📤 Upload Image")
    uploaded_file = st.file_uploader("Choose an image", type=["jpg", "jpeg", "png"])
    analyse_clicked = st.button("🔍 Analyse")

# ------------------- LEFT PANEL -------------------
with left:
    st.markdown("### 🖼 Image Preview & Analysis Output")
    img_bytes, img = None, None

    if uploaded_file:
        img_bytes = uploaded_file.getvalue()
        img = Image.open(io.BytesIO(img_bytes))

        # Show original file size warning
        size_mb = len(img_bytes) / (1024*1024)
        if size_mb > 5:
            st.warning(f"⚠ Uploaded image is {size_mb:.2f} MB — resizing and compressing for faster analysis.")

        # Resize if larger than 1024px
        MAX_DIM = 1024
        if max(img.size) > MAX_DIM:
            img.thumbnail((MAX_DIM, MAX_DIM))

        # Convert to RGB
        if img.mode != "RGB":
            img = img.convert("RGB")

        # Compress to JPEG
        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=75, optimize=True)
        img_bytes = buf.getvalue()

        st.image(img, width=800, clamp=True)
    else:
        st.info("ℹ No image uploaded yet.")

    # ------------------- ANALYZE BUTTON -------------------
    if analyse_clicked:
        if img_bytes:
            with st.spinner("🧠 Analyzing image…"):
                try:
                    files = {"file": ("image.jpg", img_bytes)}
                    response = requests.post("http://127.0.0.1:5000/analyze", files=files)
                    if response.status_code == 200:
                        st.success("✅ Analysis Complete")

                        # Parse lines and add colors + round confidence score
                        output_text = response.text.split("\n")
                        html_content = '<div class="card" style="font-family: monospace; font-size:16px;">'
                        for line in output_text:
                            # Shorten confidence score
                            if "'score':" in line:
                                match = re.search(r"'score':\s*([\d\.]+)", line)
                                if match:
                                    score = float(match.group(1))
                                    line = line.replace(match.group(1), f"{score:.2f}")

                            if "Detected Human ID" in line or "Risk Score" in line:
                                html_content += f'<span style="color:#ff4d6d; font-weight:700;">{line}</span><br>'
                            elif "Face Match" in line:
                                html_content += f'<span style="color:#00ff88;">{line}</span><br>'
                            elif "Weapon" in line or "Vehicle" in line:
                                html_content += f'<span style="color:#00bfff;">{line}</span><br>'
                            elif "Distance" in line:
                                html_content += f'<span style="color:#ffcc00;">{line}</span><br>'
                            else:
                                html_content += f'{line}<br>'
                        html_content += '</div>'

                        st.markdown(html_content, unsafe_allow_html=True)

                    else:
                        st.error(f"⚠ Backend Error: {response.status_code}")
                        st.code(response.text)
                except Exception as e:
                    st.error(f"⚠ Error: {e}")
        else:
            st.error("❗ Please upload an image first")

# ----------------------------------------------------
# FOOTER
# ----------------------------------------------------
from datetime import datetime
import streamlit as st

current_year = datetime.now().year

st.markdown(
    f"<p class='footer-text'>© {current_year} Wildlife Guardian Project</p>",
    unsafe_allow_html=True
)
# st.markdown("<p class='footer-text'>© 2025 Wildlife Guardian Project</p>", unsafe_allow_html=True)
