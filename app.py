from flask import Flask, render_template, request, jsonify
from google import genai
import openai
from dotenv import load_dotenv
import os
from mail import send_email
from datetime import datetime
# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        return render_template("index.html", user_input="abc", chatbot_reply="abc")
    return render_template("index.html", user_input="", chatbot_reply="")


@app.route("/home", methods=["GET"])
def home():
    return render_template("home.html")


@app.route("/new", methods=["GET"])
def new():
    return render_template("new.html")


@app.route("/UGM")
def ugm():
    return render_template("ugm.html")


@app.route("/from", methods=["GET"])
def new_from():
    return render_template("from.html")


@app.route("/from_post", methods=["POST"])
def from_post():
    name = f"{request.form.get('firstName')} {request.form.get('lastName')}"
    email = request.form.get("email")
    subject = request.form.get("subject")
    message = request.form.get("message")
    timestamp= datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    uploaded_file = request.files.get("attachment")
    file_info = {}
    file_path = None

    if uploaded_file:
        from werkzeug.utils import secure_filename

        filename = secure_filename(uploaded_file.filename)

        os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
        file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        uploaded_file.save(file_path)

        file_info = {"filename": filename, "content_type": uploaded_file.content_type}

    mailbody = f"""
<!DOCTYPE html>
<html>
<head>
  <style>
    body {{
      font-family: Arial, sans-serif;
      color: #333;
      line-height: 1.6;
    }}
    .container {{
      border: 1px solid #ddd;
      padding: 20px;
      max-width: 600px;
      margin: auto;
      background-color: #f9f9f9;
    }}
    h2 {{
      color: #444;
    }}
    .section {{
      margin-bottom: 20px;
    }}
    .label {{
      font-weight: bold;
    }}
    .footer {{
      margin-top: 30px;
      font-size: 0.9em;
      color: #777;
      border-top: 1px solid #ddd;
      padding-top: 10px;
    }}
  </style>
</head>
<body>
  <div class="container">s
    <h2>📩 New From submitted</h2>s
    <div class="section">
      <p class="label">🕒 Submitted On:</p>
      <p>{timestamp}</p>
    </div>
    <div class="section">
      <p class="label">👤 Details:</p>
      <ul>
        <li><strong>Name:</strong> {name}</li>
        <li><strong>Email:</strong> {email}</li>
      </ul>
    </div>
    <div class ="section">
    <p class= "lebel"> Subject: {subject} </p>
    </div>
    <div class="section">
      <p class="label">📝 Cover Letter / Message:</p>
      <p>{message}</p>
    </div>
    <div class="footer">
      <p>This is an automated notification. Please do not reply.</p>
    </div>
  </div>
</body>
</html>
"""

    try:
        send_email(
            recipient_email="pradip.paul@maheshwaree.com",
            subject="Test mail after form submit",
            html_body=mailbody,
            attachments=[file_path] if file_path else None,
        )
        # Remove the file only if it exists
        if file_path and os.path.exists(file_path):
            os.remove(file_path)
            print("✅ File deleted after successful email.")
    except Exception as e:
        print("❌ Error sending the email:", e)

    return (
        jsonify(
            {
                "status": "success",
                "message": "Form and file received.",
                "form_data": {
                    "name": name,
                    "email": email,
                    "subject": subject,
                    "message": message,
                },
                "file_info": file_info,
            }
        ),
        200,
    )


if __name__ == "__main__":
    app.run(debug=True)
