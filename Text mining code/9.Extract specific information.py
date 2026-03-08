import os
import concurrent.futures
from collections import defaultdict
from openai import OpenAI  # pip install openai
import time
import random

# The DeepSeek model is invoked using the compatible OpenAI API format. Therefore, the OpenAI client library is used and the base_url of DeepSeek is specified.
client = OpenAI(
    api_key="Please replace your API key.", 
    base_url="https://api.deepseek.com")

# === Set input and output paths ===
input_folder_path = '' 
output_markdown_path = '' 

# === System Prompt words ===
system_prompt = """
You are an expert in dietary biomarker curation and nutritional metabolomics.

Your role is to extract structured information about dietary biomarkers
from scientific texts, following strict methodological rules.

GLOBAL RULES:
- Use ONLY information explicitly stated in the provided text.
- Do NOT infer, speculate, or rely on external knowledge.
- Do NOT fill in missing information.
- When information for a required field is absent, output "-" for that field.

NAMING RULES:
- Use the full chemical name of the biomarker.
- If both a full name and an abbreviation are present, use ONLY the full name.
- Remove abbreviations shown in parentheses.
  Example:
  "3-(3,5-dihydroxyphenyl)-propanoic acid (DHPPA)"
  → "3-(3,5-dihydroxyphenyl)-propanoic acid"

OUTPUT CONSTRAINTS:
- Output ONLY the requested table.
- Do NOT include explanations, comments, or extra text.
- Each document may produce at most ONE consolidated row.

"""

# === User Prompt words ===
user_prompt = """
TASK:
Extract structured information about the dietary biomarker "{biomarker_name}"
from the text below.

OUTPUT FORMAT:
Return a table with EXACTLY the following columns:

| Food Source | Biological Sample | Analytic Procedure | Literature name |

FIELD DEFINITIONS:
- Food Source: Food item(s), food group(s), or nutrient intake explicitly linked to the biomarker.
- Biological Sample: Biological material used for measurement (e.g., urine (24 h), plasma).
- Analytic Procedure: Analytical method explicitly stated in the text.
- Literature name: Paper identifier explicitly mentioned (e.g., PMC7525000, ID1001). Do NOT include ".txt".

SPECIAL RULES:
- If multiple text fragments describe the same biomarker, consolidate them into ONE row.
- Normalize analytical method names to plain text.
- Remove LaTeX or mathematical formatting from method names.

TEXT:
{sample_text}

"""


def parse_md_row(line):
    parts = [cell.strip() for cell in line.strip().strip("|").split("|")]

    if len(parts) != 4:
        return None
        
    return dict(zip([
        "Food Source", "Biological Sample", 
        "Analytic Procedure", "Literature name"
    ], parts))


def merge_fields(val1, val2):
    values = set()
    for val in [val1, val2]:
        if val != "-":
            values.update([v.strip() for v in val.split(";") if v.strip()])
    return "; ".join(sorted(values)) if values else "-"


def process_file(txt_file):
    try:
        input_file_path = os.path.join(input_folder_path, txt_file)

        try:
            with open(input_file_path, 'r', encoding='utf-8-sig') as f:
                sample_text = f.read()
        except Exception as e:
            print(f"Error reading file {txt_file}: {e}")
            return []

  
        
        lines = sample_text.strip().split('\n')
        for line in lines:
            line = line.strip()
            if not line: continue
            if line.startswith("Paper:"): continue
            

            if ": " in line:
                biomarker_name = line.split(": ", 1)[0].strip()
                break
        
        if not biomarker_name:
            filename_no_ext = os.path.splitext(txt_file)[0]
            if "_" in filename_no_ext:
                biomarker_name = filename_no_ext.rsplit("_", 1)[0]
            else:
                biomarker_name = filename_no_ext

        current_user_prompt = user_prompt.format(biomarker_name=biomarker_name, sample_text=sample_text)

        max_retries = 5 
        response = None
        for attempt in range(max_retries):
            try:
                response = client.chat.completions.create(
                    model="deepseek-chat",
                    messages=[
                        {'role': 'system', 'content': system_prompt},
                        {'role': 'user', 'content': current_user_prompt},
                    ],
                    temperature=0.0,
                    timeout=120,
                )
                break
            except Exception as e:
                if attempt < max_retries - 1:
                    sleep_time = 2 * (attempt + 1) + random.uniform(0, 1)
                    # print(f"Retry {attempt+1}/{max_retries} for {txt_file} due to error: {e}. Sleeping {sleep_time:.2f}s...")
                    time.sleep(sleep_time)
                else:
                    print(f"Failed to process {txt_file} after {max_retries} attempts.")
                    return []
        
        if not response:
            return []

        try:
            output = response.choices[0].message.content

            grouped = defaultdict(lambda: {
                "Food Source": "-",
                "Biological Sample": "-",
                "Analytic Procedure": "-",
                "Literature name": "-"
            })

            lines = output.strip().split('\n')
            for line in lines:
                if line.startswith("|") and not line.startswith("| Food Source") and "---" not in line:
                    parsed = parse_md_row(line)
                    if not parsed:
                        continue
                    
                    key = parsed["Literature name"]
                    for field in parsed:
                        grouped[key][field] = merge_fields(grouped[key][field], parsed[field])

            file_rows = []
            for g in grouped.values():
                if all(str(val).strip() in ["-", ""] for val in g.values()):
                    continue
               
                md_row = "|" + "|".join([biomarker_name.strip()] + [g[field] for field in [
                    "Food Source", "Biological Sample", 
                    "Analytic Procedure", "Literature name"
                ]]) + "|"
                file_rows.append(md_row)

            print(f"Processed file: {txt_file}")
            return file_rows

        except Exception as e:
            print(f"Error calling API for file {txt_file}: {e}")
            return []

    except Exception as e:
        print(f"Unexpected error processing file {txt_file}: {e}")
        return []


def main():
    if not os.path.exists(input_folder_path):
        print(f"Input folder not found: {input_folder_path}")
        return

    txt_files = [f for f in os.listdir(input_folder_path) if f.endswith('.txt')]

    table_header = "|Biomarker Name|Food Source|Biological Sample|Analytic Procedure|Literature name|\n|---|---|---|---|---|\n"
    all_rows = []

    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        future_to_file = {executor.submit(process_file, txt_file): txt_file for txt_file in txt_files}

        for future in concurrent.futures.as_completed(future_to_file):
            txt_file = future_to_file[future]
            try:
                rows = future.result()
                if rows:
                    all_rows.extend(rows)
            except Exception as exc:
                print(f'{txt_file} generated an exception: {exc}')

    markdown_content = table_header
    markdown_content += "\n".join(all_rows)

    try:
        with open(output_markdown_path, 'w', encoding='utf-8-sig') as f:
            f.write(markdown_content)
        print(f"All results saved to {output_markdown_path}")
    except Exception as e:
        print(f"Error writing to output file: {e}")


if __name__ == "__main__":
    main()