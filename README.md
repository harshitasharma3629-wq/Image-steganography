# Image Steganography

Hide a text message inside an image using the LSB (least significant bit) technique, and read it back out.

## What it does
- **Encode:** upload an image and a message. The message is written into the lowest bit of each red, green and blue value, so every colour value changes by at most 1 and the image looks unchanged. You get the encoded PNG back to download.
- **Decode:** upload an encoded PNG and the hidden message is extracted.
- The message is stored as UTF-8 bytes followed by an end marker (`#####END#####`), so the decoder knows where it stops. Non-English text and emoji work.
- Checks that the message fits in the image and shows a clear error if it does not.

## Important
Save and share the encoded image as **PNG**. JPEG compression changes pixel values and destroys the hidden message. This tool hides a message; it does not encrypt it.

## Run it
Requires Python 3.9 or newer.
```bash
pip install -r requirements.txt
python app.py          # opens http://127.0.0.1:5000
```

## Project structure
```
app.py                     # Flask app
steganography/
  __init__.py              # Flask blueprint + LSB encode/decode logic
templates/                 # HTML page
static/style.css
static/uploads/            # uploaded and encoded images (git-ignored)
```

## Tech
Python, Pillow (PIL), Flask
