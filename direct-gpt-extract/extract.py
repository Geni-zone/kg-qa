import json
from typing import List, Dict, Union, Callable
import PyPDF2
import openai
import json
import os
import threading
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
# total_cost = {
#     "gpt-3.5-turbo": 0,
#     "gpt-3.5-turbo-16k": 0,
#     "gpt-3.5-turbo-1106": 0,
#     "gpt-4": 0,
#     "gpt-4-1106-preview": 0,
# }


# all_levels = {
#     'L0': 'Nuclear Engineering',
#     'L1': [
#         "Radiation Protection and Shielding", "Nuclear Policy", "Nuclear Decommissioning and Remediation",
#         "Medical and Health Physics", "Nuclear Physics", "Nuclear Safety", "Reactor Physics", "Nuclear Fusion", 
#         "Nuclear Fission", "Nuclear Instrumentation and Measurement", "Thermal Hydraulics", "Nuclear Materials", "Nuclear Fuels",
#         "Computational Nuclear Engineering", "Nuclear Chemistry", "Nuclear Waste Management", "Nuclear Systems Engineering",
#         "Nuclear Weapons", "Nuclear Propulsion", "Radioisotope Production and Application",


#         # "Nuclear Medicine", "Nuclear Reactor Design", "Nuclear Proliferation and Security", "Nuclear Non-Proliferation",
#         # "Nuclear Policy and Regulation", "Nuclear Systems Design and Analysis", "Nuclear Structural Analysis", 
#         # "Nuclear Simulation and Modeling", "Nuclear Systems and Components", "Nuclear Structural Analysis", "Nuclear Nonproliferation"
#     ],
# }

# # parent_node
# all_nodes = {
#     'Nuclear Engineering_L0': {
#         'parent': '',
#         'children': [
#             'Radiation Protection and Shielding_L1', 'Nuclear Policy_L1', 'Nuclear Decommissioning and Remediation_L1',
#             'Medical and Health Physics_L1', 'Nuclear Physics_L1', 'Nuclear Safety_L1', 'Reactor Physics_L1', 'Nuclear Fusion_L1',
#             'Nuclear Fission_L1', 'Nuclear Instrumentation and Measurement_L1', 'Thermal Hydraulics_L1', 'Nuclear Materials_L1', 'Nuclear Fuels_L1',
#             'Computational Nuclear Engineering_L1', 'Nuclear Chemistry_L1', 'Nuclear Waste Management_L1', 'Nuclear Systems Engineering_L1',
#             'Nuclear Weapons_L1', 'Nuclear Propulsion_L1', 'Radioisotope Production and Application_L1'
#         ]
#     },
#     'Radiation Protection and Shielding_L1': {
#         'parent': 'Nuclear Engineering_L0',
#         'children': []
#     },
#     'Nuclear Policy_L1': {
#         'parent': 'Nuclear Engineering_L0',
#         'children': []
#     },
#     'Nuclear Decommissioning and Remediation_L1': {
#         'parent': 'Nuclear Engineering_L0',
#         'children': []
#     },
#     'Medical and Health Physics_L1': {
#         'parent': 'Nuclear Engineering_L0',
#         'children': []
#     },
#     'Nuclear Physics_L1': {
#         'parent': 'Nuclear Engineering_L0',
#         'children': []
#     },
#     'Nuclear Safety_L1': {
#         'parent': 'Nuclear Engineering_L0',
#         'children': []
#     },
#     'Reactor Physics_L1': {
#         'parent': 'Nuclear Engineering_L0',
#         'children': []
#     },
#     'Nuclear Fusion_L1': {
#         'parent': 'Nuclear Engineering_L0',
#         'children': []
#     },
#     'Nuclear Fission_L1': {
#         'parent': 'Nuclear Engineering_L0',
#         'children': []
#     },
#     'Nuclear Instrumentation and Measurement_L1': {
#         'parent': 'Nuclear Engineering_L0',
#         'children': []
#     },
#     'Thermal Hydraulics_L1': {
#         'parent': 'Nuclear Engineering_L0',
#         'children': []
#     },
#     'Nuclear Materials_L1': {
#         'parent': 'Nuclear Engineering_L0',
#         'children': []
#     },
#     'Nuclear Fuels_L1': {
#         'parent': 'Nuclear Engineering_L0',
#         'children': []
#     },
#     'Computational Nuclear Engineering_L1': {
#         'parent': 'Nuclear Engineering_L0',
#         'children': []
#     },
#     'Nuclear Chemistry_L1': {
#         'parent': 'Nuclear Engineering_L0',
#         'children': []
#     },
#     'Nuclear Waste Management_L1': {
#         'parent': 'Nuclear Engineering_L0',
#         'children': []
#     },
#     'Nuclear Systems Engineering_L1': {
#         'parent': 'Nuclear Engineering_L0',
#         'children': []
#     },
#     'Nuclear Weapons_L1': {
#         'parent': 'Nuclear Engineering_L0',
#         'children': []
#     },
#     'Nuclear Propulsion_L1': {
#         'parent': 'Nuclear Engineering_L0',
#         'children': []
#     },
#     'Radioisotope Production and Application_L1': {
#         'parent': 'Nuclear Engineering_L0',
#         'children': []
#     },
# }

