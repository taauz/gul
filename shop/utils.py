"""Yuklangan suratlarni bitta standartga keltirish (kvadrat, shaffoflik olib tashlanadi)."""
import io

from django.core.files.base import ContentFile
from PIL import Image, ImageOps

STD_SIZE = 1000
BG = (250, 245, 238)  # sayt foniga mos krem rang


def standardize_image(field_file):
    """ImageField fayl obyektini kvadrat shaklga keltirib, yangi ContentFile qaytaradi."""
    field_file.seek(0)
    img = Image.open(field_file)
    img = ImageOps.exif_transpose(img)  # telefon suratlaridagi aylanishni tuzatish
    if img.mode in ("RGBA", "LA") or (img.mode == "P" and "transparency" in img.info):
        canvas = Image.new("RGB", img.size, BG)
        canvas.paste(img.convert("RGBA"), mask=img.convert("RGBA").split()[-1])
        img = canvas
    else:
        img = img.convert("RGB")
    img = ImageOps.fit(img, (STD_SIZE, STD_SIZE), Image.LANCZOS, centering=(0.5, 0.42))
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=88)
    return ContentFile(buf.getvalue())
