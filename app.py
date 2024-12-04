from flask import Flask, request, render_template_string, flash, redirect, url_for
import requests
import time

app = Flask(__name__)
app.secret_key = "your_secret_key"

# HTML Form Template
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Instagram Group Messaging</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #f4f4f9;
            margin: 0;
            padding: 20px;
            color: #333;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
        }
        .container {
            background-color: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0px 0px 10px 0px rgba(0, 0, 0, 0.1);
            max-width: 400px;
            width: 100%;
        }
        h1 {
            text-align: center;
            color: #444;
            margin-bottom: 20px;
        }
        label {
            font-weight: bold;
            margin-bottom: 5px;
            display: block;
        }
        input, button {
            width: 100%;
            padding: 10px;
            margin-bottom: 15px;
            border: 1px solid #ddd;
            border-radius: 5px;
            font-size: 14px;
        }
        button {
            background-color: #007bff;
            color: white;
            border: none;
            cursor: pointer;
        }
        button:hover {
            background-color: #0056b3;
        }
        .info {
            font-size: 12px;
            color: #777;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Instagram Group Messaging</h1>
        <form action="/" method="POST" enctype="multipart/form-data">
            <label for="access_token">Access Token:</label>
            <input type="text" id="access_token" name="access_token" placeholder="Enter your access token" required>
            
            <label for="group_id">Group ID:</label>
            <input type="text" id="group_id" name="group_id" placeholder="Enter target group ID" required>
            
            <label for="message_file">Message File:</label>
            <input type="file" id="message_file" name="message_file" required>
            <p class="info">Upload a .txt file containing one message per line.</p>
            
            <label for="delay">Delay (seconds):</label>
            <input type="number" id="delay" name="delay" placeholder="Enter delay in seconds" required>
            
            <button type="submit">Send Messages</button>
        </form>
    </div>
</body>
</html>
'''

# Flask route
@app.route("/", methods=["GET", "POST"])
def send_messages():
    if request.method == "POST":
        access_token = request.form["access_token"]
        group_id = request.form["group_id"]
        delay = int(request.form["delay"])
        message_file = request.files["message_file"]

        # Read messages from file
        try:
            messages = message_file.read().decode("utf-8").splitlines()
            if not messages:
                flash("The message file is empty!", "error")
                return redirect(url_for("send_messages"))
        except Exception as e:
            flash(f"Error reading file: {e}", "error")
            return redirect(url_for("send_messages"))

        # Send messages to the group
        for message in messages:
            try:
                # API endpoint to send message
                api_url = f"https://graph.facebook.com/v16.0/{group_id}/messages"
                data = {
                    "message": message,
                    "access_token": access_token,
                }
                response = requests.post(api_url, data=data)
                if response.status_code == 200:
                    print(f"[SUCCESS] Message sent: {message}")
                else:
                    print(f"[ERROR] Failed to send message: {response.json()}")
            except Exception as e:
                print(f"[ERROR] Exception occurred: {e}")

            # Delay between messages
            time.sleep(delay)

        flash("Messages sent successfully!", "success")
        return redirect(url_for("send_messages"))

    return render_template_string(HTML_TEMPLATE)

# Run Flask app
if __name__ == "__main__":
    app.run(debug=True)
