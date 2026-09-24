"""
Image Steganography
Run with:
    pip install -r requirements.txt
    python app.py
Then open http://127.0.0.1:5000
"""
import os
import webbrowser
from threading import Timer

from flask import Flask, redirect, url_for

from steganography import bp

app = Flask(__name__)
app.register_blueprint(bp)


@app.route("/")
def home():
    return redirect(url_for("steganography.index"))


def _open_browser():
    webbrowser.open_new("http://127.0.0.1:5000/")


if __name__ == "__main__":
    # Open the browser once (guarded so the debug reloader doesn't open two tabs).
    if os.environ.get("WERKZEUG_RUN_MAIN") != "true":
        Timer(1, _open_browser).start()
    app.run(debug=True)
