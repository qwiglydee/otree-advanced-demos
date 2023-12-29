"""
Utilities to generate and manipulate images
"""
from io import BytesIO
from base64 import b64decode, b64encode

MSG_NEED_PIL = """
FAILURE: Before using these real-effort tasks,
You need to:
(1) run "pip install Pillow"
(2) add Pillow to your requirements.txt
"""

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    import sys

    sys.tracebacklimit = 0
    raise SystemExit(MSG_NEED_PIL)


def encode(image: Image):
    buf = BytesIO()
    image.save(buf, "PNG")
    buf64 = b64encode(buf.getvalue())
    return "data:image/png;base64," + buf64.decode('ascii')


def decode(dataurl: str):
    assert dataurl.startswith("data:image/png;base64,")
    buf64 = b64decode(dataurl[21:])
    buf = BytesIO(buf64)
    image = Image.open(buf)
    return image


def font(filename, size):
    return ImageFont.truetype(str(filename), size)


def text(text, font, size, *, padding=0, color="#000000", bgcolor="#FFFFFF"):
    dumb = Image.new("RGB", (0, 0))
    w, h = ImageDraw.ImageDraw(dumb).textsize(text, font)
    image = Image.new("RGBA", (w + padding * 2, h + padding * 2), bgcolor)
    draw = ImageDraw.Draw(image)
    draw.text((padding, padding), text, font=font, fill=color)

    return image


def distort(image, k=8):
    w, h = image.size
    image = image.resize((w//k, h//k), Image.BILINEAR).resize((w, h), Image.BILINEAR)
    return image