import json
from typing import List, Dict, Union, Callable
import PyPDF2
import openai
import json
import os

if __name__ == "__main__":
    path = 'direct-gpt-extract/gpt3.5_1106_taxonomy_json'

    # load all_nodes
    f = open(f'{path}/all_nodes__.json', 'r')
    all_nodes = json.load(f)
    f.close()

    def capitalize_first_letter(word: str) -> str:
        new_word = ''
        cap = True
        for letter in word:
            letter_to_add = letter
            if cap:
                letter_to_add = letter.upper()
                cap = False
            elif not cap:
                letter_to_add = letter.lower()


            if letter == '_':
                cap = True
            elif letter == ' ':
                cap = True
            
            new_word += letter_to_add

        return new_word

    flowchart_mm = open(f'{path}/flowchart.mm', 'a')
    flowchart_mm.write('graph TB\n')

    for node in all_nodes:
        if all_nodes[node]['children'] == []:
            continue
        else:
            for child in all_nodes[node]['children']:
                flowchart_mm.write(f'    {node} --> {child}\n')

    flowchart_mm.close()
