from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import google.generativeai as genai
import os

# 1️⃣ Load environment variables
load_dotenv()

# 2️⃣ Configure Gemini API
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# 3️⃣ Initialize Flask
app = Flask(__name__)
CORS(app)  # allow requests from frontend

# 4️⃣ Storage for latest interaction
latest_interaction = {"text": None, "response": None}

# 5️⃣ Test route
@app.route("/")
def home():
    return "Flask backend is running ✅"

# 6️⃣ Gemini route — handles text input from frontend
@app.route("/gemini", methods=["POST"])
def gemini_response():
    data = request.get_json()
    user_text = data.get("text", "").strip()

    if not user_text:
        return jsonify({"error": "No text provided"}), 400

    try:
        print(f"\n🟢 New Input Received: {user_text}\n")

        # Wrap the user's intent in instructions
        prompt = f"""
You are a voice assistant. The user gives a short intent like "pep talk", "scary voice", or "motivation".
Reply as a voice assistant with exactly two short, natural sentences that match the tone.
It must sound human and spoken — not robotic.
Generate your response based on this intent: "{user_text}"
Examples:
pep talk → "Come on, you've got this! Don't quit now."
scary voice → "If you sleep now, something's watching. Stay awake."
motivation → "Every second counts. Keep pushing."
The output should ultimately be motivational and to keep the user awake.
"""

        # Generate response
        model = genai.GenerativeModel("gemini-2.5-flash")
        response = model.generate_content(prompt)
        gemini_output = response.text.strip()

        # Save latest interaction
        latest_interaction["text"] = user_text
        latest_interaction["response"] = gemini_output

        print(f"💬 Gemini Response: {gemini_output}\n")

        # Return confirmation + Gemini output
        return jsonify({
            "message": "✅ Received text successfully!",
            "input": user_text,
            "response": gemini_output
        })
    except Exception as e:
        print("❌ Error:", e)
        return jsonify({"error": str(e)}), 500


# 7️⃣ Retrieve last stored response
@app.route("/latest", methods=["GET"])
def get_latest():
    if not latest_interaction["response"]:
        return jsonify({"message": "No previous interaction yet."}), 404
    return jsonify(latest_interaction)

# 8️⃣ Run the server
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
