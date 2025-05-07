import csv
import json
import sys
import os
# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config as cfg

# Modified version to create dictionary with aisle_id as keys
def main():
    # Define file paths
    input_path = "../data/" + cfg.AISLE_INFO_FILENAME + ".csv"
    output_path = "../data/" + cfg.AISLE_INFO_FILENAME + ".json"


    
    # Read CSV data
    data = {}
    with open(input_path, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            # Convert numerical values from strings to appropriate types
            aisle_id = int(row['aisle_id'])
            del row['aisle_id']
            del row['impulse_index_normalized']

            row['aisle_name'] = str(row['aisle'])
            del row['aisle']

            row['impulse_index'] = float(row['impulse_index'])
            row['product_count'] = int(row['product_count'])
            data[aisle_id] = row
    
    # Write JSON data
    with open(output_path, 'w') as jsonfile:
        json.dump(data, jsonfile, indent=4)
    
    print(f"Successfully converted CSV to JSON with aisle_id as keys. Saved to {output_path}")

if __name__ == "__main__":
    main()