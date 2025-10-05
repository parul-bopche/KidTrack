# from fastapi import FastAPI, HTTPException, status, Depends
# from fastapi.middleware.cors import CORSMiddleware
# from firebase_admin import credentials, initialize_app, firestore
# import os
# from dotenv import load_dotenv
# from pydantic import BaseModel
# from auth_dependency import get_current_user_id

# # --- 1. Pydantic Model for Booking Data ---
# class BookingRequest(BaseModel):
#     pickup_location: str
#     dropoff_location: str
#     schedule_date: str
#     user_id: str 

# # --- 2. FIREBASE ADMIN SDK INITIALIZATION ---
# load_dotenv()
# db = None
# try:
#     # Try environment variable first (recommended for production)
#     key_path = os.getenv("FIREBASE_ADMIN_KEY_PATH")
#     if key_path:
#         cred = credentials.Certificate(key_path)
#         firebase_admin_app = initialize_app(cred)
#         db = firestore.client()
#     else:
#         # Fallback: look for a local admin-key.json shipped in the backend folder
#         local_key = os.path.join(os.path.dirname(__file__), "admin-key.json")
#         if os.path.exists(local_key):
#             cred = credentials.Certificate(local_key)
#             firebase_admin_app = initialize_app(cred)
#             db = firestore.client()
#         else:
#             raise FileNotFoundError("No Firebase admin key found. Set FIREBASE_ADMIN_KEY_PATH or place admin-key.json in backend/")
# except Exception as e:
#     # Don't crash the process during import; let endpoints return 500 if DB is None
#     print(f"FATAL: Firebase Admin SDK Initialization Failed. Check .env and JSON key: {e}")
#     db = None

# app = FastAPI()


# @app.on_event("startup")
# async def on_startup():
#     print("APPLICATION EVENT: startup - FastAPI is starting")


# @app.on_event("shutdown")
# async def on_shutdown():
#     print("APPLICATION EVENT: shutdown - FastAPI is shutting down")

# # --- 3. CORS Setup (Essential for React Frontend on localhost:3000) ---
# origins = ["http://localhost:3000", "http://127.0.0.1:3000"]

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=origins,
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # --- 4. ENDPOINTS ---

# @app.get("/")
# def read_root():
#     return {"message": "KidTrack Python Backend is Running"}

# # 🔑 PROTECTED ENDPOINT 1: Book Journey
# @app.post("/api/secure/book_ride")
# def book_ride(
#     request: BookingRequest, 
#     current_user_id: str = Depends(get_current_user_id) # Token Verification
# ):
#     """Handles secure ride booking logic after verifying the user token."""
    
#     # SECURITY CHECK: Ensure the token's UID matches the UID in the request body
#     if current_user_id != request.user_id:
#         raise HTTPException(status_code=403, detail="Token mismatch: User ID does not match request data.")

#     if db is None:
#         raise HTTPException(status_code=500, detail="Database not initialized.")

#     try:
#         # Securely save data to Firestore 'bookings' collection
#         db.collection('bookings').add({
#             "uid": current_user_id,
#             "pickup": request.pickup_location,
#             "dropoff": request.dropoff_location,
#             "date": request.schedule_date,
#             "status": "PENDING_DRIVER_ASSIGNMENT"
#         })
#         return {"message": "Ride successfully booked and secured by Python backend.", "booking_status": "Processing"}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Database error: {e}")


# # --- 5. RUN SERVER (Used when running this file directly) ---
# if __name__ == "__main__":
#     import uvicorn
#     # Recommended run command from project root:
#     #   uvicorn api_service:app --reload --port 8000
#     # Or run directly from the backend folder using the module name:
#     #   uvicorn api_server:app --reload --port 8000
#     uvicorn.run(app, host="0.0.0.0", port=8000)

