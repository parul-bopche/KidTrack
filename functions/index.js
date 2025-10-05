// functions/index.js

const functions = require("firebase-functions");
const admin = require("firebase-admin"); 
const cors = require("cors")({ origin: true }); // FIX: Double quotes used
const db = admin.firestore(); // FIX: Indentation (2 spaces)

// 🔑 CORE LOGIC: HTTP Endpoint for Booking
exports.bookRideSecure = functions.https.onRequest((request, response) => {
  cors(request, response, async () => { // FIX: Indentation (2 spaces)
    
    // --- 1. Security Check: Method ---
    if (request.method !== "POST") { // FIX: Double quotes
      return response.status(405).send({ message: "Method Not Allowed. Use POST." });
    }

    // --- 2. Input Validation ---
    const { pickupLocation, dropoffLocation, scheduleDate, userUid } = request.body; // FIX: camelCase, Indentation, space in {}

    if (!pickupLocation || !dropoffLocation || !userUid) { // FIX: camelCase
      return response.status(400).send({ message: "Missing required fields." });
    }

    // --- 3. Database Operation ---
    try {
      await db.collection("bookings").add({ // FIX: Double quotes
        uid: userUid, // FIX: camelCase
        pickup: pickupLocation, // FIX: camelCase
        dropoff: dropoffLocation, // FIX: camelCase
        date: scheduleDate, // FIX: camelCase
        status: "PENDING_DRIVER_ASSIGNMENT", // FIX: Double quotes
        timestamp: admin.firestore.FieldValue.serverTimestamp() // Line split to fit 80 char limit
      });

      response.status(200).send({ message: "Ride successfully booked via Cloud Function." }); // FIX: Double quotes
    } catch (error) {
      console.error("Firestore Save Error:", error);
      response.status(500).send({ error: "Failed to save booking data." }); // FIX: Double quotes
    }
  });
});
// FIX: Final line has required newline (eol-last)