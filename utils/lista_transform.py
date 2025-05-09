import csv
import json
from typing import List, Dict, Any, Tuple
import ast

def transform_csv_to_json():
    # Ruta del archivo CSV de entrada y JSON de salida
    csv_file_path = '../data/shopping_lists.csv'
    json_file_path = '../data/shopping_lists.json'

    # Leer el archivo CSV y convertir a lista de diccionarios
    with open(csv_file_path, mode='r', encoding='utf-8') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        data = list(csv_reader)

    shopping_lists: List[List[int]] = []

    for row in data:
        # Safely evaluate the string to a list
        list_from_string = ast.literal_eval(row['aisle_id'])
        if isinstance(list_from_string, list):
            # Ensure all elements are integers
            shopping_lists.append([int(item) for item in list_from_string])
        
    # for sl in shopping_lists:
    #     print(sl[0])
    
    with open(json_file_path, mode='w', encoding='utf-8') as json_file:
        json.dump(shopping_lists, json_file, indent=4)

    print(f'Transformación completada: {json_file_path}')

if __name__ == "__main__":
    transform_csv_to_json()
