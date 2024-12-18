import os
from PIL import Image

# Define the directory path
directory = 'C:/Users/rodri/Downloads/tesla_data'
# Initialize the counter
image_count = 0
all_images_50x50x3 = True

# Loop through all files in the directory
for filename in os.listdir(directory):
    if filename.endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
        image_count += 1
        image_path = os.path.join(directory, filename)
        with Image.open(image_path) as img:
            width, height = img.size
            channels = len(img.getbands())
            if width != 50 or height != 50 or channels != 3:
                print(f"Image {filename} does not have dimensions 50x50x3. Its dimensions are {width}x{height}x{channels}. Deleting the image.")
                all_images_50x50x3 = False

# Print the total number of images
print(f"Total number of images: {image_count}")

# Print if all images have dimensions 50x50x3
if all_images_50x50x3:
    print("All images have dimensions 50x50x3.")
else:
    print("Not all images have dimensions 50x50x3.")