import os

# Set directory path
directory = r"C:/Users/rodri/Downloads/TareasIA\dataset/Model_S"

# Common image extensions
image_extensions = ('.jpg', '.jpeg', '.png', '.gif', '.bmp')

# Iterate through files
for filename in os.listdir(directory):
    # Check if file contains 'custom' and is an image
    if 'custom' in filename.lower() and filename.lower().endswith(image_extensions):
        file_path = os.path.join(directory, filename)
        try:
            os.remove(file_path)
            print(f"Deleted: {filename}")
        except Exception as e:
            print(f"Error deleting {filename}: {e}")

print("Finished deleting custom images")