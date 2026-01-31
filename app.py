import streamlit as st
import google.generativeai as genai
from PIL import Image
import os
# We don't need dotenv for Cloud, but good to keep for local testing
try:
    from dotenv import load_dotenv
    load_dotenv()
except:
    pass

# Page Config
st.set_page_config(
    page_title="Alt-Text Automator",
    page_icon="👁️",
    layout="centered"
)

# --- 1. SETUP & AUTH (INVISIBLE MODE) ---
st.title("👁️ Alt-Text Automator")
st.markdown("Generates SEO-friendly and Accessible description tags for your images.")

# Try to get key from Streamlit Secrets (Cloud) OR Local Environment
api_key = None

if "GEMINI_API_KEY" in st.secrets:
    api_key = st.secrets["GEMINI_API_KEY"]
elif os.getenv("GEMINI_API_KEY"):
    api_key = os.getenv("GEMINI_API_KEY")

with st.sidebar:
    st.header("⚙️ Configuration")
    
    # Status Indicator
    if api_key:
        st.success("✅ System Connected")
    else:
        st.error("❌ No API Key found")
        st.info("If you are the admin, please add GEMINI_API_KEY to your Secrets.")
        # Fallback for manual entry if secrets fail
        api_key = st.text_input("Manual Key Entry (Debug)", type="password")

    st.markdown("---")
    st.markdown("### 🛠️ Settings")
    mode = st.radio("Optimization Goal:", ["Accessibility (Standard)", "SEO (Marketing)"])

# --- 2. THE LOGIC ---
def generate_alt_text(image, context, mode, api_key):
    try:
        genai.configure(api_key=api_key)
        # Using the Lite model we verified works
        model = genai.GenerativeModel('gemini-2.5-flash-lite')
        
        # Dynamic Prompting based on Mode
        if mode == "SEO (Marketing)":
            task = f"""
            Analyze this image and write an Alt Text description optimized for SEO.
            Context/Keywords provided by user: '{context}'
            
            RULES:
            1. Incorporate the context keywords naturally.
            2. Keep it under 125 characters.
            3. Do not start with "Image of" or "Photo of".
            4. Be descriptive but focused on the keyword topic.
            """
        else:
            task = """
            Analyze this image and write a functional Alt Text description for a screen reader.
            
            RULES:
            1. Focus on what is visually happening for a blind user.
            2. Keep it under 125 characters.
            3. Do not start with "Image of" or "Photo of".
            4. Be strictly factual.
            """

        response = model.generate_content([task, image])
        return response.text
    except Exception as e:
        return f"Error: {str(e)}"

# --- 3. THE UI ---
uploaded_file = st.file_uploader("Upload an Image (JPG, PNG, WEBP)", type=["jpg", "jpeg", "png", "webp"])

if uploaded_file:
    # Display the image
    image = Image.open(uploaded_file)
    st.image(image, caption="Preview", use_container_width=True)
    
    # Context Input (Only show if relevant)
    context_text = ""
    if mode == "SEO (Marketing)":
        context_text = st.text_input("Focus Keyword / Context (Optional)", placeholder="e.g., 'Luxury leather bag' or 'Office meeting'")

    # Action Button
    if st.button("✨ Generate Alt Text", type="primary"):
        if not api_key:
            st.error("System is missing API credentials.")
        else:
            with st.spinner("Analyzing pixels..."):
                result = generate_alt_text(image, context_text, mode, api_key)
                
                # Success Display
                st.success("Generated Successfully!")
                st.code(result, language="text")
                st.caption(f"Character count: {len(result)}")

else:
    st.info("👆 Upload an image to get started.")

# Footer
st.markdown("---")

st.markdown("Made with a lot of ☕ by Ibrahim Samir")
