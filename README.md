# Pasos

## Setup
1. Importa los datos de impulsividad del Notebook en el formato <code>aisle_id,aisle,impulse_index,impulse_index_normalized</code> en la carpeta **/data** en formato **.csv**. El nombre de este archivo se puede modificar desde el archivo de <code>/config.py</code>
2. Correr el archivo <code>utils/create_formated_aisle_impulsivity.py</code> para generar el .json con la información de los pasillos.
3. (Opcional) Correr el archivo <code>utils/create_example_layout.py</code> para crear una visualización de un grid de prueba. Esta visualización se guarda en <code>/data/example.layout</code>