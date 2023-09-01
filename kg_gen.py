from typing import Union
import openai
import json
import ast
import os
from dotenv import load_dotenv
load_dotenv()


# openai.api_key = os.getenv("OPENAI_API_KEY")
openai.api_key = os.getenv("PROF_OPENAI_API_KEY")

# Every 4k tokens with 1k overlap
# don't split sentences
# could split by '\n\n' or '\n'
def split_text(input: str, window_size: int=4000, overlap: Union[int, None]=1000, delimiter: str='\n'):
    stride = window_size - overlap
    start = 0
    end = 0
    result = list()
    while start + window_size <= len(input):
        end = start + window_size
        while input[end - 1] != delimiter and end > start:
            end -= 1
        if end <= start:
            end = start + window_size
        result.append(input[start:end])
        if stride == 0 or stride is None:
            start = end
        else:
            start_tmp = start
            start += stride
            while input[start - 1] != delimiter and start > start_tmp:
                start -= 1
            if start <= start_tmp:
                start = start_tmp + stride
    
    if start + window_size > len(input):
        result.append(input[start:len(input)])
    return result

{
# Every 4k tokens with 1k overlap
# Tiger
# entities = {
#     "Barbara Wilson": {
#         "description": "Barbara Wilson is the Chancellor of UIUC at 2015-2016.",
#         "types": ["person"]
#     },
#     "UIUC": {
#         "description": "UIUC is an abbreviation for the University of Illinois at Urbana-Champaign.",
#         "types": ["organization", "place"]
#     }
# }
}
def entity_extract(text: str) -> {str: {'description': str, 'types': [str]}}:
    system_prompt : str = "You are an expert in linguistics and knowledge graph. You help examine text and extract all identifiable entities. You provide a brief, in-context description for each and classify them under appropriate types.\n\nAn 'entity' in knowledge graph refers to any distinct and identifiable concept, person, place, or thing in the text with specific attributes and relationships. For instance, 'Elon Musk' is an entity as it defines a distinct person.\n\nAnalyze the given text and extract all entity mentions. For each identified entity, provide a short description based on its context in the text and classify them into one or more types such as person, place, organization, event, etc. Please note that an entity like 'BMW' can be categorized as a 'Car Manufacturer', 'Organization', and 'Thing'.\n\nThe returned output should be in a well-formatted JSON structure: {'Entity_Name': {'description': 'brief description', 'types': ['type1', 'type2',...]\}\}, ensure that the entities are clearly identified.\n\nDo not incorporate information about the entities from outside the given text. Aim for a comprehensive extraction of all possible entities in the text."
    prompt : str = f"\n\nGiven Text:\n{text}\n\n"

    model = "gpt-3.5-turbo-16k"
    messages = [{"role": "system", "content": system_prompt}, {"role": "user", "content": prompt}]
    completion = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=0.0,
        max_tokens=8192,
        stop=None,
        n=1
    )
    result = ast.literal_eval(completion["choices"][0]["message"]["content"])
    num_tokens_used = completion['usage']['total_tokens']
    print(f"Entity Extract; {num_tokens_used} tokens used.")

    for key, value in result.items():
        if key[0] == '\'' and key[-1] == '\'':
            key = f'"key[1:-1]"'
    for res in result:
        if res[0] == '\'' and res[-1] == '\'':
            res = f'"res[1:-1]"'

    return result, num_tokens_used

