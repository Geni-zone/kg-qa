import json
from typing import List, Dict, Union, Callable
import PyPDF2
import openai
import json
import os
from dotenv import load_dotenv
load_dotenv()

openai.api_key = os.getenv("PROF_OPENAI_API_KEY")

# from .utils.exec_retry import exec_retry
# from utils.exec_retry import *
# from utils import exec_retry



import time

def exec_retry(func : Callable, max_retries : int, task_name : str):
    for i in range(max_retries):
        try:
            result = func()
            return result
        except Exception as e:
            print(f"While completing, {task_name}, Error occurred: {e}")
            print(f"Retrying in 1 second... ({i+1}/{max_retries})")
            print(str(e))
            time.sleep(1)
    raise Exception(f"{task_name} failed after {max_retries} retries")


topic = 'Nuclear Engineering'
total_cost = {
    "gpt-3.5-turbo": 0,
    "gpt-3.5-turbo-16k": 0,
    "gpt-4": 0,
}

def calc_cost(model : str, in_tokens : int, out_tokens : int) -> float:
    cost = 0
    if model == "gpt-3.5-turbo":
        cost = in_tokens * 0.0000015 + out_tokens * 0.000002
        total_cost["gpt-3.5-turbo"] += cost
    elif model == "gpt-3.5-turbo-16k":
        cost = in_tokens * 0.000003 + out_tokens * 0.000004
        total_cost["gpt-3.5-turbo-16k"] += cost
    elif model == "gpt-4":
        cost = in_tokens * 0.00003 + out_tokens * 0.00006
        total_cost["gpt-4"] += cost
    
    return cost

all_levels = {
    'L0': 'Nuclear Engineering',
    'L1': [
        'Radiation Protection and Shielding', 'Nuclear Systems Design and Analysis', 'Nuclear Materials'
        'Nuclear Fuels', 'Reactor Physics', 'Nuclear Safety', 'Nuclear Waste Management', 'Nuclear Fusion',
        'Nuclear Fission', 'Nuclear Nonproliferation', 'Health Physics', 'Medical Physics', 'Nuclear Power Engineering',
        'Nuclear Propulsion', 'Nuclear Instrumentation and Measurement', 'Nuclear Structural Analysis',
        'Nuclear Chemistry', 'Nuclear Decommissioning and Remediation','Nuclear Simulation and Modeling'
    ]
}


# parent_node
all_nodes = {
    'Nuclear Engineering_L0': {
        'parent': '',
        'children': [
            'Radiation Protection and Shielding_L1', 'Nuclear Systems Design and Analysis_L1', 'Nuclear Materials'
            'Nuclear Fuels_L1', 'Reactor Physics_L1', 'Nuclear Safety_L1', 'Nuclear Waste Management_L1', 'Nuclear Fusion_L1',
            'Nuclear Fission_L1', 'Nuclear Nonproliferation_L1', 'Health Physics_L1', 'Medical Physics_L1', 'Nuclear Power Engineering_L1',
            'Nuclear Propulsion_L1', 'Nuclear Instrumentation and Measurement_L1', 'Nuclear Structural Analysis_L1',
            'Nuclear Chemistry_L1', 'Nuclear Decommissioning and Remediation_L1','Nuclear Simulation and Modeling_L1'
        ]
    },
    'Radiation Protection and Shielding_L1': {
        'parent': 'Nuclear Engineering_L0',
        'children': []
    },
    'Nuclear Systems Design and Analysis_L1': {
        'parent': 'Nuclear Engineering_L0',
        'children': []
    },
    'Nuclear Materials_L1': {
        'parent': 'Nuclear Engineering_L0',
        'children': []
    },
    'Nuclear Fuels_L1': {
        'parent': 'Nuclear Engineering_L0',
        'children': []
    },
    'Reactor Physics_L1': {
        'parent': 'Nuclear Engineering_L0',
        'children': []
    },
    'Nuclear Safety_L1': {
        'parent': 'Nuclear Engineering_L0',
        'children': []
    },
    'Nuclear Waste Management_L1': {
        'parent': 'Nuclear Engineering_L0',
        'children': []
    },
    'Nuclear Fusion_L1': {
        'parent': 'Nuclear Engineering_L0',
        'children': []
    },
    'Nuclear Fission_L1': {
        'parent': 'Nuclear Engineering_L0',
        'children': []
    },
    'Nuclear Nonproliferation_L1': {
        'parent': 'Nuclear Engineering_L0',
        'children': []
    },
    'Health Physics_L1': {
        'parent': 'Nuclear Engineering_L0',
        'children': []
    },
    'Medical Physics_L1': {
        'parent': 'Nuclear Engineering_L0',
        'children': []
    },
    'Nuclear Power Engineering_L1': {
        'parent': 'Nuclear Engineering_L0',
        'children': []
    },
    'Nuclear Propulsion_L1': {
        'parent': 'Nuclear Engineering_L0',
        'children': []
    },
    'Nuclear Instrumentation and Measurement_L1': {
        'parent': 'Nuclear Engineering_L0',
        'children': []
    },
    'Nuclear Structural Analysis_L1': {
        'parent': 'Nuclear Engineering_L0',
        'children': []
    },
    'Nuclear Chemistry_L1': {
        'parent': 'Nuclear Engineering_L0',
        'children': []
    },
    'Nuclear Decommissioning and Remediation_L1': {
        'parent': 'Nuclear Engineering_L0',
        'children': []
    },
    'Nuclear Simulation and Modeling_L1': {
        'parent': 'Nuclear Engineering_L0',
        'children': []
    }
}


