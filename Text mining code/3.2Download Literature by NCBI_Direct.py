import requests
import os
import pandas as pd
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm


INPUT_FILE = ''  
OUTPUT_DIR = ''  
MAX_WORKERS = 5 

os.makedirs(OUTPUT_DIR, exist_ok=True)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def get_oa_download_url(pmcid):
    api_url = "https://www.ncbi.nlm.nih.gov/pmc/utils/oa/oa.fcgi"
    try:
        response = requests.get(api_url, params={"id": pmcid}, timeout=10, headers=HEADERS)
        response.raise_for_status()
        
        root = ET.fromstring(response.content)
        
        pdf_url = None
        tgz_url = None
        
        for link in root.findall(".//link"):
            fmt = link.get("format")
            href = link.get("href")
            if fmt == "pdf":
                pdf_url = href
            elif fmt == "tgz":
                tgz_url = href
        final_url = pdf_url if pdf_url else tgz_url
        
        if final_url and final_url.startswith("ftp://"):
            final_url = final_url.replace("ftp://", "https://")
            
        return final_url
        
    except Exception as e:
        # print(f"Error getting URL for {pmcid}: {e}")
        return None

def download_single_pmc(row):

    pmcid = row.get('PMCID')
    
    if pd.isna(pmcid):
        return "Skipping: Missing PMCID"
    
    pmcid = str(pmcid).strip()

    if not pmcid.upper().startswith('PMC'):
        pmcid = f"PMC{pmcid}"
    
    sources = []

    
    sources.append(("NCBI_Direct", f"https://www.ncbi.nlm.nih.gov/pmc/articles/{pmcid}/pdf/"))

    errors = []
    
    for source_name, download_url in sources:
        try:

            response = requests.get(download_url, stream=True, timeout=60, headers=HEADERS, allow_redirects=True)
            
            if response.status_code == 200:
                content_type = response.headers.get('Content-Type', '').lower()

                is_valid = False
                ext = ".pdf"
                
                if "application/pdf" in content_type:
                    is_valid = True
                    ext = ".pdf"
                elif "application/x-gzip" in content_type or "application/gzip" in content_type:
                    is_valid = True
                    ext = ".tar.gz"
                elif "application/octet-stream" in content_type:
                    if download_url.lower().endswith(".tar.gz") or download_url.lower().endswith(".tgz"):
                        is_valid = True
                        ext = ".tar.gz"
                    else:

                        is_valid = True
                        ext = ".pdf"
                
                if not is_valid:
                    errors.append(f"{source_name}: Invalid Content-Type ({content_type})")
                    continue

                safe_pmcid = "".join([c for c in pmcid if c.isalnum() or c in ('-', '_')])
                filename = os.path.join(OUTPUT_DIR, f"{safe_pmcid}{ext}")

                if os.path.exists(filename):
                    return None 

                with open(filename, 'wb') as file:
                    for chunk in response.iter_content(1024):
                        file.write(chunk)
                return None 
            else:
                errors.append(f"{source_name}: HTTP {response.status_code}")
        except Exception as e:
            errors.append(f"{source_name}: {str(e)}")
            
    return f"Failed {pmcid}: {'; '.join(errors)}"

def main():
    print(f" reading file: {INPUT_FILE}")
    try:
        df = pd.read_excel(INPUT_FILE)
    except Exception as e:
        print(f" File reading failed: {e}")
        return

    if 'PMCID' not in df.columns:
        print(" Error: 'PMCID' column Not found in Excel file ")
        return

    tasks = [row for _, row in df.iterrows()]
    total_tasks = len(tasks)

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        future_to_pmcid = {executor.submit(download_single_pmc, row): row['PMCID'] for row in tasks}

        with tqdm(total=total_tasks, desc="Percent") as pbar:
            for future in as_completed(future_to_pmcid):
                pmcid = future_to_pmcid[future]
                try:
                    result = future.result()
                    if result:
                        tqdm.write(result)  
                except Exception as e:
                    tqdm.write(f"Exception for {pmcid}: {e}")
                finally:
                    pbar.update(1)

if __name__ == "__main__":
    main()
