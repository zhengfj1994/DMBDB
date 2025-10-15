import os
import concurrent.futures
from openai import OpenAI

# Set OpenAI API Key
api_key = ''
client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")


def remove_bom_from_filename(filename):

    return filename[1:] if filename.startswith('\ufeff') else filename


def sanitize_filename(name):

    return name.replace('/', '_').replace('\\', '_').replace(':', ' ').replace('*', '')


def generate_marker_description_from_paper(context, marker):
    "Use the OpenAI API to extract the descriptive segments related to dietary markers mentioned in the literature."
    prompt = f"""
    -Please extract all the relevant text related to '{marker}' mentioned in the following paper. 
    -Do not generate any new content, just return the parts that mention the marker in the paper. 
    -The content needs to contain as much descriptive information as possible. 
    -The response should be in English.

    \n\n{context}"""

    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {'role': 'system', 'content': 'You are an expert in diet and nutrition, specializing in dietary biomarkers and food components.'},
                {'role': 'user', 'content': prompt}
            ],
            temperature=0,
            timeout=120
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Error generating description for {marker}: {e}")
        return None


def process_line(line, papers_folder, output_folder):

    if ':' not in line:
        print(f"Skipping line without ':' separator: {line}")
        return

    try:
        paper_name, markers = line.split(':', 1)
        paper_name, markers = paper_name.strip(), markers.strip()


        marker_list = [marker.strip() for marker in markers.split('||')]

        paper_path = os.path.join(papers_folder, paper_name)

        if not os.path.exists(paper_path):
            print(f"Warning: Paper {paper_name} not found, skipping.")
            return
        paper_name = remove_bom_from_filename(paper_name)

        # 读取文献内容（避免重复读取）
        with open(paper_path, 'r', encoding='utf-8-sig') as paper_file:
            context = paper_file.read()

        for marker in marker_list:
            try:
                relevant_description = generate_marker_description_from_paper(context, marker)
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



txt_file_path = ''
papers_folder = ''
output_folder = ''

extract_marker_descriptions(txt_file_path, papers_folder, output_folder)
