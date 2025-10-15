import os

def extract_biomarkers_from_code_block(lines):
    """
Extract the content between `...` and then filter out the names of dietary markers from it. """
    inside_block = False
    extracted = []
    for line in lines:
        line = line.strip()
        if line == "```":
            inside_block = not inside_block
            continue
        if inside_block:
            if line not in ["Biomarker Name", "----------------", "-", ""] and not line.startswith("#"):
                extracted.append(line)
    return extracted

def load_biomarkers_from_folder(biomarker_folder):

    biomarkers = []
    total_biomarkers = 0
    total_files = 0

    for filename in os.listdir(biomarker_folder):
        if filename.endswith('.txt'):
            file_path = os.path.join(biomarker_folder, filename)
            try:
                with open(file_path, 'r', encoding='utf-8-sig') as file:
                    lines = file.readlines()
                    file_biomarkers = extract_biomarkers_from_code_block(lines)
                    if file_biomarkers:
                        total_biomarkers += len(file_biomarkers)
                        total_files += 1
                        biomarkers.append((filename, len(file_biomarkers), file_biomarkers))
            except FileNotFoundError:
                print(f"file not found: {file_path}")
    return biomarkers, total_biomarkers, total_files

def main(biomarker_folder, output_file):
    biomarkers, total_biomarkers, total_files = load_biomarkers_from_folder(biomarker_folder)

    print(f"A total of {total_biomarkers} dietary markers were found.\n")
    print(f"A total of {total_files} text files are included.\n")
    print("\nThe number and names of dietary markers included in each file:\n")

    for filename, count, biomarker_list in biomarkers:
        print(f"\nfile {filename} contain {count} dietary markers：\n")


    # 输出结果写入文件
    with open(output_file, 'w', encoding='utf-8-sig') as output:
        for filename, count, biomarker_list in biomarkers:
            for biomarker in biomarker_list:
                output.write(f"{filename}: {biomarker}\n")


output_file = r''
biomarker_folder = r''
main(biomarker_folder, output_file)
