import requests
import os
import pandas as pd

# Load the CSV file
file_path = r''  # Replace with the actual path to your CSV
data = pd.read_excel(file_path)

# Directory where files will be saved
output_dir = r''
os.makedirs(output_dir, exist_ok=True)

# Iterate over each URL in the 'V5' column
for idx, row in data.iterrows():
    url = row['V5']
    pmid = row['PMCID']

    # Ensure there is a valid PMID value
    if pd.notna(pmid):
        try:
            # Send GET request to the URL
            response = requests.get(url, stream=True)

            # Ensure the request was successful
            if response.status_code == 200:
                # Use PMID for the filename and save with a .tar.gz extension
                filename = os.path.join(output_dir, f"{pmid}.tar.gz")

                # Write the content to a tar.gz file
                with open(filename, 'wb') as file:
                    for chunk in response.iter_content(1024):
                        file.write(chunk)
                print(f"Downloaded: {filename}")
            else:
                print(f"Failed to download from {url}, status code {response.status_code}")
        except Exception as e:
            print(f"Error downloading {url}: {e}")
    else:
        print(f"Skipping row {idx + 1} due to missing PMID")

print("All downloads completed.")
