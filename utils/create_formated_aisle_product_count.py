import csv
import json
import os

def convert_csv_to_json(input_path, output_path):
    """
    Converts a CSV file with 'aisle_id' and 'product_count' columns to a JSON file.
    """
    data = {}
    with open(input_path, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            aisle_id = int(row['aisle_id'])
            product_count = int(row['product_count'])
            data[aisle_id] = product_count

    with open(output_path, 'w') as jsonfile:
        json.dump(data, jsonfile, indent=4)

    print(f"Successfully converted CSV to JSON. Saved to {output_path}")

if __name__ == "__main__":
    # Get the directory of the current script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Define file paths relative to the script's directory
    input_path = os.path.join(script_dir, "../data/aisle_product_count.csv")
    output_path = os.path.join(script_dir, "../data/aisle_product_count.json")

    # Convert CSV to JSON
    convert_csv_to_json(input_path, output_path)