tree = {
    "Nuclear Engineering": [
        'Radiation Protection and Shielding', 'Nuclear Systems Design and Analysis', 'Nuclear Materials'
        'Nuclear Fuels', 'Reactor Physics', 'Nuclear Safety', 'Nuclear Waste Management', 'Nuclear Fusion',
        'Nuclear Fission', 'Nuclear Nonproliferation', 'Health Physics', 'Medical Physics', 'Nuclear Power Engineering',
        'Nuclear Propulsion', 'Nuclear Instrumentation and Measurement', 'Nuclear Structural Analysis',
        'Nuclear Chemistry', 'Nuclear Decommissioning and Remediation','Nuclear Simulation and Modeling'
    ],
}

def log_to_files():
    print(total_cost)
    with open('direct-gpr-extract/total_cost.json', 'w') as f:
        json.dump(total_cost, f, indent=4)
    f.close()

    # write all_nodes to a JSON file
    with open('direct-gpr-extract/all_nodes.json', 'w') as f:
        json.dump(all_nodes, f, indent=4)

    # write all_levels to a JSON file
    with open('direct-gpr-extract/all_levels.json', 'w') as f:
        json.dump(all_levels, f, indent=4)
    
    # write tree to a JSON file
    with open('direct-gpr-extract/tree.json', 'w') as f:
        json.dump(tree, f, indent=4)

if __name__ == '__main__':

    def extract_next_layer(node : str, level : str):
        print(level)
        model = "gpt-4"
        messages = [
            {"role": "user", "content": f"In the broad topic of {topic}, what is the sub categories of {node}? Give me a comma-separated list"},
        ]
        print(messages)
        # def comp():
        completion = openai.ChatCompletion.create(
            model=model,
            messages=messages,
            temperature=0,
            max_tokens=512,
            stop=None,
            n=1
        )
        next_levels : str = completion["choices"][0]["message"]["content"]
        cur_level = int(level[1:])
        split_words = next_levels.split(',')
        print(split_words)
        tree[node] = split_words
        print(207)
        split_labels = [f'{word.strip()}_L{cur_level+1}' for word in split_words]
        if not (f'{node}_{level}' in all_nodes):
            all_nodes[f'{node}_{level}'.strip()] = {}
        all_nodes[f'{node}_{level}']['children'] = split_labels
        print(209)
        # if not (f'L{cur_level+1}' in all_nodes):
        #     all_nodes[f'{node}_{level}'] = {}
        all_levels[f'L{cur_level+1}'] = [f'{word.strip()}' for word in split_words]
        print(211)
        calc_cost(model, completion['usage']['prompt_tokens'], completion['usage']['completion_tokens'])
        
        # exec_retry(comp, 3, f"extract_next_layer({node}, {level})")

    def check_constraints():
        pass

    

    for node in ['Nuclear Fission', 'Nuclear Power Engineering']:
        extract_next_layer(node, 'L1')
        for child in tree[node]:
            print(child)
            extract_next_layer(child, 'L2')
            log_to_files()
            for grandchild in tree[child]:
                print('grandchild: ', grandchild)
                extract_next_layer(grandchild, 'L3')
                log_to_files()
                # for greatgrandchild in tree[grandchild]:
                #     extract_next_layer(greatgrandchild, 'L3')
                #     for greatgreatgrandchild in tree[greatgrandchild]:
                #         extract_next_layer(greatgreatgrandchild, 'L4')
                #         for greatgreatgreatgrandchild in tree[greatgreatgrandchild]:
                #             extract_next_layer(greatgreatgreatgrandchild, 'L5')
                #             for greatgreatgreatgreatgrandchild in tree[greatgreatgreatgrandchild]:
                #                 extract_next_layer(greatgreatgreatgreatgrandchild, 'L6')
                #                 for greatgreatgreatgreatgreatgrandchild in tree[greatgreatgreatgreatgrandchild]:
                #                     extract_next_layer(greatgreatgreatgreatgreatgrandchild, 'L7')
                #                     for greatgreatgreatgreatgreatgreatgrandchild in tree[greatgreatgreatgreatgreatgrandchild]:
                #                         extract_next_layer(greatgreatgreatgreatgreatgreatgrandchild, 'L8')


    log_to_files()


