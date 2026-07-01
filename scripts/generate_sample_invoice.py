"""Generate a sample invoice image for testing."""
from PIL import Image, ImageDraw, ImageFont
import os

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "uploads")
os.makedirs(OUTPUT_DIR, exist_ok=True)


def generate_invoice():
    img = Image.new("RGB", (800, 1000), "white")
    draw = ImageDraw.Draw(img)

    try:
        font_title = ImageFont.truetype("arial.ttf", 36)
        font_header = ImageFont.truetype("arial.ttf", 24)
        font_body = ImageFont.truetype("arial.ttf", 18)
        font_small = ImageFont.truetype("arial.ttf", 14)
    except (OSError, IOError):
        font_title = ImageFont.load_default()
        font_header = font_title
        font_body = font_title
        font_small = font_title

    draw.text((50, 40), "INVOICE", fill="black", font=font_title)
    draw.text((50, 100), "TechSupply Co.", fill="darkblue", font=font_header)
    draw.text((50, 150), "123 Business Ave, Suite 100", fill="gray", font=font_small)
    draw.text((50, 175), "Cityville, ST 12345", fill="gray", font=font_small)
    draw.text((50, 200), "Phone: (555) 123-4567", fill="gray", font=font_small)

    draw.line([(50, 230), (750, 230)], fill="black", width=2)

    draw.text((50, 250), "Invoice #: INV-2024-0042", fill="black", font=font_body)
    draw.text((50, 280), "Date: 2024-03-15", fill="black", font=font_body)
    draw.text((50, 310), "Due Date: 2024-04-14", fill="black", font=font_body)

    draw.text((50, 360), "Bill To:", fill="black", font=font_body)
    draw.text((50, 390), "John Smith", fill="black", font=font_body)
    draw.text((50, 415), "Acme Corp", fill="black", font=font_small)
    draw.text((50, 440), "456 Oak Street", fill="black", font=font_small)
    draw.text((50, 465), "Metropolis, NY 10001", fill="black", font=font_small)

    draw.line([(50, 500), (750, 500)], fill="gray", width=1)

    headers = ["Item", "Qty", "Unit Price", "Total"]
    cols = [50, 350, 480, 620]
    for i, h in enumerate(headers):
        draw.text((cols[i], 520), h, fill="black", font=font_body)

    draw.line([(50, 550), (750, 550)], fill="black", width=2)

    items = [
        ("Laptop Stand", "2", "$45.00", "$90.00"),
        ("USB-C Hub", "1", "$35.00", "$35.00"),
        ("Wireless Mouse", "3", "$25.00", "$75.00"),
        ("Mechanical Keyboard", "1", "$89.99", "$89.99"),
    ]

    y = 570
    for item in items:
        for i, val in enumerate(item):
            draw.text((cols[i], y), val, fill="black", font=font_body)
        y += 40

    draw.line([(50, y + 10), (750, y + 10)], fill="gray", width=1)
    y += 40

    draw.text((480, y), "Subtotal:", fill="black", font=font_body)
    draw.text((620, y), "$289.99", fill="black", font=font_body)
    y += 35

    draw.text((480, y), "Tax (8.5%):", fill="black", font=font_body)
    draw.text((620, y), "$24.65", fill="black", font=font_body)
    y += 35

    draw.line([(470, y), (750, y)], fill="black", width=2)
    y += 10

    draw.text((480, y), "Grand Total:", fill="black", font=font_title)
    draw.text((580, y), "$314.64", fill="black", font=font_title)
    y += 50

    draw.text((50, y), "Payment Method: Visa **** 4242", fill="black", font=font_body)
    y += 35

    draw.text((50, y), "Payment Terms: Net 30", fill="black", font=font_small)

    path = os.path.join(OUTPUT_DIR, "sample_invoice.png")
    img.save(path)
    print(f"Sample invoice saved to: {path}")
    return path


if __name__ == "__main__":
    generate_invoice()
