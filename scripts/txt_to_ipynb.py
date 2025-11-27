# convert_txt_to_ipynb.py
import json
import re


def txt_to_cells(txt_path):
    with open(txt_path) as f:
        content = f.read()

    cells = []
    for match in re.finditer(
        r'<VSCode\.Cell id="(.*?)" language="(.*?)">(.*?)</VSCode\.Cell>',
        content,
        re.DOTALL,
    ):
        cells.append(
            {
                "id": match.group(1),
                "language": match.group(2),
                "value": match.group(3).strip(),
            }
        )

    return {"cells": cells}


ipynb_data = txt_to_cells("results_and_stats_v2_chapter4.txt")
with open("results_and_stats_v2_chapter4.ipynb", "w") as f:
    json.dump(ipynb_data, f, indent=2)
