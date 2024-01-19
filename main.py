import re
import requests
from bs4 import BeautifulSoup
import json
import logging

logging.basicConfig(level=logging.INFO)

def download_page(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        logging.error(f"Error downloading page: {e}")
        return None

def get_page_title(page_content):
    soup = BeautifulSoup(page_content, 'html.parser')
    title_tag = soup.find('title')
    return title_tag.text.strip() if title_tag else "Untitled"

def read_regex_patterns_from_file(file_path):
    try:
        with open(file_path, 'r') as file:
            return json.load(file)['patterns']
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logging.error(f"Error reading regex patterns from file: {e}")
        return []

def check_regex_matches(page_content, regex_patterns):
    results = []
    sentences = re.split(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s', page_content)
    for sentence in sentences:
        for pattern in regex_patterns:
            compiled_pattern = re.compile(pattern["regex"], re.IGNORECASE)
            matches = compiled_pattern.finditer(sentence)
            for match in matches:
                results.append({
                    "name": pattern["name"],
                    "sentence": sentence,
                })
    return results

def save_to_file(output_filename, regex_results):
    with open(output_filename, 'w') as file:
        file.write("Regex matches found:\n")
        for result in regex_results:
            cleaned_sentence = result['sentence'].replace('<', '').replace('>', '')
            file.write(f"{result['name']} Found in sentence: {cleaned_sentence}\n")
            file.write("==========================\n")

def main():
    try:
        url = input("Enter the URL of the page: ")
        regex_file_path = input("Enter the path to the regex pattern file (e.g., patterns.json): ")

        regex_patterns = read_regex_patterns_from_file(regex_file_path)

        if not regex_patterns:
            logging.warning("No valid regex patterns found. Exiting.")
            return

        page_content = download_page(url)

        if page_content is not None:
            title = get_page_title(page_content)
            output_filename = f"fallacies_{title}.txt".replace(" ", "_")

            regex_results = check_regex_matches(page_content, regex_patterns)

            if regex_results:
                logging.info("Regex matches found:")
                for result in regex_results:
                    logging.info(f"{result['name']} Found in sentence: {result['sentence']}")
                    logging.info("==========================")

                save_to_file(output_filename, regex_results)
                logging.info(f"Results saved to {output_filename}")
            else:
                logging.info("No regex matches found.")
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()
