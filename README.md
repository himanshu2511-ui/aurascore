# ✦ AuraScore
**AI Personal Glow-Up Coach & Facial Aesthetics Analyzer**

AuraScore is a full-stack, AI-powered application designed to analyze facial features securely and privately. Using advanced computer vision and machine learning geometry directly in the browser/backend flow, it provides users with personalized styling, grooming, and skincare roadmaps. 

![AuraScore](https://img.shields.io/badge/Status-Live-success?style=for-the-badge) ![License](https://img.shields.io/badge/License-MIT-blue?style=for-the-badge) ![Python](https://img.shields.io/badge/Python-3.10-purple?style=for-the-badge) ![React](https://img.shields.io/badge/React-19-cyan?style=for-the-badge)

---

## ✨ Features
* **Real-time Facial Scanning:** Uses `mediapipe` and OpenCV to capture and calculate precise facial landmarks over a 40-second analysis period.
* **Smart Auth Portal:** Secure JWT & Argon2 based authentication with an automated 6-digit OTP email verification flow to prevent spam requests.
* **Global Leaderboard:** Compete for the highest cosmetic and grooming "Aura Score" amongst all authenticated users.
* **Actionable Roadmap:** Generates customized skincare and grooming steps based directly on detected facial shape (Oval, Square, Round, etc.) and skin tone characteristics.
* **End-to-End Privacy:** Image payloads are parsed completely ephemerally in memory and discarded. No images are aggressively stored on servers.
* **Premium Glassmorphism UI:** Framer motion page transitions and responsive design.

---

## 🛠 Tech Stack
### **Frontend (`/frontend`)**
* **Framework:** React 19 + Vite
* **Styling:** Vanilla CSS (Glassmorphism & animated gradients)
* **Animation:** Framer Motion
* **Webcam:** `react-webcam`
* **Deployment:** Vercel

### **Backend (`/backend`)**
* **Framework:** FastAPI
* **Computer Vision:** Google MediaPipe (`0.10.14`) + OpenCV Headless
* **Database:** SQLite (local) / PostgreSQL (production bindings included) + SQLAlchemy ORM
* **Auth:** Python-JOSE (JWT), Passlib (Argon2), `smtplib` (Email Validation)
* **Deployment:** Render

---

## 🚀 Running Locally

### 1. Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`

# Install dependencies
pip install -r requirements.txt

# Create .env file based on the example
cp .env.example .env
```

**Backend Environment Variables (`.env`)**
```env
# Required for signup OTPs
GMAIL_USER=your-email@gmail.com
GMAIL_APP_PASSWORD=your-16-digit-app-password
JWT_SECRET=YOUR_secret_jwt_key

# Optional (Defaults to local SQLite)
DATABASE_URL=postgresql://user:password@hostname/db_name 
```

**Start the API**
```bash
uvicorn main:app --reload --port 8000
```

### 2. Frontend Setup
```bash
cd frontend

# Install packages
npm install

# Setup environment variable
# Create a .env file and add the local API URL
echo "VITE_API_URL=http://localhost:8000" > .env

# Run the dev server
npm run dev
```

---

## 🌐 Production Deployment

### Frontend (Vercel)
1. Import the repository into **Vercel**.
2. Set the **Root Directory** to `frontend`.
3. Choose **Vite** as the framework preset.
4. Set the `VITE_API_URL` environment variable to your active backend URL.

### Backend (Render Web Service)
1. Import the repository into **Render** as a new Web Service.
2. Set **Root Directory** to `backend`.
3. Build Command: `pip install -r requirements.txt`
4. Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. *(Important)* Provide your `GMAIL_USER`, `GMAIL_APP_PASSWORD`, and `JWT_SECRET` in Render.
6. *(Important)* A `.python-version` file is included natively to force `Python 3.10.11` to prevent `mediapipe` incompatibilities on cutting-edge Render native environments.

> **Note on Free Tiers:** Render's free tier erases internal SQLite databases when spinning down. Connect a free PostgreSQL database (e.g., Neon.tech) by simply pasting their `DATABASE_URL` into Render's environment variables. The `psycopg2` bindings are installed and will transition automatically!

---

## 🛡️ License & Privacy
All facial processing matrices are strictly loaded in memory and purged instantly. AuraScore does not log or warehouse personal media artifacts.

VISIT :https://aurascore-eight.vercel.app/ ------FOR TRIAL

*(Educational / Demo License)*
