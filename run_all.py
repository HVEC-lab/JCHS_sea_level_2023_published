"""
Script running all notebooks

HVEC-lab, 2023
"""

import os
import papermill as pm


file_list = os.listdir()


for name in file_list:
    if not name.endswith('ipynb'):
        continue

    print(name)
    pm.execute_notebook(name, output_path = 'none')

input("That's all folks!")
