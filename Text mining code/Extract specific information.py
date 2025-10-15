import os
from openai import OpenAI  # pip install openai
import collections

# === Initialize OpenAI client ===
client = OpenAI(
    api_key="",  # <-- Please replace with your own KEY
    base_url="https://api.deepseek.com")

input_folder_path = r''  # Input Folder: Each .txt file represents a description of a dietary marker.
output_markdown_path = r''

txt_files = [f for f in os.listdir(input_folder_path) if f.endswith('.txt')]

# === Prompt Template ===
PROMPT_TEMPLATE = """
You are an expert in the field of dietary biomarkers and food components. Please read the text inside the triple curly braces and extract the relevant information about the dietary biomarker "{biomarker_name}":


1. Output Format:
   Output the extracted information in a table format with the following columns:
   - Biomarker Name
   - Food Source
   - Sample Size
   - Biological Sample
   - Analytic Procedure
   - Literature name



2.Detailed Explanation for Each Output Element:
	-Biomarker Name: The exact name of the dietary biomarker or metabolite mentioned in the literature. If both a full name and abbreviation are provided, use the full name.
	-Food Source: The food item(s) that intake correlates with or leads to a significant increase in the biomarker (e.g., beef, protein intake). If no food source is mentioned, omit this element.
	-Sample Size: The biomarker together with sample size info (e.g.,17 subjects,107 participants). If sample size is not provided, return "-".
	-Biological Sample: The type of sample used for measurement (e.g., Urine(24hr),Urine (fasting),Plasma). If unavailable, return "-".
	-Analytic Procedure: The method used for analysis (e.g., HPLC, FT-ICR-MS). If not mentioned, return "-".
    -Literature name: The ID or name of the paper, e.g., PMC7525000,ID1001. Always fill this with the correct paper ID. do not contain ".txt".



3. Extraction Details:
   - Ensure Accuracy: Only extract information explicitly mentioned in the literature.
   - Handle Missing Data: If certain data points are missing or not mentioned, return "-".
   - Allow Partial Output: If only some fields are mentioned, output just those fields.
   - Remove the abbreviations of the markers, that is, the content within the parentheses,For example, remove (DHPPA) from 3-(3,5-dihydroxyphenyl)-propanoic acid (DHPPA).
   - If there is no specific description fragment of the dietary marker in the document, then this dietary marker should not be output in the result and can be skipped directly.

4. Important Notes:
   - Avoid Speculation: Do not fill in information that is not stated.
   - No Additional Commentary: Output only the table without extra explanations.
   - The output result of a document must be one piece of information. If there are multiple pieces, they should be consolidated into one.



----------------------------------------------------------------------------------------

文本内容：
{{{sample_text}}}
"""

# === Initialize Markdown Header ===
table_header = "| Biomarker Name | Food Source| Sample Size | Biological Sample  | Analytic Procedure | Literature name |\n"
table_rows = []

for txt_file in txt_files:
    try:
        input_file_path = os.path.join(input_folder_path, txt_file)


        biomarker_name = txt_file.replace("_description.txt", "")


        try:
            with open(input_file_path, 'r', encoding='utf-8') as f:
                sample_text = f.read()
        except Exception as e:
            print(f"Error reading file {txt_file}: {e}")
            continue


        prompt = PROMPT_TEMPLATE.format(biomarker_name=biomarker_name, sample_text=sample_text)

        # Calling the OpenAI API
        try:
            response = client.chat.completions.create(
                messages=[
                    {'role': 'system',
                     'content': 'You are an expert in the field of diet and nutrition, specializing in dietary biomarkers and food components.'},
                    {'role': 'user', 'content': prompt},
                ],
                model="deepseek-chat",
                temperature=0,
                timeout=120
            )


            output = response.choices[0].message.content


            from collections import defaultdict


            def parse_md_row(line):

                parts = [cell.strip() for cell in line.strip().strip("|").split("|")]
                if len(parts) != 6:
                    return None
                return dict(zip([
                    "Biomarker Name",  "Food Source", "Sample Size",
                    "Biological Sample", "Analytic Procedure", "Literature name"
                ], parts))


            def merge_fields(val1, val2):

                values = set()
                for val in [val1, val2]:
                    if val != "-":
                        values.update([v.strip() for v in val.split(";") if v.strip()])
                return "; ".join(sorted(values)) if values else "-"



            grouped = defaultdict(lambda: {
                "Biomarker Name": "-",
                "Food Source": "-",
                "Sample Size": "-",
                "Biological Sample": "-",
                "Analytic Procedure": "-",
                "Literature name": "-"
            })

            lines = output.strip().split('\n')
            for line in lines:
                if line.startswith("|") and not line.startswith("| Biomarker Name"):
                    parsed = parse_md_row(line)
                    if not parsed:
                        continue
                    key = (parsed["Biomarker Name"], parsed["Literature name"])
                    for field in parsed:
                        grouped[key][field] = merge_fields(grouped[key][field], parsed[field])


            for g in grouped.values():
                md_row = "| " + " | ".join(g[field] for field in [
                    "Biomarker Name","Food Source", "Sample Size",
                    "Biological Sample", "Analytic Procedure",  "Literature name"
                ]) + " |"
                table_rows.append(md_row)

            print(f"Processed file: {txt_file}")
        except Exception as e:
            print(f"Error calling API for file {txt_file}: {e}")
            continue
    except Exception as e:
        print(f"Unexpected error processing file {txt_file}: {e}")
        continue

# Merge all table rows
markdown_content = table_header
markdown_content += "\n".join(table_rows)

# Write the results into a Markdown file
try:
    with open(output_markdown_path, 'w', encoding='utf-8-sig') as f:
        f.write(markdown_content)
    print(f"All results saved to {output_markdown_path}")
except Exception as e:
    print(f"Error writing to output file: {e}")