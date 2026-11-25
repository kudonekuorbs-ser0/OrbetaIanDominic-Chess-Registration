import streamlit as st
import cv2
import pandas as pd
import numpy as np
from datetime import datetime
import os
import glob

DB_FILE = "chess_tournament_registry.csv"

# Initialize Local CSV database
if not os.path.exists(DB_FILE):
    df = pd.DataFrame(columns=["Timestamp", "Full Name", "Email", "Elo Rating", "Face Registered"])
    df.to_csv(DB_FILE, index=False)

# Initialize OpenCV Face Detector
cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
face_cascade = cv2.CascadeClassifier(cascade_path)

def get_registered_players():
    if os.path.exists(DB_FILE):
        return pd.read_csv(DB_FILE)
    return pd.DataFrame()

def check_if_already_registered(new_face_gray):
    saved_images = glob.glob("registered_faces/*.jpg")
    if not saved_images:
        return None

    new_face_resized = cv2.resize(new_face_gray, (100, 100))
    best_match_email = None
    highest_similarity = -1.0

    for img_path in saved_images:
        saved_img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
        if saved_img is None:
            continue

        saved_faces = face_cascade.detectMultiScale(saved_img, scaleFactor=1.1, minNeighbors=6, minSize=(60, 60))
        if len(saved_faces) == 0:
            saved_face_resized = cv2.resize(saved_img, (100, 100))
        else:
            (x, y, w, h) = saved_faces[0]
            saved_face_resized = cv2.resize(saved_img[y:y+h, x:x+w], (100, 100))

        res = cv2.matchTemplate(new_face_resized, saved_face_resized, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, _ = cv2.minMaxLoc(res)

        if max_val > 0.75 and max_val > highest_similarity:
            highest_similarity = max_val
            filename = os.path.basename(img_path)
            parts = filename.replace(".jpg", "").split("_")
            if len(parts) > 1:
                best_match_email = parts[-1]

    return best_match_email if highest_similarity > 0.78 else None

# --- Streamlit Layout & UI ---
st.set_page_config(page_title="Chess Tournament Registration", layout="wide")
st.title("♟️ Chess Tournament - Face Registration App")
st.write("Fill out your details and use your camera to register your face for the upcoming local tournament.")

col1, col2 = st.columns(2)

with col1:
    st.header("Step 1: Player Information")
    name = st.text_input("Full Name", placeholder="e.g., Magnus Carlsen")
    email = st.text_input("Email Address", placeholder="e.g., magnus@chess.com")
    elo = st.number_input("FIDE / Local Elo Rating", min_value=0, max_value=4000, value=1500, step=1)

    st.header("Step 2: Camera Capture")
    camera_image = st.camera_input("Capture Face")

    register_clicked = st.button("Register & Verify Face", type="primary")

with col2:
    st.header("Step 3: Registration Status")
    
    if register_clicked:
        if not name or not email:
            st.error("Error: Name and Email are required!")
        elif camera_image is None:
            st.error("Error: Please capture your photo first!")
        else:
            # Decode image bytes to OpenCV format
            file_bytes = np.asarray(bytearray(camera_image.read()), dtype=np.uint8)
            image = cv2.imdecode(file_bytes, 1)
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

            faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=6, minSize=(60, 60))

            if len(faces) == 0:
                st.error("Error: No face detected. Please position yourself correctly in front of the camera.")
                st.image(rgb_image, caption="Captured Photo")
            else:
                (x, y, w, h) = faces[0]
                captured_face_region = gray[y:y+h, x:x+w]

                duplicate_player_email = check_if_already_registered(captured_face_region)
                if duplicate_player_email:
                    df = pd.read_csv(DB_FILE)
                    matched_row = df[df["Email"] == duplicate_player_email]
                    matched_name = matched_row["Full Name"].values[0] if not matched_row.empty else "Unknown Player"

                    annotated_image = rgb_image.copy()
                    cv2.rectangle(annotated_image, (x, y), (x+w, y+h), (255, 0, 0), 3)
                    st.warning(f"⚠️ Security Alert: This face is already registered under '{matched_name}' ({duplicate_player_email})!")
                    st.image(annotated_image, caption="Already Registered Face Detected")
                else:
                    # Unique Face Process
                    annotated_image = rgb_image.copy()
                    cv2.rectangle(annotated_image, (x, y), (x+w, y+h), (0, 255, 0), 3)

                    df = pd.read_csv(DB_FILE)
                    if email in df["Email"].values:
                        st.error(f"Error: Player with email {email} is already registered!")
                    else:
                        # Save database record
                        new_record = {
                            "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            "Full Name": name,
                            "Email": email,
                            "Elo Rating": elo,
                            "Face Registered": "Yes (Verified)"
                        }
                        df = pd.concat([df, pd.DataFrame([new_record])], ignore_index=True)
                        df.to_csv(DB_FILE, index=False)

                        # Save image local
                        os.makedirs("registered_faces", exist_ok=True)
                        safe_name = "".join([c for c in name if c.isalpha() or c.isdigit()]).rstrip()
                        cv2.imwrite(f"registered_faces/{safe_name}_{email}.jpg", cv2.cvtColor(image, cv2.COLOR_RGB2BGR))

                        st.success(f"🎉 Success! {name} has been successfully registered!")
                        st.image(annotated_image, caption="Registration Successful")

    st.subheader("🛠️ Admin Options")
    delete_email = st.text_input("Enter Email to Delete")
    delete_clicked = st.button("Delete Player Profile")

    if delete_clicked:
        if not delete_email:
            st.error("Error: Please provide a player's email to delete!")
        else:
            df = pd.read_csv(DB_FILE)
            if delete_email not in df["Email"].values:
                st.error(f"Error: Player with email '{delete_email}' not found.")
            else:
                player_row = df[df["Email"] == delete_email]
                p_name = player_row["Full Name"].values[0]
                safe_name = "".join([c for c in p_name if c.isalpha() or c.isdigit()]).rstrip()

                face_path = f"registered_faces/{safe_name}_{delete_email}.jpg"
                if os.path.exists(face_path):
                    os.remove(face_path)

                df = df[df["Email"] != delete_email]
                df.to_csv(DB_FILE, index=False)
                st.info(f"Successfully deleted player '{p_name}' from registry.")

st.markdown("---")
st.header("🏆 Current Registered Players")
st.dataframe(get_registered_players(), use_container_width=True)
