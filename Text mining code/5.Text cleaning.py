import os
import re


folder_path = ''  
output_path = '' 

if not os.path.exists(output_path):
    os.makedirs(output_path)

def clean_and_save_file(file_path, output_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()

    ref_pattern = re.compile(r'(^|\n)#+\s*(References|Literature Cited|Bibliography|Acknowledgements|Acknowledgments).*', re.IGNORECASE | re.DOTALL)
    match = ref_pattern.search(content)
    if match:
        content = content[:match.start()]

    content = re.sub(r'!\[.*?\]\(.*?\)', '', content)

    content = re.sub(r'<img[^>]*>', '', content, flags=re.IGNORECASE)

    content = re.sub(r'\n\s*\n', '\n\n', content).strip()

    file_name = os.path.basename(file_path).replace('.md', '.txt')
    new_file_path = os.path.join(output_path, file_name)

    with open(new_file_path, 'w', encoding='utf-8') as new_file:
        new_file.write(content)

    print(f" process and save: {new_file_path}")


def process_all_md_files(folder_path):

    if not os.path.exists(folder_path):
        print(f" Error: Input folder '{folder_path}' does not exist ")
        return

    for file_name in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file_name)

        if file_name.endswith('.md'):
            clean_and_save_file(file_path, output_path)

if __name__ == "__main__":
    process_all_md_files(folder_path)
