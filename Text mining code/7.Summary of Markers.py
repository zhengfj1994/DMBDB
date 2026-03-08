import os

def extract_biomarkers_from_code_block(lines):
    extracted = []
    for line in lines:
        line = line.strip()
        if line and line != "Biomarker Name" and line != "-" and line !='```' and line !="":
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
                print(f" File not found: {file_path}")
    return biomarkers, total_biomarkers, total_files

def main(biomarker_folder, output_file):
    biomarkers, total_biomarkers, total_files = load_biomarkers_from_folder(biomarker_folder)


    with open(output_file, 'w', encoding='utf-8-sig') as output:
        for filename, count, biomarker_list in biomarkers:
            for biomarker in biomarker_list:
                output.write(f"{filename}: {biomarker}\n")


output_file = ''
biomarker_folder = ''
main(biomarker_folder, output_file)
