import json
import os

# Define file paths
base_dir = r"c:\Users\jaime\Documents\Github\Respaldo Tec\Materias\Semestre 8\IA\Simulacion\data"
input_file = os.path.join(base_dir, "aisle_info.json")
output_file = os.path.join(base_dir, "aisle_info_scaled.json")

# Read the original data
with open(input_file, 'r') as f:
    aisle_info = json.load(f)

# Scale down impulse_index values
for aisle_id, data in aisle_info.items():
    if 'impulse_index' in data:
        data['impulse_index'] = data['impulse_index'] / 10

# Write the modified data to a new file
with open(output_file, 'w') as f:
    json.dump(aisle_info, f, indent=4)

print(f"Modified data saved to {output_file}")
print(f"Example: Aisle 1 impulse_index: {aisle_info['1']['impulse_index']}")