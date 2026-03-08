from openai import OpenAI  # for calling the OpenAI API
import os  # for getting API token from env variable OPENAI_API_KEY
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
import time

# create a list of models
DeepSeek_MODELS = ["deepseek-chat"]


# Define the folder path where the .txt files are stored
folder_path = ''
output_path = ''

# Get the list of all .txt files in the folder
txt_files = [f for f in os.listdir(folder_path) if f.endswith('.txt')]


# Initialize OpenAI client
# The DeepSeek model is invoked using the compatible OpenAI API format. Therefore, the OpenAI client library is used and the base_url of DeepSeek is specified.
client = OpenAI(api_key="Please replace your API key.", base_url="https://api.deepseek.com")

# System Prompt Words 
system_prompt= """
You are an expert in dietary biomarkers and nutritional metabolomics.

Your task is to extract ONLY valid dietary-related biomarker NAMES
explicitly mentioned in the text enclosed within triple curly braces {{{ }}}.

You MUST strictly follow ALL rules below.
Any deviation is considered an error.

────────────────────────
1. Definition (STRICT)
────────────────────────

A dietary biomarker MUST be: 

- A specific, chemically defined compound (or a clearly defined conjugated derivative), AND 
- Explicitly described in the text as reflecting: 
dietary intake, food consumption, or intake of normal food-derived constituents.

 “Dietary exposure” is valid ONLY when it arises from 
normal food components or food-derived compounds. 
Environmental contamination 
or chemical residues are NOT considered dietary biomarkers. 

If dietary relevance is NOT explicitly stated in the text, 
the compound MUST NOT be extracted.
────────────────────────
Explicit Exclusion (CRITICAL)
────────────────────────

Endogenous compounds MUST NOT be extracted if they are
primarily described as:

- disease-related biomarkers,
- inflammatory mediators,
- immune-related molecules,
- hormones or hormone-like regulators,
- or core signaling molecules,

EVEN IF the text states that they are
"diet-associated", "diet-modulated",
or "affected by diet".

────────────────────────
2. Mandatory Inclusion Conditions
────────────────────────

Extract a biomarker ONLY IF ALL of the following are true:

- The compound name appears explicitly in the text, AND
- The text explicitly links the compound to diet,
  dietary intake, food consumption,
  or dietary exposure.

Do NOT infer dietary relevance
from general biochemical knowledge.

────────────────────────
3. Mandatory Exclusion Rules (HARD FILTER)
────────────────────────

You MUST NOT extract ANY of the following,
even if mentioned:

A. Clinical or disease-related biomarkers
Compounds primarily used as indicators of disease,
organ dysfunction, or clinical diagnosis
(e.g., CRP, creatinine, ammonia)
MUST NOT be extracted,


B. Inflammatory, immune, or signaling molecules
   (e.g., prostaglandin, eicosanoid, cytokine,
    interleukin, TNF-alpha, IL-6)

C. Hormones or hormone-like regulators
   (e.g., insulin, cortisol, estrogen, testosterone)

D. Foods, food groups, nutrients, or dietary variables
   described only as intake components
   (e.g., protein, fiber, fruits, vegetables, alcohol)

E. Sample type, tissue, or matrix–qualified terms
   (e.g., plasma vitamin C, serum folate, urinary nitrogen)

   HARD RULE:
   - Any extracted name containing sample or matrix words
     (plasma, serum, urine, blood, erythrocyte,
      fecal, stool) is INVALID.
   - Output ONLY the pure chemical entity name.
   - If the chemical entity cannot be cleanly separated,
     DO NOT extract it.

F. Physical, analytical, or measurement-based indicators
   (e.g., isotope ratios, CIR, NMR signals)

G. Lipid / fatty-acid formatting rules:

EXCLUDE:
- Generic lipid class terms without molecular specificity
  (e.g., TAGs, phospholipids, cholesteryl esters)

EXCLUDE:
- Fatty acids or lipids written ONLY as numeric codes
  without chemical name or abbreviation
  (e.g., 15:0, 18:0, C15:0)

ALLOW:
- Lipid species or fatty acids with explicit chemical names
  or lipid-class abbreviations
  (e.g., oleic acid, eicosapentaenoic acid,
   C54:4 TAG, C20:5 CE, C15:0 FA)

H. Broad or collective categories
   rather than single compounds
   (e.g., amino acids, branched-chain amino acids,
    carotenoids, indoles)

I. Abbreviations or acronyms
   UNLESS explicitly defined in the text
   as a specific chemical compound.

J. Environmental or non-food chemicals
EXCLUDE:
- Environmental contaminants, personal-care chemicals,
  packaging migrants, or plastic-related compounds
  (e.g., parabens, triclosan, benzophenone-3,
   phthalate metabolites),
  even if exposure occurs via food.
 
K. Aggregate or total measures
EXCLUDE:
- Any biomarker expressed as a total, sum, or bulk measure
  (e.g., total cholesterol, total protein, total lipids).


────────────────────────
4. Allowed Chemical Entities
────────────────────────

You MAY extract, if ALL rules are satisfied:

- Vitamins and vitamers
- Polyphenols and phytochemicals
- Chemically defined fatty acids and lipid species
- Gut microbial metabolites derived from diet
- Endogenous metabolites associated with diet
  that are NOT inflammatory, immune, hormonal,
  or disease-related
- Conjugated metabolites
  (e.g., sulfates, glucuronides,
   amino-acid conjugates)

────────────────────────
5. Output Rules (ABSOLUTE)
────────────────────────

- Output MUST be plain text.
- The FIRST line MUST be exactly:

Biomarker Name

- Each subsequent line MUST contain exactly ONE biomarker name.
- Each biomarker name MUST appear ONLY ONCE,
  even if mentioned multiple times.
- NO explanations, NO commentary,
  NO bullets, NO numbering.
- NO empty lines.

────────────────────────
6. No-Biomarker Case (STRICT)
────────────────────────

ONLY IF the text contains ZERO valid biomarkers,
output EXACTLY:

Biomarker Name
-

If at least ONE biomarker is extracted,
you MUST NOT output "-".

────────────────────────
7. Final Instruction
────────────────────────

Return ONLY the output described above.
Return NOTHING else.


"""

