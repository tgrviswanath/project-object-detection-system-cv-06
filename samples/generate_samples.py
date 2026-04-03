"""
Generate sample images for cv-06 Object Detection System.
Run: pip install Pillow && python generate_samples.py
Output: 4 images — street scene, indoor, parking lot, park.
"""
from PIL import Image, ImageDraw
import os

OUT = os.path.dirname(__file__)


def save(img, name):
    img.save(os.path.join(OUT, name))
    print(f"  created: {name}")


def draw_car(d, x, y, w, h, color):
    d.rectangle([x, y + h // 3, x + w, y + h], fill=color)
    d.polygon([(x + w // 6, y + h // 3), (x + w // 4, y), (x + 3 * w // 4, y), (x + 5 * w // 6, y + h // 3)], fill=color)
    d.ellipse([x + w // 8, y + h - h // 4, x + w // 8 + h // 3, y + h + h // 6], fill=(30, 30, 30))
    d.ellipse([x + w - w // 8 - h // 3, y + h - h // 4, x + w - w // 8, y + h + h // 6], fill=(30, 30, 30))


def draw_person(d, x, y, h, skin=(220, 180, 140), shirt=(60, 100, 180)):
    head_r = h // 8
    d.ellipse([x - head_r, y, x + head_r, y + head_r * 2], fill=skin)
    body_top = y + head_r * 2
    d.rectangle([x - head_r - 2, body_top, x + head_r + 2, body_top + h // 3], fill=shirt)
    d.rectangle([x - head_r, body_top + h // 3, x - 2, body_top + h // 3 + h // 3], fill=(40, 40, 80))
    d.rectangle([x + 2, body_top + h // 3, x + head_r, body_top + h // 3 + h // 3], fill=(40, 40, 80))


def street_scene():
    img = Image.new("RGB", (800, 500), (135, 180, 220))
    d = ImageDraw.Draw(img)
    d.rectangle([0, 320, 800, 500], fill=(80, 80, 80))
    for x in range(0, 800, 100):
        d.rectangle([x, 390, x + 60, 405], fill=(255, 255, 255))
    d.rectangle([0, 290, 800, 322], fill=(160, 150, 140))
    for bx, bw, bh, bc in [(0, 120, 200, (180, 170, 160)), (140, 100, 160, (160, 150, 140)),
                             (560, 130, 190, (190, 180, 170)), (700, 100, 170, (170, 160, 150))]:
        d.rectangle([bx, 290 - bh, bx + bw, 290], fill=bc)
    draw_car(d, 80, 330, 160, 60, (200, 50, 50))
    draw_car(d, 400, 330, 160, 60, (50, 100, 200))
    draw_car(d, 600, 330, 160, 60, (50, 180, 80))
    draw_person(d, 300, 240, 80)
    draw_person(d, 360, 245, 75, shirt=(180, 60, 60))
    draw_person(d, 500, 242, 78, shirt=(60, 160, 60))
    return img


def indoor_scene():
    img = Image.new("RGB", (700, 500), (230, 220, 210))
    d = ImageDraw.Draw(img)
    d.rectangle([0, 400, 700, 500], fill=(160, 140, 110))
    # sofa
    d.rectangle([50, 280, 350, 400], fill=(100, 80, 160))
    d.rectangle([50, 250, 350, 290], fill=(120, 100, 180))
    d.rectangle([50, 250, 90, 400], fill=(120, 100, 180))
    d.rectangle([310, 250, 350, 400], fill=(120, 100, 180))
    # table
    d.rectangle([400, 310, 650, 340], fill=(140, 100, 60))
    d.rectangle([410, 340, 430, 400], fill=(120, 80, 40))
    d.rectangle([620, 340, 640, 400], fill=(120, 80, 40))
    # tv
    d.rectangle([200, 80, 500, 240], fill=(20, 20, 20))
    d.rectangle([210, 90, 490, 230], fill=(40, 80, 120))
    d.rectangle([330, 240, 370, 280], fill=(30, 30, 30))
    # lamp
    d.polygon([(580, 100), (620, 100), (600, 60)], fill=(255, 220, 100))
    d.rectangle([597, 100, 603, 310], fill=(160, 130, 80))
    draw_person(d, 180, 200, 90)
    return img


def parking_lot():
    img = Image.new("RGB", (800, 500), (100, 100, 100))
    d = ImageDraw.Draw(img)
    for y in range(0, 500, 160):
        d.rectangle([0, y, 800, y + 3], fill=(255, 255, 255))
    for x in range(0, 800, 130):
        d.rectangle([x, 0, x + 3, 500], fill=(200, 200, 200))
    colors = [(200, 50, 50), (50, 100, 200), (50, 180, 80), (200, 180, 50), (150, 50, 200), (50, 180, 180)]
    positions = [(20, 20), (160, 20), (300, 20), (440, 20), (580, 20), (20, 180), (160, 180), (300, 180)]
    for i, (px, py) in enumerate(positions):
        draw_car(d, px, py, 120, 50, colors[i % len(colors)])
    return img


def park_scene():
    img = Image.new("RGB", (700, 500), (135, 200, 240))
    d = ImageDraw.Draw(img)
    d.rectangle([0, 320, 700, 500], fill=(80, 160, 60))
    d.rectangle([0, 300, 700, 325], fill=(100, 180, 80))
    # path
    d.polygon([(280, 500), (420, 500), (380, 300), (320, 300)], fill=(180, 160, 120))
    # trees
    for tx, th in [(80, 180), (160, 160), (540, 190), (620, 170)]:
        d.rectangle([tx - 8, 320 - th + 60, tx + 8, 320], fill=(100, 70, 40))
        d.ellipse([tx - 50, 320 - th, tx + 50, 320 - th + 100], fill=(40, 140, 40))
        d.ellipse([tx - 40, 320 - th - 20, tx + 40, 320 - th + 60], fill=(60, 160, 60))
    # bench
    d.rectangle([290, 340, 410, 350], fill=(140, 100, 60))
    d.rectangle([295, 350, 310, 380], fill=(120, 80, 40))
    d.rectangle([390, 350, 405, 380], fill=(120, 80, 40))
    draw_person(d, 200, 240, 80)
    draw_person(d, 480, 238, 82, shirt=(200, 100, 60))
    draw_person(d, 350, 260, 70, shirt=(180, 60, 180))
    return img


if __name__ == "__main__":
    print("Generating cv-06 samples...")
    save(street_scene(), "sample_street.jpg")
    save(indoor_scene(), "sample_indoor.jpg")
    save(parking_lot(), "sample_parking.jpg")
    save(park_scene(), "sample_park.jpg")
    print("Done — 4 images in samples/")
