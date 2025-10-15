import pandas as pd

# Read Markdown files and process formatting
file_path = r''

with open(file_path, 'r', encoding='utf-8-sig') as file:
    markdown_content = file.read()


rows = markdown_content.split('\n')

rows = [row.strip() for row in rows if row.strip()]


header = rows[0].split('|')[1:-1]

data = []
for row in rows[1:]:

    if '|' in row and not all(c in ['-', ' ', '|'] for c in row.strip()):
        data.append(row.split('|')[1:-1])

# Create DataFrame
df = pd.DataFrame(data, columns=header)

# Save as CSV file
csv_file_path = r''

df.to_csv(csv_file_path, index=False, encoding='utf-8-sig')

print(f"CSV file has been saved：{csv_file_path}")
