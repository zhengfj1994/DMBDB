import os

# Folder path
folder_path = r''
output_path = r''


if not os.path.exists(output_path):
    os.makedirs(output_path)

def remove_references_from_md(file_path,output_path):

    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()

    # Search # Locate the position of the "References" title
    reference_start_index = content.lower().find("# references" or '# REFERENCES' or '# LITERATURE CITED' or 'References' or '# Literature Cited')

    if reference_start_index != -1:
        # Extract # Extract the content before "References" and delete the reference section.
        content = content[:reference_start_index]

    # Generate a new file name (change .md to .txt) and save it to the output folder
    file_name = os.path.basename(file_path).replace('.md', '.txt')
    new_file_path = os.path.join(output_path, file_name)

    # Save as txt file
    with open(new_file_path, 'w', encoding='utf-8') as new_file:
        new_file.write(content)

    print(f"Handle and store: {new_file_path}")


def process_all_md_files(folder_path):
    # Traverse all the files in the folder
    for file_name in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file_name)


        if file_name.endswith('.md'):
            remove_references_from_md(file_path,output_path)



process_all_md_files(folder_path)
