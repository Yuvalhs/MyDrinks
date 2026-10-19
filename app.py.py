import streamlit as st
import pandas as pd
import os
from datetime import datetime

st.set_page_config(page_title="My Spirits Journal", layout="wide", initial_sidebar_state="expanded")

DATA_FILE = "spirits_database.csv"

# טעינת נתונים קיימים או יצירת DataFrame חדש
if 'database' not in st.session_state:
    if os.path.exists(DATA_FILE):
        st.session_state.database = pd.read_csv(DATA_FILE)
    else:
        st.session_state.database = pd.DataFrame()

if 'cask_stages' not in st.session_state:
    st.session_state.cask_stages = 1

def add_cask_stage():
    st.session_state.cask_stages += 1

st.title("🥃 My Spirits Journal")

tab1, tab2 = st.tabs(["📝 Add New Bottle", "📚 My Collection"])

with tab1:
    st.header("Log a New Tasting")
    
    st.markdown("### 📷 Bottle Image & Scanner")
    uploaded_file = st.file_uploader("Upload or Take Photo of Bottle Label", type=["jpg", "jpeg", "png"])
    
    if uploaded_file:
        st.image(uploaded_file, caption="Uploaded Bottle Label", width=250)
        if st.button("✨ Scan Label (AI Auto-Fill)"):
            st.info("🔹 AI Vision API integration point - scans distillery, ABV, and bottle name.")

    st.divider()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("General Information")
        alc_type = st.selectbox("Alcohol Type", ["Whisky", "Gin", "Rum", "Tequila", "Vodka", "Liqueur", "Beer", "Wine", "Other"])
        
        country = ""
        region = ""
        
        if alc_type == "Whisky":
            whisky_type = st.selectbox("Whisky Type", ["Scotch", "Bourbon / American", "Irish", "Japanese", "Israeli", "Worldwide"])
            if whisky_type == "Scotch":
                region = st.selectbox("Region", ["Islay", "Speyside", "Highlands", "Lowlands", "Campbeltown", "Islands"])
                country = "Scotland"
            elif whisky_type == "Israeli":
                country = "Israel"
            elif whisky_type == "Worldwide":
                country = st.text_input("Country", placeholder="e.g., Taiwan, India")
            else:
                country = whisky_type.split(" / ")[0] if "Bourbon" in whisky_type else whisky_type
        else:
            country = st.text_input("Country")
            
        distillery = st.text_input("Distillery / Brand")
        indie_bottler = st.text_input("Independent Bottler (Optional)")
        bottle_name = st.text_input("Bottle Name / Edition")
        
        st.subheader("Technical Details")
        age = st.text_input("Age (Years or NAS)", value="NAS")
        abv = st.number_input("ABV (%)", min_value=0.0, max_value=100.0, step=0.1, format="%.1f")
        
        st.markdown("**🛢️ Cask History**")
        cask_info = []
        for i in range(st.session_state.cask_stages):
            c1, c2 = st.columns(2)
            with c1:
                ctype = st.text_input(f"Stage {i+1} - Cask Type", key=f"cask_type_{i}", placeholder="e.g., Ex-Bourbon")
            with c2:
                cdur = st.text_input(f"Stage {i+1} - Duration", key=f"cask_dur_{i}", placeholder="e.g., 12 Years")
            if ctype:
                cask_info.append(f"{ctype} ({cdur})" if cdur else ctype)
        
        st.button("➕ Add Cask Stage", on_click=add_cask_stage)
        
    with col2:
        st.subheader("Tasting Notes")
        nose = st.text_area("Nose (Aroma)", height=80)
        palate = st.text_area("Palate (Taste)", height=80)
        finish = st.text_area("Finish", height=80)
        
        st.subheader("🕸️ Flavor Profile (1-5)")
        f1 = st.slider("Intensity / Peat", 1, 5, 1)
        f2 = st.slider("Sweetness", 1, 5, 3)
        f3 = st.slider("Fruity / Floral", 1, 5, 3)
        f4 = st.slider("Spicy / Herbal", 1, 5, 2)
        f5 = st.slider("Finish Length", 1, 5, 3)
            
        st.markdown("### 🏆 Overall Rating")
        overall_rating = st.slider("Score (1-100)", 1, 100, 85)
        
        st.subheader("Logistics")
        status = st.radio("Inventory Status", ["In Stock", "Out of Stock"], horizontal=True)
        price = st.number_input("Price Paid (₪)", min_value=0)
        
        if st.button("💾 Save to Collection", type="primary", use_container_width=True):
            if not distillery or not bottle_name:
                st.error("Please fill in at least Distillery and Bottle Name.")
            else:
                new_entry = {
                    "Date Added": datetime.now().strftime("%Y-%m-%d"),
                    "Type": alc_type,
                    "Distillery": distillery,
                    "Bottle Name": bottle_name,
                    "Country": country,
                    "Region": region,
                    "ABV": abv,
                    "Age": age,
                    "Casks": ", ".join(cask_info),
                    "Nose": nose,
                    "Palate": palate,
                    "Finish": finish,
                    "Rating": overall_rating,
                    "Status": status,
                    "Price": price
                }
                
                # הוספת הרשומה ל-DataFrame
                new_df = pd.DataFrame([new_entry])
                st.session_state.database = pd.concat([st.session_state.database, new_df], ignore_index=True)
                
                # שמירה לקובץ
                st.session_state.database.to_csv(DATA_FILE, index=False)
                st.success(f"Successfully saved {distillery} {bottle_name}!")

with tab2:
    st.header("📚 My Collection")
    if st.session_state.database.empty:
        st.info("No bottles logged yet. Add your first bottle in the tab above!")
    else:
        selected_type = st.selectbox("Filter by Type", ["All"] + list(st.session_state.database["Type"].unique()))
        
        df_display = st.session_state.database
        if selected_type != "All":
            df_display = df_display[df_display["Type"] == selected_type]
            
        st.dataframe(df_display, use_container_width=True)