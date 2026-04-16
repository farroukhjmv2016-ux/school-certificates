import streamlit as st
import pandas as pd
from PIL import Image, ImageDraw, ImageFont
import io

# ===============================
# PAGE CONFIG (Premium UI)
# ===============================
st.set_page_config(page_title="Certificate Portal", layout="centered")

st.markdown("""
    <style>
    .main {
        background-color: #f5f7fa;
    }
    .title {
        text-align: center;
        font-size: 36px;
        font-weight: bold;
        color: #1f4e79;
    }
    .subtitle {
        text-align: center;
        font-size: 18px;
        color: #555;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="title">🏆 School Certificate Portal</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Enter your Admission Number to download your certificate</div><br>', unsafe_allow_html=True)

# ===============================
# LOAD DATA
# ===============================
@st.cache_data
def load_data():
    df = pd.read_excel("winners.xlsx")
    df["Admission_Number"] = df["Admission_Number"].astype(str)
    return df

data = load_data()

# ===============================
# INPUT (AUTO SUGGEST)
# ===============================
adm_no = st.text_input("🔍 Enter Admission Number")

# Auto-suggestions
if adm_no:
    suggestions = data[data["Admission_Number"].str.contains(adm_no)]
    
    if not suggestions.empty:
        selected = st.selectbox(
            "Select your record",
            suggestions["Admission_Number"] + " - " + suggestions["Name"]
        )
        
        selected_adm = selected.split(" - ")[0]
        user = data[data["Admission_Number"] == selected_adm].iloc[0]

        st.info(f"Name: {user['Name']} | Class: {user['Class']}")

        if st.button("🎓 Generate Certificate"):

            # ===============================
            # LOAD TEMPLATE
            # ===============================
            image = Image.open("certificate_template.jpeg")
            draw = ImageDraw.Draw(image)

            try:
                font_name = ImageFont.truetype("arial.ttf", 40)   # bigger font for name
                font_class = ImageFont.truetype("arial.ttf", 40)  # slightly smaller for class
            except:
                font_name = ImageFont.load_default()
                font_class = ImageFont.load_default()

            # ===============================
            # VALUES
            # ===============================
            values = {
                "NAME": user["Name"],
                "CLASS": user["Class"]
            }

            # ===============================
            # DRAW TEXT (ALIGN TO LINES)
            # ===============================
            # Adjust these Y positions to match your dashed and solid lines
            y_name_line = 370   # <-- replace with dashed line Y coordinate
            y_class_line = 415  # <-- replace with solid line Y coordinate

            # Center NAME on dashed line
            bbox_name = draw.textbbox((0,0), values["NAME"], font=font_name)
            name_width = bbox_name[2] - bbox_name[0]
            x_name = (image.width - name_width) // 2
            draw.text((x_name, y_name_line), values["NAME"], font=font_name, fill="black")

            # Center CLASS on solid line
            bbox_class = draw.textbbox((0,0), values["CLASS"], font=font_class)
            class_width = bbox_class[2] - bbox_class[0]
            x_class = (image.width - class_width) // 2
            draw.text((x_class, y_class_line), values["CLASS"], font=font_class, fill="black")

            # ===============================
            # DOWNLOAD
            # ===============================
            buf = io.BytesIO()
            image.save(buf, format="JPEG")
            byte_im = buf.getvalue()

            st.success("✅ Certificate Generated Successfully!")

            st.download_button(
                label="📥 Download Certificate",
                data=byte_im,
                file_name=f"Certificate_{selected_adm}.jpeg",
                mime="image/png"
            )

    else:
        st.error("❌ No matching record found")
