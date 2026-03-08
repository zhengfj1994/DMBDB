import os
import concurrent.futures
from openai import OpenAI

# The DeepSeek model is invoked using the compatible OpenAI API format. Therefore, the OpenAI client library is used and the base_url of DeepSeek is specified.
api_key = 'Please replace your API key.'
client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")


def remove_bom_from_filename(filename):  
    "Remove the BOM characters from the file name." ""
    return filename[1:] if filename.startswith('\ufeff') else filename


def sanitize_filename(name):
    return name.replace('/', '_').replace('\\', '_').replace(':', ' ').replace('*', '').replace('"', '').replace('<', '').replace('>', '').replace('?', '').replace('|', '')


def extract_marker_evidence_from_paper(context: str, marker: str):

# === System Prompt words ===
    system_prompt = """
You are an expert curator of dietary biomarker literature.

Your role is to extract exact textual evidence from scientific papers.

GLOBAL RULES:
1. Copy ONLY text that appears verbatim in the provided paper.
2. Do NOT summarize, paraphrase, interpret, or rewrite content.
3. Do NOT generate new information or infer unstated relationships.
4. The extracted text MUST contain the exact biomarker name provided.
5. Extract ONLY complete sentences or complete paragraphs.
6. The extracted text MUST provide descriptive, contextual, methodological,
   quantitative, or biological information about the biomarker.
7. Mentions where the biomarker appears only in lists, tables, figures,
   captions, headings, or titles are INVALID.
8. If multiple consecutive sentences in the same paragraph describe the biomarker,
   extract the entire paragraph.
9. Extract ALL valid text segments that meet the criteria, not just a single example.
10. Prefer richer contextual descriptions, but DO NOT exclude short,
    information-dense sentences that clearly describe the biomarker.
    """
# === User Prompt words ===
    user_prompt = """
TASK:
Extract ALL verbatim text segments from the following paper that explicitly
mention the biomarker "{biomarker_name}".

VALID TEXT SEGMENTS MUST:
- Contain the exact biomarker name "{biomarker_name}".
- Be a complete sentence or a complete paragraph.
- Describe, characterize, measure, quantify, or contextualize the biomarker,
  including analytical methods or sample context.

INVALID SEGMENTS:
- Simple compound name listings.
- Tables, figures, captions, headings.
- Standalone chemical names without descriptive context.

OUTPUT:
- Return ONLY the extracted text segments.
- Preserve original wording and formatting.
- Do NOT merge text from different locations or paragraphs.
- Do NOT add explanations or commentary.
- If no valid segment exists, return exactly:
---


TEXT:
{sample_text}

"""
    current_user_prompt = user_prompt.format(
    biomarker_name=marker,
    sample_text=context
)
    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": current_user_prompt},
            ],
            temperature=0.0,
            timeout=120,
        )
        # Get the output from the API response
        return response.choices[0].message.content.strip()

    except Exception as e:
        print(f"Error extracting evidence for biomarker '{marker}': {e}")
        return None



def process_line(line, papers_folder, output_folder):
    if ':' not in line:
        print(f"Skipping line without ':' separator: {line}")
        return

    try:
        paper_name, markers = line.split(':', 1)
        paper_name, markers = paper_name.strip(), markers.strip()

        marker_list = [marker.strip() for marker in markers.split('||')]


        paper_name = remove_bom_from_filename(paper_name)
        
        paper_path = os.path.join(papers_folder, paper_name)

        if not os.path.exists(paper_path):
            if not paper_name.lower().endswith('.txt'):
                paper_path_with_ext = os.path.join(papers_folder, paper_name + '.txt')
                if os.path.exists(paper_path_with_ext):
                    paper_path = paper_path_with_ext
                    paper_name = paper_name + '.txt'
                else:
                    print(f"Warning: Paper {paper_name} not found at {paper_path}, skipping.")
                    return
            else:
                print(f"Warning: Paper {paper_name} not found at {paper_path}, skipping.")
                return

        with open(paper_path, 'r', encoding='utf-8-sig') as paper_file:
            context = paper_file.read()

        for marker in marker_list:
            try:
                relevant_description = extract_marker_evidence_from_paper(context, marker)
                if not relevant_description:
                    print(f"No relevant description found for marker {marker} in {paper_name}, skipping file output.")
                    continue

                safe_marker_name = sanitize_filename(marker)
                output_filename = f"{safe_marker_name}_{paper_name}"
                output_file_path = os.path.join(output_folder, output_filename)

                with open(output_file_path, 'w', encoding='utf-8-sig') as output_file:
                    output_file.write(f"Paper: {paper_name}\n")
                    output_file.write(f"{marker}: {relevant_description}\n")

                print(f"Saved description for biomarker {marker} in {output_file_path}")
            except Exception as e:
                print(f"Error processing marker {marker} for {paper_name}: {e}")

    except ValueError:
        print(f"Skipping line due to incorrect format: {line}")


def extract_marker_descriptions(txt_file_path, papers_folder, output_folder):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    with open(txt_file_path, 'r', encoding='utf-8') as file:
        lines = [line.strip() for line in file if line.strip()]

    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(process_line, line, papers_folder, output_folder) for line in lines]
        concurrent.futures.wait(futures)


# === Set input and output paths ===
txt_file_path = ''
papers_folder = ''
output_folder = ''

# Run Code
extract_marker_descriptions(txt_file_path, papers_folder, output_folder)