{
# gather the excepts about the entity
# ask GPT
# Phrase Selection & Mention Recognition & Relation Extraction
# Philip: suppose you have a list of entities.
# objectProperty
# kg = {
#     'Barbara Wilson': [
#         ['Barbara Wilson', 'Chancellor of', 'UIUC']
#     ], 
#     'UIUC': [
#         ['UIUC', 'Chancellor', 'Barbara Wilson']
#     ]
# }
# predicates = {
#     'Chancellor of': {
#         'description': 'The role or position of being the chancellor of an institution', 
#         'types': []
#     }, 
#     'Chancellor': {
#         'description': 'The person who holds the position of Chancellor',
#         'types': []
#     }
# }
}
def predicate_extract(text: str, entities: {str: {'description': str, 'types': [str]}}):
    entity_list = list(entities.keys())
    text_chunks = split_text(text, 600, 150, '.')
    total_tokens_used = {"num": 0}
    
    def phrase_selection(entity: str, text_chunk: str):
        system_prompt: str = "You are an expert in linguistics and knowledge graph. You are given an entity and a chunks of text. You help extract the relevant sentences about that entity. Do not modify the sentences when extracting. Your output should be a string of sentences separated by a period."
        prompt: str = f"Entity: {entity}\nText: {text_chunk}\n\n"

        model = "gpt-3.5-turbo"
        messages = [{"role": "system", "content": system_prompt}, {"role": "user", "content": prompt}]
        completion = openai.ChatCompletion.create(
            model=model,
            messages=messages,
            temperature=0.0,
            max_tokens=2048,
            stop=None,
            n=1
        )
        result: str = completion["choices"][0]["message"]["content"]
        num_tokens_used = completion['usage']['total_tokens']
        total_tokens_used["num"] += num_tokens_used
        print(f"Phrase Selection; {num_tokens_used} tokens used.")

        return result
    # returns a list of strings
    def mention_recognition(entity_list: [str], text_chunk: str) -> [str]:
        system_prompt: str = "You are an expert finding whether a word appeared in a sentence. You are given the names of an entity and text. You output a list of names of the entity that appeared in the text. Your output should be a list of strings."
        prompt: str = f"Entities: {entity_list}\nText: {text_chunk}\n\n"

        model = "gpt-3.5-turbo"
        messages = [{"role": "system", "content": system_prompt}, {"role": "user", "content": prompt}]
        completion = openai.ChatCompletion.create(
            model=model,
            messages=messages,
            temperature=0.0,
            max_tokens=1024,
            stop=None,
            n=1
        )
        result: [str] = completion["choices"][0]["message"]["content"]
        num_tokens_used = completion['usage']['total_tokens']
        total_tokens_used["num"] += num_tokens_used
        print(f"Mention Recognition; {num_tokens_used} tokens used.")

        return ast.literal_eval(str(result))
    def relation_extraction(entity: str, entity_list: [str], text_chunk: str, n_ary = False) -> {"triplets": [], "predicates": {str: {'description': str, 'types': list}}}:
        # TODO: we could have a more sophisticated text_chunk selection
        system_prompt: str = "You are an expert in linguistics and knowledge graph. You are given a target entity, a list of entities, and a text chunk. You help extract relations between the target entity and each of the entities in the list. Do not add any external information outside of the text to the relations. Your output should be a list of triplets in this 2d-list format: [['Head_entity', 'relation', 'Tail_entity'], ...]"
        prompt: str = f"Target Entity: {entity}\nEntities: {entity_list}\nText: {text_chunk}\n\n"

        model = "gpt-3.5-turbo-16k"
        messages = [{"role": "system", "content": system_prompt}, {"role": "user", "content": prompt}]
        completion = openai.ChatCompletion.create(
            model=model,
            messages=messages,
            temperature=0.0,
            max_tokens=8192,
            stop=None,
            n=1
        )

        triplets: [] = ast.literal_eval(completion["choices"][0]["message"]["content"])
        print(f"Triplets Extraction; {completion['usage']['total_tokens']} tokens used.")
        total_tokens_used["num"] += completion['usage']['total_tokens']
        if (not n_ary):
            messages.append({"role": "assistant", "content": triplets})
            messages.append({"role": "user", "content": "Thanks, now you've seen the a knowledge graph triplets. Give me a well-formatted JSON that has all the predicates, their respective description, source text excerpt and types. It should be in this format: {'Predicate_Name': {'description': 'brief description', 'types': ['type1', 'type2',...]}})"})

            completion = openai.ChatCompletion.create(
                model=model,
                messages=messages,
                temperature=0.0,
                max_tokens=8192,
                stop=None,
                n=1
            )
            predicates: {str: {'description': str, 'types': [str]}} = completion["choices"][0]["message"]["content"]
            print(f"Relation Extraction; {completion['usage']['total_tokens']} tokens used.")
            total_tokens_used["num"] += completion['usage']['total_tokens']
            return {"ete_triplets": triplets, "etl_triplets": [], "predicates": predicates}
        elif (n_ary):
            # {'Relation_Name': {'description': 'brief description', 'source': 'excerpt abut the relation'}}
            # {'Relation_Name': {'description': 'brief description', 'source': 'excerpt abut the relation', 'data_properties': {'property_name': ['value', 'type']}}}
            relations: {str: {'description': str, 'source': str, 'data_properties': {str: [str, str]}}} = {} # TODO: need better naming of the input variables
            triplets_to_add = []
            for triplet in triplets:
                print(f'{triplet}\n\n')
                head = ''
                relation = ''
                tail = ''
                if len(triplet) != 3:
                    head, relation = triplet
                    tail = ''
                elif len(triplet) == 3: head, relation, tail = triplet # TODO: head will always be the given entity
                this_system_prompt: str = "You are an expert in linguistics and knowledge graph. You are given a head entity, relation, tail entity, and a text chunk. You help extract the only relevant text that may describe that relation for head entity and tail entity. Do not add any external information outside of the given text chunk. Your output should has a brief description of the relation and the excerpt about the relation in this format: {'description': 'brief description', 'source': 'excerpt abut the relation'}" # TODO: here could be done sentence selection (with overlap)
                this_prompt: str = f"Head Entity: {head}\nRelation: {relation}\nTail Entity: {tail}\nText: {text_chunk}\n\n"

                messages = [{"role": "system", "content": this_system_prompt}, {"role": "user", "content": this_prompt}]
                completion = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=messages,
                    temperature=0.0,
                    max_tokens=1024,
                    stop=None,
                    n=1
                )
                # this_result = json.loads(completion["choices"][0]["message"]["content"])
                this_result = ast.literal_eval(completion["choices"][0]["message"]["content"])
                print(f"Relation Phrase Selection; {completion['usage']['total_tokens']} tokens used.")
                total_tokens_used["num"] += completion['usage']['total_tokens']

                relation_text_chuck = this_result["source"]
                
                # TODO: here could be done sentence selection (with overlap)
                # TODO: Need to utilize the returned data properties types
                next_system_prompt: str = "You are an expert in linguistics, knowledge graph, and Ontology Web Language (OWL). You are given a head entity, relation, tail entity, and a text chunk. You help extract the data properties of the relation for head entity and tail entity. Data properties for a relation means the attributes for that relation. Do not add any external information outside of the given text chunk. Your output should be a well-formatted JSON that has all property names and their respective values and the literal types in this format: {'property_name': ['value', 'type']}\n\nFor example given:\nHead Entity: Christine\nRelation: Diagnosis\nTail Entity: Breast Tumor\nText: At the age of 89, Christine has breast tumor with high probability.\n\nThis 'Diagnosis' relation has attributes like 'age', 'value', 'probability'; so, you should ouput:\n{'age': ['89', 'number'], 'value': ['Breast Tumor', 'string'], 'probability': ['high probability', 'string']."
                next_prompt: str = f"Head Entity: {head}\nRelation: {relation}\nTail Entity: {tail}\nText: {relation_text_chuck}\n\n"
                next_messages = [{"role": "system", "content": next_system_prompt}, {"role": "user", "content": next_prompt}]
                # TODO: maybe directly infer dataProperties from the description is easier
                next_completion = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=next_messages,
                    temperature=0.0,
                    max_tokens=1024,
                    stop=None,
                    n=1
                )

                relation_triplets = ast.literal_eval(next_completion["choices"][0]["message"]["content"])
                print(f"N-ary Relations Extractions; {next_completion['usage']['total_tokens']} tokens used.")
                total_tokens_used["num"] += next_completion['usage']['total_tokens']
                relation_ = f'{str(relation).replace(" ", "_")}'
                relation_class = f'{relation_}_Relation'
                for key, value in relation_triplets.items():
                    try:
                        triplets_to_add.append([relation_class, f'has_{key}', value[0]]) # TODO: not using value[1] type yet
                    except Exception as e:
                        # print(f"Warning: {relation_class} has no {key} property.")
                        print(e)
                        break

                this_result["data_properties"] = relation_triplets
                relations[f'{relation_}_Relation'] = this_result

                # TODO: may have a better way
                triplet[1] = f'has/is_{relation_}'
                if len(triplet) < 3: triplet.append(relation_class)
                else: triplet[2] = relation_class

                # TODO: may not need it in the future
                triplets_to_add.append([relation_class, 'has_value', tail])

                # # add to triplets
                # for key, value in relations.items():
                #     properties = value["data_properties"]
                #     for property_name, property_value in properties.items():
                #         triplets.append([property_name, property_value])
            # relations = {
            #     'Chancellor_of_Relation': {
            #         'description': 'Barbara Wilson is the Chancellor of UIUC', 'source': 'Barbara Wilson is the Chancellor of UIUC at 2015-2016.', 
            #         'data_properties': {
            #             'start_date': ['2015', 'date'], 
            #             'end_date': ['2016', 'date']
            #         }
            #     }, 
            #     'Chancellor_Relation': {
            #         'description': 'The relation "Chancellor" describes the position held by Barbara Wilson at UIUC.', 
            #         'source': 'Barbara Wilson is the Chancellor of UIUC at 2015-2016.', 
            #         'data_properties': {
            #             'start_date': ['2015-2016', 'string']
            #         }
            #     }
            # }

            return {"ete_triplets": triplets, "etl_triplets": triplets_to_add, "predicates": relations}

    kg = {}
    all_triplets = {"ete_triplets": [], "etl_triplets": []}
    predicates = {}
    for entity in entity_list:
        kg_triplets = []
        for text_chunk in text_chunks:
            other_entities = entity_list.copy()
            other_entities.remove(entity)
            phrases : str = phrase_selection(entity, text_chunk)
            mentioned_list : [str] = mention_recognition(other_entities, phrases)
            result = relation_extraction(entity, mentioned_list, text_chunk, True)
            kg_triplets += result["ete_triplets"] + result["etl_triplets"] # TODO: in the future, the names need to be unique labels
            all_triplets["ete_triplets"] += (result["ete_triplets"])
            all_triplets["etl_triplets"] += (result["etl_triplets"])
            for key, value in result["predicates"].items():
                if key not in predicates:
                    predicates[key] = value
                else:
                    print(f"Warning: predicate {key} already exists. Current:\n{predicates[key]}\n\nNew:\n{value}")
                    predicates[key]["description"] += f'{ value["description"]}'
                    # predicates[key]["types"] += value["types"]


        kg[entity] = kg_triplets    

    return kg, all_triplets, predicates, total_tokens_used["num"]


# def n_ary_extract(relation: [str], predicates: {str: {'description': str, 'types': [str]}}, text_chunk: str):
#     pass


# Tiger
def entity_aggregate():
    pass

# use hypernym
# Isaac
def predicate_aggregate():
    pass

# All
def merge_kg():
    pass

def infer_schema():
    pass
