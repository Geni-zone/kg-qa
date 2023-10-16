import json
from typing import List, Dict, Union


# WordType = Dict[str, Union[Dict[str, List[int]], List['WordType']]]
# Words = {
#     'word name': {
#         'page': [1, 2, 3],
#         'related words': [
#            {
#               'word name': {
#                  'page': [1, 2, 3],
#                  'related words': [
#                     {
#                        'word name': {
#                           'page': [1, 2, 3],
#                           'related words': []
#                        }
#                     }
#                  ]
#               }
#            }
#         ]
#     },
#     ...
# }
WordType = Dict[str, Union[List[int], 'Words']]
Words = Dict[str, WordType]

if __name__ == '__main__':
    data = {}

    level = 0
    l0_key = ''
    l1_key = ''
    l2_key = ''

    with open('nuclear-reactor/index/index.txt', 'r') as f:
        for line in f:
            content = line.strip().split(',')

            # count the number of '-' in the beginning of the line to determine the level of the word
            count = content[0].count('- ')
            # print(count)  # Output: 3

            cur_key = content[0].replace("- ", "")
            cur_page_nums = []
            if len(content) > 1:
                if content[1].strip()[0].isalpha():
                    cur_key += ',' + content[1]
                    if len(content) > 2:
                        cur_page_nums = content[2:]
                    else:
                        cur_page_nums = []
                else: # is digits
                    cur_page_nums = content[1:]

            if count == 0:
                data[cur_key] = {
                    "page": cur_page_nums,
                    "related words": {}
                }
            elif count == 1:
                l0_key = cur_key
                data[l0_key] = {
                    "page": cur_page_nums,
                    "related words": {}
                }
            elif count == 2:
                l1_key = cur_key
                data[l0_key]["related words"][l1_key] = {
                    "page": cur_page_nums,
                    "related words": {}
                }
            elif count == 3:
                try: 
                    l2_key = cur_key
                    data[l0_key]["related words"][l1_key]["related words"][l2_key] = {
                        "page": cur_page_nums,
                        "related words": {}
                    }
                except:
                    print(f'{l0_key}, {l1_key}, {l2_key}')
                    raise Exception("Error")


    json_data = json.dumps(data, indent=4)
    with open('nuclear-reactor/index/index.json', 'w') as f:
        f.write(json_data)
