import os
import streamlit as st
import requests
import pandas as pd
from PIL import Image
from pdf_generator import generate_pdf_report

# Page Config
st.set_page_config(
    page_title="Advanced AI Medical Intelligence Platform",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>

/* Hide Streamlit menu and footer */
#MainMenu {
    visibility: hidden;
}

footer {
    visibility: hidden;
}

/* Main page padding */
.block-container{
    max-width: 1300px;
    margin: auto;
    padding-top: 3rem;
    padding-bottom: 1rem;
}

/* Card */
.card{
    background:#1E1E1E;
    border-radius:18px;
    padding:18px;
    border:1px solid #31333F;
    margin-bottom:15px;
}

/* Dashboard title */
.title{
    font-size:30px;
    font-weight:700;
    color:white;
}

/* Subtitle */
.subtitle{
    color:#A6A6A6;
    font-size:15px;
}

/* Prediction */
.prediction{
    font-size:30px;
    font-weight:bold;
    color:#00E676;
}

/* Section title */
.section-title{
    font-size:26px;
    font-weight:bold;
    color:white;
}

</style>
""", unsafe_allow_html=True)

with st.sidebar:

    st.image(
        "https://img.icons8.com/color/96/stethoscope.png",
        width=80
    )

    st.title("AI Medical Platform")

    st.divider()

    with st.container(border=True):
        st.markdown("### 🧠 Model")
        st.write("EfficientNetB0")

    with st.container(border=True):
        st.markdown("### 🔥 Explainability")
        st.write("Grad-CAM")

    with st.container(border=True):
        st.markdown("### 🤖 LLM")
        st.write("Groq (Llama 3.3 70B)")

    with st.container(border=True):
        st.markdown("### 🗄️ Database")
        st.write("SQLite")

    st.divider()

    st.caption("Version 1.0")

# Title
left, center, right = st.columns([1, 8, 1])

with center:

    st.markdown("""
    <div class="card">

    <div class="title">
    🩺 Advanced AI Medical Intelligence Platform
    </div>

    <div class="subtitle">
    AI-powered Chest X-ray Analysis using Deep Learning,
    Explainable AI and Large Language Models
    </div>

    </div>
    """, unsafe_allow_html=True)

# Tabs
# Center the tabs
left, center, right = st.columns([2, 6, 2])
with center:
    tab1, tab2, tab3 = st.tabs([
        "🔍 Analysis",
        "📜 Prediction History",
        "ℹ️ About"
    ])

# TAB 1 - ANALYSIS

with tab1:
    # Center the upload card
    left, center, right = st.columns([1, 9, 1])
    with center:
        with st.container(border=True):

            st.markdown(
                "## 📤 Upload Chest X-ray"
            )

            st.caption(
                "Upload a Chest X-ray (JPG, JPEG or PNG) to generate an AI-assisted diagnosis."
            )

            st.write("")

            uploaded_file = st.file_uploader(
                "Choose Chest X-ray Image",
                type=["jpg", "jpeg", "png"],
                label_visibility="collapsed",
                width="stretch"
            )

    if uploaded_file is not None:
        st.success("✅ Image uploaded successfully")

        if st.button(
            "🩺 Predict Disease",
            use_container_width=True
        ):
            image = Image.open(uploaded_file)

            files = {
                "image": (
                    uploaded_file.name,
                    uploaded_file.getvalue(),
                    uploaded_file.type
                )
            }

            with st.spinner("🔍 Analyzing Chest X-ray..."):

                response = requests.post(
                    "http://127.0.0.1:5000/predict",
                    files=files
                )

                result = response.json()

                prediction = result["prediction"]
                confidence = result["confidence"]
                gradcam_image = result["gradcam_image"]
                medical_report = result["medical_report"]
                
                # Image Layout
                image_col, gradcam_col = st.columns(2)
                with image_col:

                    st.subheader("🩻 Uploaded X-ray")
                    st.image(
                        image,
                        use_container_width=True
                    )

                # LEFT
                metric1, metric2, metric3 = st.columns(3)
                # Prediction
                with metric1:
                    st.metric(
                        label="Prediction",
                        value=prediction
                    )

                # Confidence
                with metric2:
                    st.metric(
                        label="Confidence",
                        value=f"{confidence}%"
                    )

                # Risk level
                with metric3:
                    if confidence >= 95:
                        risk = "High"

                    elif confidence >= 80:
                        risk = "Medium"

                    else:
                        risk = "Low"

                    st.metric(
                        label="Risk Level",
                        value=risk
                    )
                

                # RIGHT
                with gradcam_col:

                    st.subheader("🔥 Grad-CAM")

                    st.image(
                        gradcam_image,
                        use_container_width=True
                    )

                st.subheader("🤖 AI Medical Report")

                st.write(medical_report)

                # Generate PDF

                pdf_path = generate_pdf_report(
                    filename=uploaded_file.name,
                    prediction=prediction,
                    confidence=confidence,
                    medical_report=medical_report
                )

                # Download Button

                with open(pdf_path, "rb") as pdf_file:

                    st.download_button(
                        label="📄 Download Medical Report",
                        data=pdf_file,
                        file_name=os.path.basename(pdf_path),
                        mime="application/pdf"
                    )

# TAB 2 - HISTORY

with tab2:

    st.subheader("📜 Prediction History")

    try:

        history_response = requests.get(
            "http://127.0.0.1:5000/history"
        )

        history = history_response.json()

        if len(history) > 0:

            df = pd.DataFrame(history)

            df = df[
                [
                    "created_at",
                    "filename",
                    "prediction",
                    "confidence"
                ]
            ]

            df.columns = [
                "Date",
                "Filename",
                "Prediction",
                "Confidence (%)"
            ]

            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True
            )

        else:

            st.info("No prediction history available.")

    except Exception as e:

        st.error(f"Unable to load prediction history: {e}")

# TAB 3 - ABOUT
with tab3:

    st.subheader("ℹ️ About This Project")

    st.markdown("""
### 🩺 Advanced AI Medical Intelligence Platform

This application uses **Artificial Intelligence** to analyze Chest X-ray images and assist in identifying potential cases of pneumonia.

---

### 🚀 Technologies Used

- 🧠 EfficientNetB0
- 🔥 Grad-CAM Explainable AI
- 🤖 Groq LLM (Llama 3.3 70B)
- 🌐 Flask REST API
- 🎨 Streamlit Dashboard
- 🗄 SQLite Database
- 🐍 Python

---

### 📊 Model Performance

- Validation Accuracy: **95.49%**
- Binary Classification:
  - NORMAL
  - PNEUMONIA
- AI-generated Medical Report
- Explainable Predictions using Grad-CAM

---

### 🔄 Project Workflow

1. Upload Chest X-ray
2. AI predicts disease
3. Grad-CAM highlights important regions
4. Groq generates a medical report
5. Prediction stored in SQLite
6. View prediction history

---

### ⚠ Disclaimer

This application is intended **only for educational and research purposes**.

It should **not** be used as a substitute for professional medical diagnosis or clinical decision-making.
""")