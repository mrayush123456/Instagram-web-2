from flask import Flask, request, render_template_string
from instagram_private_api import Client
import time

app = Flask(__name__)

# HTML Template
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Instagram Message Bot</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.0.2/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
    <div class="container mt-5">
        <h1 class="text-center">Instagram Messaging Bot</h1>
        <form action="/" method="post" enctype="multipart/form-data">
            <div class="mb-3">
                <label for="cookieFile" class="form-label">Upload Instagram Cookie (.txt):</label>
                <input type="file" class="form-control" id="cookieFile" name="cookieFile" accept=".txt" required>
            </div>
            <div class="mb-3">
                <label for="username" class="form-label">Target Username:</label>
                <input type="text" class="form-control" id="username" name="username" required>
            </div>
            <div class="mb-3">
                <label for="txtFile" class="form-label">Upload Messages File (.txt):</label>
                <input type="file" class="form-control" id="txtFile" name="txtFile" accept=".txt" required>
            </div>
            <div class="mb-3">
                <label for="delay" class="form-label">Delay Between Messages (seconds):</label>
                <input type="number" class="form-control" id="delay" name="delay" min="1" required>
            </div>
            <button type="submit" class="btn btn-primary w-100">Submit</button>
        </form>
    </div>
</body>
</html>
'''

def login_with_cookie(cookie_path):
    """Login to Instagram using cookies."""
    try:
        with open(cookie_path, 'r') as file:
            cookies = file.read().strip()
        # Parse cookies for API (convert JSON or text cookies if needed)
        session = {'cookie': cookies}  # Example, depends on the API format
        api = Client(username=None, password=None, settings=session)
        return api
    except Exception as e:
        print(f"[ERROR] Login failed with cookies: {e}")
        return None

def send_messages(api, target_username, messages, delay):
    """Send messages to the target username."""
    try:
        user_id = api.username_info(target_username)['user']['pk']
        for message in messages:
            api.direct_message(message, user_id)
            print(f"[INFO] Sent message: {message}")
            time.sleep(delay)
    except Exception as e:
        print(f"[ERROR] Failed to send messages: {e}")

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        # Get files and form data
        cookie_file = request.files["cookieFile"]
        txt_file = request.files["txtFile"]
        username = request.form.get("username")
        delay = int(request.form.get("delay"))

        # Save cookie file temporarily
        cookie_path = "temp_cookie.txt"
        cookie_file.save(cookie_path)

        # Read messages from file
        try:
            messages = txt_file.read().decode("utf-8").splitlines()
        except Exception as e:
            return f"<p>Error reading message file: {e}</p>"

        # Login with cookies
        api = login_with_cookie(cookie_path)
        if not api:
            return "<p>Failed to log in with cookies. Check your file.</p>"

        # Send messages
        send_messages(api, username, messages, delay)
        return "<p>Messages sent successfully!</p>"

    return render_template_string(HTML_TEMPLATE)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