from fastapi import FastAPI, HTTPException, status, Depends
from fastapi.middleware.cors import CORSMiddleware
from firebase_admin import credentials, initialize_app, firestore
import os
from dotenv import load_dotenv
from pydantic import BaseModel
from auth_dependency import get_current_user_id

# --- 1. Pydantic Models for Data Validation ---

# Model for Booking Data (Parent Request)
class BookingRequest(BaseModel):
    pickup_location: str
    dropoff_location: str
    schedule_date: str
    user_id: str 

# 🎯 NEW: Model for Live GPS Updates (Driver/Vehicle Tracking)
class GPSUpdate(BaseModel):
    latitude: float
    longitude: float
    vehicle_id: str
    

# --- 2. FIREBASE ADMIN SDK INITIALIZATION (CRITICAL SECURITY) ---
load_dotenv()
db = None
try:
    # Logic to securely find and load the admin-key.json
    key_path = os.getenv("FIREBASE_ADMIN_KEY_PATH")
    if not key_path:
        local_key = os.path.join(os.path.dirname(__file__), "admin-key.json")
        if os.path.exists(local_key):
             key_path = local_key
        else:
             raise FileNotFoundError("No Firebase admin key found.")
             
    cred = credentials.Certificate(key_path)
    firebase_admin_app = initialize_app(cred)
    db = firestore.client()
    
except Exception as e:
    print(f"FATAL: Firebase Admin SDK Initialization Failed. Check .env and JSON key: {e}")
    db = None

app = FastAPI()

# --- 3. CORS Setup (Essential for React Frontend on localhost:3000) ---
origins = ["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:3001",   # <--- ADDED: New Port
    "http://127.0.0.1:3001"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 4. ENDPOINTS ---

@app.get("/")
def read_root():
    return {"message": "KidTrack Python Backend is Running"}

# 🔑 PROTECTED ENDPOINT 1: Book Journey
@app.post("/api/secure/book_ride")
def book_ride(
    request: BookingRequest, 
    current_user_id: str = Depends(get_current_user_id) # Token Verification
):
    """Handles secure ride booking logic after verifying the user token."""
    
    # SECURITY CHECK: Ensure the token's UID matches the UID in the request body
    if current_user_id != request.user_id:
        raise HTTPException(status_code=403, detail="Token mismatch: User ID does not match request data.")

    if db is None:
        raise HTTPException(status_code=500, detail="Database not initialized.")

    try:
        # Securely save data to Firestore 'bookings' collection
        db.collection('bookings').add({
            "uid": current_user_id,
            "pickup": request.pickup_location,
            "dropoff": request.dropoff_location,
            "date": request.schedule_date,
            "status": "PENDING_DRIVER_ASSIGNMENT"
        })
        return {"message": "Ride successfully booked and secured by Python backend.", "booking_status": "Processing"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")


# 🎯 NEW PROTECTED ENDPOINT 2: Live GPS Update (CRITICAL FOR TRACKING)
@app.post("/api/secure/update_gps")
def update_gps_location(
    data: GPSUpdate, 
    current_user_id: str = Depends(get_current_user_id) # Token Verification for Driver App
):
    """
    Receives live location data from a driver's device and updates Firestore.
    """
    if db is None:
        raise HTTPException(status_code=500, detail="Database not initialized.")

    try:
        # Uses set() to UPDATE the single document for the vehicle (Document ID is the Vehicle ID)
        db.collection("live_tracking").document(data.vehicle_id).set({
            "latitude": data.latitude,
            "longitude": data.longitude,
            "timestamp": firestore.SERVER_TIMESTAMP,
            "driver_uid": current_user_id
        })
        return {
            "message": "GPS location updated successfully.",
            "vehicle": data.vehicle_id,
            "coordinates": f"{data.latitude}, {data.longitude}"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database save error: {e}")


# --- 5. RUN SERVER ---
if __name__ == "__main__":
    import uvicorn
    # Use this command to run your server: uvicorn api_service:app --reload --port 8000
    uvicorn.run(app, host="0.0.0.0", port=8000)