# tree = {
#     "Nuclear Engineering": [
#         "Radiation Protection and Shielding", "Nuclear Policy", "Nuclear Decommissioning and Remediation",
#         "Medical and Health Physics", "Nuclear Physics", "Nuclear Safety", "Reactor Physics", "Nuclear Fusion", 
#         "Nuclear Fission", "Nuclear Instrumentation and Measurement", "Thermal Hydraulics", "Nuclear Materials", "Nuclear Fuels",
#         "Computational Nuclear Engineering", "Nuclear Chemistry", "Nuclear Waste Management", "Nuclear Systems Engineering",
#         "Nuclear Weapons", "Nuclear Propulsion", "Radioisotope Production and Application",
#     ],
# }

def log_to_files(path, total_cost, all_nodes, all_levels, tree):
    print(total_cost)
    with open(f'{path}/total_cost.json', 'w') as f:
        json.dump(total_cost, f, indent=3)
        f.close()

    # write all_nodes to a JSON file
    with open(f'{path}/all_nodes__.json', 'w') as f:
        json.dump(all_nodes, f, indent=3)
        f.close()

    # write all_levels to a JSON file
    with open(f'{path}/all_levels__.json', 'w') as f:
        json.dump(all_levels, f, indent=3)
        f.close()
    
    # write tree to a JSON file
    with open(f'{path}/tree__.json', 'w') as f:
        json.dump(tree, f, indent=3)
        f.close()

def load_files(path : str = 'direct-gpt-extract/'):
    with open(f'{path}/total_cost.json', 'r') as f:
        total_cost = json.load(f)

    # write all_nodes to a JSON file
    with open(f'{path}/all_nodes.json', 'r') as f:
        all_nodes = json.load(f)

    # write all_levels to a JSON file
    with open(f'{path}/all_levels.json', 'r') as f:
        all_levels = json.load(f)
    
    # write tree to a JSON file
    with open(f'{path}/tree.json', 'r') as f:
        tree = json.load(f)

    return total_cost, all_nodes, all_levels, tree