def process_single_file(txt_file):
    "Functions for processing a single file"
    try:
        input_file_path = os.path.join(folder_path, txt_file)

        # Read the content of the current file
        with open(input_file_path, 'r', encoding='utf-8-sig') as f:
            sample_text = f.read()

        # Extract the filename without extension for output
        file_name_without_extension = os.path.splitext(txt_file)[0]

        # Construct output file path
        output_file_path = os.path.join(output_path, f'{file_name_without_extension}.txt')

# === User Prompt words ===
        user_prompt = """
TASK:
Extract dietary-related biomarker NAMES from the following text.

OUTPUT REQUIREMENTS (STRICT):
- Output ONLY biomarker names.
- Do NOT output explanations, comments, headings, tables, symbols, or any other text.
- Do NOT include sample type, biological matrix, units, or descriptors.
- Do NOT repeat the same biomarker name.

OUTPUT FORMAT:
- Plain text only.
- The FIRST line MUST be exactly:
Biomarker Name
- Each subsequent line MUST contain exactly ONE biomarker name.

NO-BIOMARKER CASE:
If ZERO dietary-related biomarkers are found, output EXACTLY:
Biomarker Name
-
              
TEXT:
{sample_text}
        """
        current_user_prompt = user_prompt.format(sample_text=sample_text)
        response = client.chat.completions.create(
            messages=[
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': current_user_prompt},
            ],
            model=DeepSeek_MODELS[0],
            timeout=120,
            temperature=0.0
        )
        # Get the output from the API response
        output = response.choices[0].message.content

        # Write the output to the output file
        with open(output_file_path, 'w', encoding='utf-8-sig') as f:
            f.write(output)

        return f"Success: {txt_file}"

    except Exception as e:
        return f"Error: {txt_file} - {str(e)}"

if __name__ == "__main__":
    max_workers = 2  
    delay_between_requests = 0.5 

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {}
        with tqdm(total=len(txt_files), desc="processing progress") as pbar:
            for txt_file in txt_files:
                futures[executor.submit(process_single_file, txt_file)] = txt_file
                time.sleep(delay_between_requests)  

            for future in as_completed(futures):
                result = future.result()
                if result.startswith("Error") or result.startswith("Skipped"):
                    tqdm.write(result)
                pbar.update(1)

