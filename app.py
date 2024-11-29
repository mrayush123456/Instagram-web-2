from flask import Flask, request, render_template_string, redirect, url_for
from instagrapi import Client
import time
import os

app = Flask(__name__)

# HTML Template for the Web Page
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Instagram Group Messenger</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #f0f0f0;
            margin: 0;
            padding: 0;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
        }
        .container {
            background-color: #ffffff;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2);
            max-width: 400px;
            width: 100%;
        }
        h1 {
            text-align: center;
            color: #333;
            margin-bottom: 20px;
        }
        label {
            font-weight: bold;
            margin-top: 10px;
            display: block;
            color: #555;
        }
        input, textarea, button {
            width: 100%;
            padding: 10px;
            margin-top: 5px;
            margin-bottom: 15px;
            border: 1px solid #ccc;
            border-radius: 5px;
            font-size: 16px;
        }
        button {
            background-color: #007BFF;
            color: white;
            border: none;
            cursor: pointer;
        }
        button:hover {
            background-color: #0056b3;
        }
        .message {
            color: red;
            text-align: center;
            margin-top: -10px;
            font-size: 14px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Instagram Group Messenger</h1>
        <form action="/" method="POST" enctype="multipart/form-data">
            <label for="username">Instagram Username:</label>
            <input type="text" id="username" name="username" required placeholder="Enter your username">

            <label for="password">Instagram Password:</label>
            <input type="password" id="password" name="password" required placeholder="Enter your password">

            <label for="group_id">Target Group/Chat ID:</label>
            <input type="text" id="group_id" name="group_id" required placeholder="Enter group/chat ID">

            <label for="delay">Delay (in seconds):</label>
            <input type="number" id="delay" name="delay" required placeholder="Enter delay between messages">

            <label for="messages_file">Upload Messages File (TXT):</label>
            <input type="file" id="messages_file" name="messages_file" accept=".txt" required>

            <button type="submit">Send Messages</button>
        </form>
    </div>
</body>
</html>
'''

# Function to log in to Instagram
def instagram_login(username, password):
    cl = Client()
    try:
        cl.login(username, password)
        print("[SUCCESS] Logged in to Instagram!")
        return cl
    except Exception as e:
        print(f"[ERROR] Login failed: {e}")
        return None

# Function to send messages to a group/chat
def send_messages(cl, group_id, messages, delay):
    try:
        for message in messages:
            cl.direct_send(message, thread_ids=[group_id])
            print(f"[SUCCESS] Sent message: {message}")
            time.sleep(delay)
        return True
    except Exception as e:
        print(f"[ERROR] Failed to send message: {e}")
        return False

# Flask routes
@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        # Get form data
        username = request.form.get("username")
        password = request.form.get("password")
        group_id = request.form.get("group_id")
        delay = int(request.form.get("delay"))
        messages_file = request.files["messages_file"]

        # Save uploaded file temporarily
        file_path = os.path.join("temp_messages.txt")
        messages_file.save(file_path)

        # Read messages from the file
        try:
            with open(file_path, "r") as file:
                messages = file.read().splitlines()
        except Exception as e:
            return f"<p>Error reading the file: {e}</p>"

        # Log in to Instagram
        cl = instagram_login(username, password)
        if not cl:
            return "<p>Failed to log in. Please check your credentials.</p>"

        # Send messages to the group
        success = send_messages(cl, group_id, messages, delay)
        os.remove(file_path)  # Delete temp file after sending

        if success:
            return "<p>Messages sent successfully!</p>"
        else:
            return "<p>Failed to send messages. Check the group ID or your messages.</p>"

    # Render the form
    return render_template_string(HTML_TEMPLATE)

if __name__ == "__main__":
    app.run(debug=True)
