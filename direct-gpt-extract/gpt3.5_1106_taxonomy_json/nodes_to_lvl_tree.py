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

    all_levels = {
        "L0": [],
        "L1": [],
        "L2": [],
        "L3": [],
        "L4": [],
        "L5": [],
        "L6": []
    }
    tree = {}

    new_all_nodes = {}

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


    # interate through all nodes, and capitalize the first letter of each word delimited by a space
    for node in all_nodes:
        new_node = {
            'parent': capitalize_first_letter(all_nodes[node]['parent']),
            'children': [capitalize_first_letter(child) for child in all_nodes[node]['children']],
            'taxonomy': capitalize_first_letter(all_nodes[node]['taxonomy'])
        }
        node_name = capitalize_first_letter(node)
        new_all_nodes[node_name] = new_node
    
    all_nodes = new_all_nodes


    labels = list(all_nodes.keys())
    levels = ['L0', 'L1', 'L2', 'L3', 'L4', 'L5', 'L6']
    for label in labels:
        # print(label)
        label_level = label[-2:]
        # print(label_level)
        all_levels[label_level].append(label)
        tree[label] = all_nodes[label]['children']

    

    # write all_levels to a JSON file
    with open(f'{path}/all_levels__.json', 'w') as f:
        json.dump(all_levels, f, indent=3)
        f.close()
    
    # write tree to a JSON file
    with open(f'{path}/tree__.json', 'w') as f:
        json.dump(tree, f, indent=3)
        f.close()

    # write all_nodes to a JSON file
    with open(f'{path}/all_nodes__.json', 'w') as f:
        json.dump(all_nodes, f, indent=3)
        f.close()