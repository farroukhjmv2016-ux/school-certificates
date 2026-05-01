import streamlit as st
import pandas as pd
from PIL import Image, ImageDraw, ImageFont
import io

# ===============================
# PAGE CONFIG
# ===============================
st.set_page_config(page_title="Certificate Portal", layout="centered")

# ===============================
# ADVANCED UI STYLING (CSS)
# ===============================
# ===============================
# FINAL OVERRIDE UI STYLING (CSS)
# ===============================
st.markdown("""
    <style>
    /* 1. FORCE HIDE ALL STREAMLIT OVERLAYS */
    header, [data-testid="stHeader"], .stAppHeader, #MainMenu, footer {
        visibility: hidden !important;
        height: 0 !important;
        display: none !important;
    }
    
    /* Target the specific toolbar at the bottom right/left */
    [data-testid="stStatusWidget"], [data-testid="stToolbar"], .st-emotion-cache-18ni7ap {
        display: none !important;
    }

    /* Target the specific 'Manage app' button container if it persists */
    div[class^="st-emotion-cache"] > button[title="Manage app"] {
        display: none !important;
    }

    /* 2. Main background */
    .stApp {
        background-color: #f8f9fa;
    }
    
    /* 3. Title Styling */
    .main-title {
        text-align: center;
        font-size: 38px;
        font-weight: 800;
        color: #1a365d;
        margin-top: -100px; /* Pulls content up since the header is removed */
    }
    
    .main-subtitle {
        text-align: center;
        font-size: 16px;
        color: #4a5568;
        margin-bottom: 30px;
    }

    /* 4. HOVER REVEAL FOOTER */
    .hover-footer {
        position: fixed;
        bottom: 0;
        left: 0;
        width: 100%;
        background-color: rgba(255, 255, 255, 0.95);
        border-top: 1px solid #e2e8f0;
        text-align: center;
        z-index: 999;
        transition: all 0.4s ease-in-out;
        height: 5px; 
        padding: 0;
        overflow: hidden;
        opacity: 0.3;
    }
    
    .hover-footer:hover {
        height: 60px; 
        padding: 10px 0;
        opacity: 1;
        box-shadow: 0 -5px 15px rgba(0,0,0,0.05);
    }
    
    .brand-text {
        font-weight: 700;
        color: #2b6cb0;
        margin: 0;
        font-size: 14px;
    }
    
    .copyright-text {
        font-size: 11px;
        color: #718096;
        margin: 0;
    }

    /* 5. Professional Button */
    div.stButton > button {
        width: 100%;
        border-radius: 6px;
        background-color: #2b6cb0;
        color: white;
        border: none;
        height: 3em;
        font-weight: 600;
    }
    
    div.stButton > button:hover {
        background-color: #1a365d !important;
        color: white !important;
    }

    .content-spacer {
        margin-bottom: 80px;
    }
    </style>
""", unsafe_allow_html=True)
# App Headers
st.markdown('<div class="main-title">Jain Bharati Mrigavati Vidyalaya</div>', unsafe_allow_html=True)
st.markdown('<div class="main-subtitle">🏆 Certificate Download Portal</div>', unsafe_allow_html=True)
#st.markdown('<div class="main-subtitle">Official School Recognition System</div>', unsafe_allow_html=True)

# ===============================
# DATA LOGIC
# ===============================
@st.cache_data
def load_data():
    try:
        df = pd.read_excel("winners.xlsx")
        df["Admission_Number"] = df["Admission_Number"].astype(str)
        return df
    except:
        return pd.DataFrame()

data = load_data()

if data.empty:
    st.error("⚠️ Data source 'winners.xlsx' not found.")
else:
    adm_no = st.text_input("🔍 Enter Admission Number", placeholder="Type here...")

    if adm_no:
        suggestions = data[data["Admission_Number"].str.contains(adm_no, na=False)]
        
        if not suggestions.empty:
            selected = st.selectbox(
                "Verify Details",
                suggestions["Admission_Number"] + " - " + suggestions["Name"]
            )
            
            selected_adm = selected.split(" - ")[0]
            user = data[data["Admission_Number"] == selected_adm].iloc[0]

            st.info(f"**Record Found:** {user['Name'].title()} | **Class:** {user['Class']}")

            if st.button("Generate Certificate"):
                with st.spinner("Processing..."):
                    try:
                        image = Image.open("certificate_template.jpeg")
                        draw = ImageDraw.Draw(image)
                    except:
                        st.error("Template file missing.")
                        st.stop()

                    try:
                        font_name = ImageFont.truetype("fonts/AlexBrush-Regular.ttf", 44)
                        font_class = ImageFont.truetype("fonts/arial.ttf", 32)
                    except:
                        font_name = ImageFont.load_default()
                        font_class = ImageFont.load_default()

                    # CAPITALIZATION LOGIC
                    raw_name = str(user["Name"]).strip()
                    formatted_name = " ".join([word.capitalize() for word in raw_name.split()])
                    
                    # COORDINATES
                    y_name_line, y_class_line, x_offset = 370, 415, -100 

                    bbox_name = draw.textbbox((0,0), formatted_name, font=font_name)
                    x_name = (image.width - (bbox_name[2] - bbox_name[0])) // 2 + x_offset
                    draw.text((x_name, y_name_line), formatted_name, font=font_name, fill="black")

                    cls_str = str(user["Class"]).upper()
                    bbox_class = draw.textbbox((0,0), cls_str, font=font_class)
                    x_class = (image.width - (bbox_class[2] - bbox_class[0])) // 2 + x_offset
                    draw.text((x_class, y_class_line), cls_str, font=font_class, fill="black")

                    buf = io.BytesIO()
                    image.save(buf, format="JPEG", quality=95)
                    byte_im = buf.getvalue()

                    # FIX: Replaced use_container_width with width="stretch"
                    st.image(byte_im, caption="Certificate Preview", width="stretch")

                    st.download_button(
                        label="📥 Download JPG",
                        data=byte_im,
                        file_name=f"Certificate_{selected_adm}.jpg",
                        mime="image/jpeg"
                    )
        else:
            st.warning("No records found.")

st.markdown('<div class="content-spacer"></div>', unsafe_allow_html=True)

# ===============================
# HOVER REVEAL BRANDING FOOTER
# ===============================
st.markdown("""
    <div class="hover-footer">
        <p class="brand-text">🚀 Farry-Tech Softwares</p>
        <p class="copyright-text">Copyrights @ Farroukh Nadim</p>
    </div>
""", unsafe_allow_html=True)
