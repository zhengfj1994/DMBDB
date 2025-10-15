from openai import OpenAI  # for calling the OpenAI API
import os  # for getting API token from env variable OPENAI_API_KEY

# create a list of models
GPT_MODELS = ["deepseek-chat"]
# models
EMBEDDING_MODEL = "text-embedding-3-small"

# Define the folder path where the .txt files are stored
folder_path = r''
output_path = r''

# Get the list of all .txt files in the folder
txt_files = [f for f in os.listdir(folder_path) if f.endswith('.txt')]


# Initialize OpenAI client

client = OpenAI(api_key=" ", base_url="https://api.deepseek.com")
# Iterate through all .txt files in the folder
for txt_file in txt_files:
    try:
        input_file_path = os.path.join(folder_path, txt_file)

        # Read the content of the current file
        with open(input_file_path, 'r', encoding='utf-8-sig') as f:
            sample_text = f.read()

        # Extract the filename without extension for output
        file_name_without_extension = os.path.splitext(txt_file)[0]

        # Construct output file path
        output_file_path = os.path.join(output_path, f'{file_name_without_extension}.txt')

        # Prepare the prompt
        prompt = f"""
You are an expert in the field of dietary biomarkers and food components.
Please read the text inside the triple curly braces and extract only the dietary-related biomarkers present in the text.

1.Explanation of Dietary Biomarkers:
- Dietary biomarkers refer to changes in metabolic products in the body that occur after the intake of specific foods or nutrients, which can reflect food intake or nutritional status. These biomarkers include the food components themselves or substances produced during the body's metabolic process.

2. Extraction Requirements
(1) Accurate Information to Extract:
- The extraction of dietary biomarkers should comply with the explanation provided in "Explanation of Dietary Biomarkers".
- Extract biomarkers related to dietary components.
- If certain metabolites significantly increase after the intake of specific foods (e.g., choline, betaine, methionine increase after beef consumption), these metabolites can be considered associated with the food.
- If certain foods (e.g., protein) show a strong or significant correlation with specific metabolites (e.g., p-cresyl sulfate, phenylacetylglutamine, indoxyl sulfate, taurine, alanine), extract this relationship as well.
- Exclude biomarkers related to diseases (e.g., N-terminal pro-B-type natriuretic peptide, disease-related markers).
- The names of dietary biomarkers should not merely consist of numbers and symbols, such as 18:0 or 22:5n-6. They must include the full names, such as fatty acid 18:3 (n-3),palmitoleic (16:1n-7),myristoleic (14:1n-5) ,etc.
- Just output the dietary biomarkers and nothing else. For instance, "13C in serum" is incorrect. There is no need for "in serum", just "13C" is sufficient.


(2) Output Format:
- Output the extracted dietary biomarker names in a table format with only the "Biomarker Name" column.

(3) Extraction Details:
- Ensure Accuracy: Only extract dietary biomarkers or metabolites explicitly mentioned in the literature.
- Handle Missing Data: If certain data points are missing or not mentioned, return "-".
- Exclude Non-Dietary Related Biomarkers: Such as Hemoglobin, Albumin, Interleukin, TNF-α,IBA1, insulin, IL-6,etc.
- Exclude all disease-related biomarkers.
  

(4) Important Notes:
- Do not speculate or fill in information that is not explicitly stated in the literature.
- Only include the biomarker names in the output, without additional explanations or comments.
- If the content in the literature is empty ,Please do not generate any dietary biomarker.  
- Do not generate any dietary biomarkers that are not mentioned in the literature.

```
Biomarker Name
----------------
Trimethylamine N-oxide (TMAO)
Phenylacetylglutamine
Dimethylglycine (DMG)
Proline betaine
```
________________________________________
文本内容：
{sample_text}
"""

        # Call the OpenAI API to process the prompt
        response = client.chat.completions.create(
            messages=[
                {'role': 'system', 'content': 'You are an expert in the field of diet and nutrition, specializing in dietary biomarkers and food components.'},
                {'role': 'user', 'content': prompt},
            ],
            model=GPT_MODELS[0],
            timeout=120,
            temperature=0.0


        )

        # Get the output from the API response
        output = response.choices[0].message.content

        # Write the output to the output file
        with open(output_file_path, 'w', encoding='utf-8-sig') as f:
            f.write(output)

        print(f"Output written to {output_file_path}")

    except Exception as e:
        print(f"Error processing {txt_file}: {e}")
        continue  # Skip the current file and move on to the next one
