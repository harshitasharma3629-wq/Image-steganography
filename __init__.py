"""
Image Steganography - Flask blueprint.
Web UI around the same LSB encode/decode logic as the standalone CLI
version: hide a text message inside an uploaded image, or extract one.
"""
import io
import uuid
from pathlib import Path

from flask import Blueprint, render_template, request, send_from_directory, url_for
from PIL import Image

bp = Blueprint("steganography", __name__, url_prefix="/steganography")

UPLOAD_DIR = Path(__file__).parent.parent / "static" / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
DELIMITER = "#####END#####"


def _text_to_bits(text: str) -> str:
    return "".join(format(ord(char), "08b") for char in text)


def _bits_to_text(bits: str) -> str:
    chars = [bits[i:i + 8] for i in range(0, len(bits), 8)]
    return "".join(chr(int(b, 2)) for b in chars if len(b) == 8)


def encode_image(img: Image.Image, message: str) -> Image.Image:
    img = img.convert("RGB")
    pixels = list(img.getdata())
    bits = _text_to_bits(message + DELIMITER)

    capacity_bits = len(pixels) * 3
    if len(bits) > capacity_bits:
        raise ValueError(
            f"Message too long for this image ({len(bits)} bits needed, "
            f"{capacity_bits} available). Use a larger image or a shorter message."
        )

    bit_index = 0
    new_pixels = []
    for pixel in pixels:
        channels = list(pixel[:3])
        for c in range(3):
            if bit_index < len(bits):
                channels[c] = (channels[c] & ~1) | int(bits[bit_index])
                bit_index += 1
        new_pixels.append(tuple(channels))

    out = Image.new("RGB", img.size)
    out.putdata(new_pixels)
    return out


def decode_image(img: Image.Image) -> str:
    img = img.convert("RGB")
    pixels = list(img.getdata())
    bits = "".join(str(pixel[c] & 1) for pixel in pixels for c in range(3))
    decoded = _bits_to_text(bits)
    if DELIMITER in decoded:
        return decoded.split(DELIMITER)[0]
    raise ValueError("No hidden message found in this image (or it wasn't encoded with this tool).")


@bp.route("/", methods=["GET"])
def index():
    return render_template("steganography/index.html", active="steganography")


@bp.route("/encode", methods=["POST"])
def encode():
    error = None
    encoded_filename = None
    original_filename = None
    try:
        file = request.files.get("image")
        message = request.form.get("message", "")
        if not file or file.filename == "":
            raise ValueError("Please choose an image to encode.")
        if not message.strip():
            raise ValueError("Please enter a message to hide.")

        img = Image.open(file.stream)

        session_id = uuid.uuid4().hex[:8]
        original_filename = f"{session_id}_original.png"
        img.convert("RGB").save(UPLOAD_DIR / original_filename)

        encoded_img = encode_image(img, message)
        encoded_filename = f"{session_id}_encoded.png"
        encoded_img.save(UPLOAD_DIR / encoded_filename)
    except (ValueError, OSError) as e:
        error = str(e)

    return render_template(
        "steganography/index.html",
        active="steganography",
        encode_error=error,
        encoded_filename=encoded_filename,
        original_filename=original_filename,
    )


@bp.route("/decode", methods=["POST"])
def decode():
    error = None
    hidden_message = None
    uploaded_filename = None
    try:
        file = request.files.get("image")
        if not file or file.filename == "":
            raise ValueError("Please choose an image to decode.")
        img = Image.open(file.stream)

        uploaded_filename = f"{uuid.uuid4().hex[:8]}_decode_input.png"
        img.convert("RGB").save(UPLOAD_DIR / uploaded_filename)

        hidden_message = decode_image(img)
    except (ValueError, OSError) as e:
        error = str(e)

    return render_template(
        "steganography/index.html",
        active="steganography",
        decode_error=error,
        hidden_message=hidden_message,
        uploaded_filename=uploaded_filename,
        show_decode=True,
    )


@bp.route("/uploads/<path:filename>")
def uploaded_file(filename):
    return send_from_directory(UPLOAD_DIR, filename)
