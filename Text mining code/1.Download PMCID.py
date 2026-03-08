import requests
from bs4 import BeautifulSoup
import pandas as pd
import time


# Read the titles of the literature from the Excel file
def read_titles_from_excel(file_path):
    df = pd.read_excel(file_path)
    return df['Article Title'].tolist()


# Search for literature on PubMed and obtain the PMIDs, PMCID and DOIs.
def search_pubmed(title):
    search_url = f"https://pubmed.ncbi.nlm.nih.gov/?term={title.replace(' ', '+')}"

    try:
        response = requests.get(search_url)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching search results for {title}: {e}")
        return None, None, None

    try:
        soup = BeautifulSoup(response.text, 'html.parser')

        # Obtain PMID
        pmid_tag = soup.find('strong', class_='current-id')
        if pmid_tag:
            pmid = pmid_tag.text.strip()
        else:
            pmid = None

        # Obtain PMCID
        pmcid_tag = soup.find('span', class_='identifier pmc')
        if pmcid_tag:
            pmcid = pmcid_tag.find_next('a').text.strip()
        else:
            pmcid = None

        # Obtain DOI
        DOI_tag = soup.find('span', class_='identifier doi')
        if DOI_tag:
            DOI = DOI_tag.find_next('a').text.strip()
        else:
            DOI = None

        return pmid, pmcid, DOI

    except Exception as e:
        print(f"Error processing the page for {title}: {e}")
        return None, None, None


# Main Function
def main(excel_file, output_file):
    titles = read_titles_from_excel(excel_file)
    results = []

    for title in titles:
        print(f"Processing title: {title}")
        pmid, pmcid, DOI = search_pubmed(title)  # obtain PMID、PMCID和DOI
        results.append({'Title': title, 'PMID': pmid, 'PMCID': pmcid, 'DOI': DOI})


        time.sleep(1)


    results_df = pd.DataFrame(results)
    results_df.to_excel(output_file, index=False)
    print(f"Results saved to {output_file}")



excel_file = r''
output_file = r''

main(excel_file, output_file)