if __name__ == '__main__':

    start_time = time.time()

    out_path = 'direct-gpt-extract/gpt3.5_1106_taxonomy_json'
    total_cost, all_nodes, all_levels, tree = load_files()
    # print(207, tree["Nuclear Engineering"])

    def calc_cost(model : str, in_tokens : int, out_tokens : int) -> float:
        cost = 0
        if model == "gpt-3.5-turbo":
            cost = in_tokens * 0.0000015 + out_tokens * 0.000002
            total_cost["gpt-3.5-turbo"] += cost
        elif model == "gpt-3.5-turbo-16k":
            cost = in_tokens * 0.000003 + out_tokens * 0.000004
            total_cost["gpt-3.5-turbo-16k"] += cost
        elif model == "gpt-3.5-turbo-1106":
            cost = in_tokens * 0.000001 + out_tokens * 0.000002
            total_cost["gpt-3.5-turbo-1106"] += cost
        elif model == "gpt-4":
            cost = in_tokens * 0.00003 + out_tokens * 0.00006
            total_cost["gpt-4"] += cost
        elif model == "gpt-4-1106-preview":
            cost = in_tokens * 0.00001 + out_tokens * 0.00003
            total_cost["gpt-4-1106-preview"] += cost
        
        return cost

    def extract_next_layer(label : str, level : str, taxonomy : str = ""):
        # parnent_info = "" if parent == "" else f" {parent}"
        word = label.split('_')[0]
        if (label[0] == ('_')):
            word = label.split('_')[-2]
        print(f'Extracting next layer for {word}, at level: {level}')
        # model = "gpt-4"
        # model = "gpt-4-1106-preview"
        model = "gpt-3.5-turbo-1106"
        messages = [
            # {"role": "user", "content": f"In the broad topic of {topic + parnent_info}, what is the sub categories of {node}? Give me a only a comma-separated list"},
            {"role": "user", "content": f"In the broad topic of {topic}, given a part of the taxonomy: {taxonomy}. What would be the topics or detailed subjects in {word}. Give me only a comma separated list."},
            {"role": "assistant", "content": "The topics or detailed subjects in {word} as comma-separated-list are:"},
            # {"role": "user", "content": f"In the broad topic of {topic}, given a part of the taxonomy: Nuclear Engineering -> Nuclear Fission -> Reactor Physics -> Reactor Kinetics. What would be the subcategories or topics in Reactor Kinetics. Give me only a comma separated list."},
        ]
        
        # print(messages)
        def comp():
            completion = openai.ChatCompletion.create(
                model=model,
                messages=messages,
                temperature=0,
                max_tokens=512,
                stop=None,
                n=1
            )
            next_level_words : str = completion["choices"][0]["message"]["content"]
            split_words = [word.strip() for word in next_level_words.split(',')]
            # print(253, split_words)

            cur_level = int(level[1:])
            next_level = f'L{cur_level+1}'
            split_labels = [f'{s_word}_{next_level}' for s_word in split_words]
            cur_node_label = label
            
            # add word and the new words (split_labels) into tree, all_nodes, and all_levels
            # label naming scheme: _*{word}_{level}, number of _ depends on the number of same words
            # As a key, cur_node_label exists in tree, all_nodes, just need to add the values
            # As a key, split_labels are not in tree, all_nodes
            all_nodes[cur_node_label]['children'] = split_labels # assuming no children

            # add the new words (split_labels) into tree, all_nodes, and all_levels
            for i in range(len(split_labels)):
                word_label = split_labels[i]
                cur_word = split_words[i]
                if word_label in all_nodes:
                    word_label = '_' + word_label
                    cur_word = '_' + cur_word
                # print(272, word_label)
                all_nodes[word_label] = {
                    'parent': cur_node_label,
                    'children': [],
                    'taxonomy': f'{taxonomy} -> {cur_word}'
                }
                # print(278, all_nodes[word_label])
                if next_level in all_levels:
                    all_levels[next_level].append(word_label)
                else:
                    all_levels[next_level] = [word_label]
                # print(283, tree[label])
                tree[word_label] = [] # add the new words to the tree
                tree[label].append(word_label) # add the new words to the parent node


            
            # if not (cur_node_label in all_nodes):
            #     all_nodes[cur_node_label.strip()] = {}
            # else: # node already exists, check if the taxonomy is the same
            #     if all_nodes[cur_node_label]['taxonomy'] != taxonomy:
            #         cur_node_label = '_' + cur_node_label.strip()
            #         all_nodes[cur_node_label] = {}
            # all_nodes[cur_node_label]['parent'] = node
            # all_nodes[cur_node_label]['children'] = split_labels
            # all_nodes[cur_node_label]['taxonomy'] = f'{taxonomy} -> {node}'
            # all_levels[f'L{cur_level+1}'] = [f'{word.strip()}' for word in split_words]
            # tree[cur_node_label] = split_words
            calc_cost(model, completion['usage']['prompt_tokens'], completion['usage']['completion_tokens'])
        
        exec_retry(comp, 3, f"extract_next_layer({word}, {level})")

    def check_constraints():
        pass

    

    # for node in ['Nuclear Fission', 'Reactor Physics', 'Nuclear Power Engineering']:
    #     extract_next_layer(node, 'L1')
    #     for child in tree[node]:
    #         extract_next_layer(child, 'L2', parent=node)
    #         log_to_files()
    #         for grandchild in tree[child]:
    #             print('grandchild: ', grandchild)
    #             extract_next_layer(grandchild, 'L3', parent=node)
    #             log_to_files()
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

    # extract_next_layer('Nuclear Fission', 'L1')
    # extract_next_layer('Reactor Physics', 'L1')
    def extract(labels : [str], cur_level : int, stop_level : int):
        time.sleep(0.5)
        idx = 0
        for label in labels:
            if cur_level == stop_level:
                break
            # print(346, label)
            extract_next_layer(label, f'L{cur_level}', taxonomy=all_nodes[f'{label}']["taxonomy"])

            idx += 1
            print(f'completed {idx}/{len(labels)}\n')
            log_to_files(out_path, total_cost, all_nodes, all_levels, tree)
            extract(tree[label], cur_level+1, stop_level)

    thread1 = threading.Thread(target=extract(['Nuclear Reactor Design_L2'], 2, 6))
    thread2 = threading.Thread(target=extract(['Reactor Kinetics_L2'], 2, 6))
    # thread1 = threading.Thread(target=extract(['Nuclear Fission_L1'], 1, 6))
    # thread2 = threading.Thread(target=extract(['Nuclear Physics_L1'], 1, 6))
        # [
        #     "Neutron Transport Theory", "Neutron Diffusion Theory", "Reactor Kinetics", "Reactor Dynamics",
        #     "Fuel Burnup and Depletion", "Reactor Core Design", "Neutronics", "Thermal-Hydraulics",
        #     "Reactor Safety Analysis", "Reactor Control Systems", "Monte Carlo Methods", "Deterministic Methods",
        #     "Cross Section Data Analysis", "Reactor Operation and Regulation", "Radiation Shielding and Protection"
        # ]

    thread1.start()
    thread2.start()

    thread1.join()
    thread2.join()
    log_to_files(out_path, total_cost, all_nodes, all_levels, tree)

    end_time = time.time()
    print(f'Total time: {end_time - start_time}')





# def print_numbers():
#     for i in range(1, 6):
#         print(f"Number {i}")
#         time.sleep(0.1)

# def print_letters():
#     for letter in "ABCDE":
#         print(f"Letter {letter}")
#         time.sleep(0.1)

# # Create two threads
# thread1 = threading.Thread(target=print_numbers)
# thread2 = threading.Thread(target=print_letters)

# # Start the threads
# thread1.start()
# thread2.start()

# # Wait for both threads to finish
# thread1.join()
# thread2.join()

# print("Both threads have finished")


