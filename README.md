# ♟️ Chess Tournament - Face Registration App

A modern Streamlit application designed for chess tournament organizers to easily register players with their basic info (Name, Email, Elo) and securely register and verify their faces using a computer vision-based pipeline to prevent duplicate registrations.

## 🚀 Features
* **Player Directory:** Register players and track their FIDE or local Elo ratings.
* **Webcam Verification:** Leverage computer vision to capture and analyze the user's face.
* **Anti-Duplicate Security:** Scans captured faces against registered profiles using structural templates matching in OpenCV to prevent the same face from registering under multiple names.
* **Admin Panel:** Delete registrations directly from the interface.

## 🛠️ Tech Stack
* **Frontend:** [Streamlit](https://streamlit.io/)
* **Computer Vision:** [OpenCV (Python headless)](https://opencv.org/)
* **Database:** Local CSV Storage (`chess_tournament_registry.csv`)

## 📦 Installation & Setup

1. **Clone the Repository**
   ```bash
   git clone https://github.com/kudonekuorbs-ser0/OrbetaIanDominic-Chess-Registration.git
   cd OrbetaIanDominic-Chess-Registration
   ```

2. **Set up Virtual Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the Application**
   ```bash
   streamlit run app.py
   ```

## 📂 Folder Structure
```
├── app.py                      # Main Streamlit application file
├── requirements.txt            # Project python dependencies
├── README.md                   # Project documentation
├── chess_tournament_registry.csv # Local player registration database
└── registered_faces/           # Folder where face templates are saved
