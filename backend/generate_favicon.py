from PIL import Image, ImageDraw

# Create a blank square image (256x256)
favicon_size = 256
image = Image.new("RGBA", (favicon_size, favicon_size), color=(255, 255, 255, 0))

# Draw an upward arrow (trading icon)
draw = ImageDraw.Draw(image)
arrow_color = (34, 139, 34, 255)  # Green color
draw.polygon([(128, 20), (180, 100), (140, 100), (140, 236), (116, 236), (116, 100), (76, 100)], fill=arrow_color)

# Save as favicon.ico (ICO format)
favicon_path = "static/favicon.ico"
image.save(favicon_path, format="ICO")

print(f"Favicon generated and saved at: {favicon_path}")
