import tarfile
import os

# Directory where the .tar.gz files are located
input_dir = r'' # Replace with your directory containing the .tar.gz files
# Directory where the files will be extracted
output_dir = r''
os.makedirs(output_dir, exist_ok=True)

# Iterate through the .tar.gz files in the input directory
for filename in os.listdir(input_dir):
    if filename.endswith(".tar.gz"):
        file_path = os.path.join(input_dir, filename)
        try:
            # Open the tar.gz file
            with tarfile.open(file_path, 'r:gz') as tar:
                # Extract all contents to the output directory
                tar.extractall(path=output_dir)
                print(f"Extracted: {filename}")
        except Exception as e:
            print(f"Error extracting {filename}: {e}")

print("All files extracted.")
