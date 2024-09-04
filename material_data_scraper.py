import os
import pdfkit
import pdfplumber
import pandas as pd
import numpy as np
import requests
from bs4 import BeautifulSoup

# Step 1: Convert the webpage to PDF
def convert_webpage_to_pdf(url, output_pdf, config):
    try:
        pdfkit.from_url(url, output_pdf, configuration=config)
        print(f"Webpage saved as PDF: {output_pdf}")
    except Exception as e:
        print(f"Error converting webpage to PDF: {e}")

# Step 2: Extract tables from the PDF and merge tables 2 onwards
def extract_and_merge_tables_from_pdf(pdf_path):
    merged_table = pd.DataFrame()
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                extracted_tables = page.extract_tables()
                if len(extracted_tables) > 1:
                    for table in extracted_tables[1:]:  # Skip the first table
                        df = pd.DataFrame(table[1:], columns=table[0])  # Convert each table to a DataFrame
                        merged_table = pd.concat([merged_table, df], ignore_index=True)  # Merge all tables except the first
    except Exception as e:
        print(f"Error extracting tables from PDF: {e}")
        
    # Remove rows before the first occurrence of "properties" (case insensitive)
    merged_table.replace('', np.nan, inplace=True)
    merged_table = merged_table.replace(to_replace='None', value=np.nan).dropna(how='all')  # Remove empty rows
    merged_table = merged_table.iloc[:, 0:4]  # Keep only the first 4 columns
    merged_table.columns = ['Properties', 'None', 'Metric', 'English']  # Rename columns
    merged_table = merged_table.drop(['None'], axis=1)  # Drop the 'None' column
    
    # Fill NaN values in 'Properties' column with the previous row value + " (Alternative)"
    merged_table.update(merged_table.ffill().mask(~merged_table.isnull()) + " (Alternative)")
    
    # Remove rows before and containing "properties"
    merged_table = merged_table.map(str)  # Convert all cells to string for easy comparison
    first_prop_index = merged_table[merged_table.apply(lambda row: row.str.contains('properties', case=False).any(), axis=1)].index.min()
    merged_table = merged_table.iloc[first_prop_index:]  # Keep rows from the first "properties" occurrence onwards
    merged_table = merged_table[~merged_table.apply(lambda row: row.str.contains('properties', case=False).any(), axis=1)]

    return merged_table

# Step 3: Find material match using Levenshtein distance
def levenshtein_distance(s1, s2):
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)
    if len(s2) == 0:
        return len(s1)
    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
    return previous_row[-1]

# Step 4: Extract material results from Matweb
def extract_matweb_results(material_name):
    # Build the search URL
    search_url = f"https://www.matweb.com/search/QuickText.aspx?SearchText={material_name.replace(' ', '%20')}"
    
    # Send GET request to fetch the webpage
    response = requests.get(search_url)
    
    if response.status_code != 200:
        print(f"Failed to retrieve the page for {material_name}")
        return
    
    # Parse the HTML content using BeautifulSoup
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Find all links that contain "MatGUID" in the href
    results = []
    for link in soup.find_all('a', href=True):
        if 'MatGUID' in link['href']:
            material_link = f"https://www.matweb.com{link['href']}"
            material_name = link.text.strip()
            results.append((material_name, material_link))
    
    return results

# Step 5: Find best match for material name using Levenshtein
def find_best_match(user_query, material_results):
    material_names = [result[0] for result in material_results]
    best_match = min(material_names, key=lambda name: levenshtein_distance(user_query.lower(), name.lower()))
    
    for name, link in material_results:
        if name == best_match:
            return name, link
    return None, None

# Step 6: Baseline material data retrieval function for external use
def retrieve_material_data(material_query):
    # Configuration for wkhtmltopdf
    config = pdfkit.configuration(wkhtmltopdf='C:/Program Files/wkhtmltopdf/bin/wkhtmltopdf.exe')

    # Find material matches
    material_results = extract_matweb_results(material_query)
    if material_results:
        best_name, best_link = find_best_match(material_query, material_results)
        if best_name and best_link:
            print(f"Best match found: {best_name} - {best_link}")

            # Convert the best matched webpage to PDF
            output_pdf = "material_webpage.pdf"
            convert_webpage_to_pdf(best_link, output_pdf, config)

            # Extract and merge tables from the generated PDF (skipping the first table)
            merged_table = extract_and_merge_tables_from_pdf(output_pdf)

            # Clean up: delete the PDF after extraction
            if os.path.exists(output_pdf):
                os.remove(output_pdf)

            return merged_table
    return None

# Step 7: Verbose material data retrieval function for external use
def retrieve_material_data_verbose(material_query):
    # Configuration for wkhtmltopdf
    config = pdfkit.configuration(wkhtmltopdf='C:/Program Files/wkhtmltopdf/bin/wkhtmltopdf.exe')

    # Find material matches
    material_results = extract_matweb_results(material_query)
    if material_results:
        # Print all found material matches
        print("Found the following material matches:")
        for idx, (name, link) in enumerate(material_results, start=1):
            print(f"{idx}. {name} - {link}")
        
        best_name, best_link = find_best_match(material_query, material_results)
        if best_name and best_link:
            print(f"\nBest match based on Levenshtein distance: {best_name} - {best_link}")

            # Convert the best matched webpage to PDF
            output_pdf = "material_webpage.pdf"
            convert_webpage_to_pdf(best_link, output_pdf, config)

            # Extract and merge tables from the generated PDF (skipping the first table)
            merged_table = extract_and_merge_tables_from_pdf(output_pdf)

            # Clean up: delete the PDF after extraction
            if os.path.exists(output_pdf):
                os.remove(output_pdf)

            return merged_table
    return None

# Step 8: Main function using baseline material data retrieval
if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python material_data_scraper.py [material_name]")
        sys.exit(1)

    material_query = sys.argv[1]
    result_table = retrieve_material_data(material_query)

    if result_table is not None and not result_table.empty:
        result_table.to_csv('material_table.csv', index=False)
        print("Material table saved as CSV.")
    else:
        print(f"No data found for {material_query}.")
