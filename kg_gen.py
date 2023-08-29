from typing import Union
import openai
import json
import ast
import os
from dotenv import load_dotenv
load_dotenv()


openai.api_key = os.getenv("OPENAI_API_KEY")

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

# Every 4k tokens with 1k overlap
# Tiger
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
    result = completion["choices"][0]["message"]["content"]
    num_tokens_used = completion['usage']['total_tokens']
    print(f"Entity Extrac; {num_tokens_used} tokens used.")

    return json.loads(result)

# gather the excepts about the entity
# ask GPT
# Phrase Selection & Mention Recognition & Relation Extraction
# Philip: suppose you have a list of entities.
def predicate_extract(text: str, entities: {str: {'description': str, 'types': [str]}}):
    entity_list = list(entities.keys())
    text_chunks = split_text(text, 600, 150, '.')
    
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
        print(f"Mention Recognition; {num_tokens_used} tokens used.")

        return ast.literal_eval(result)
    def relation_extraction(entity: str, entity_list: [str], text_chunk: str) -> {"triplets": [], "predicates": {str: {'description': str, 'types': list}}}:
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

        triplets: [] = completion["choices"][0]["message"]["content"]
        # print(126, ast.literal_eval(triplets))
        print(f"Number of tokens used: {completion['usage']['total_tokens']}")
        messages.append({"role": "system", "content": triplets})
        messages.append({"role": "user", "content": "Now you've seen the a knowledge graph triplet. You are given a list of triplets. Give me a well-formatted JSON that has all the predicates and their description and types. It should be in this format: {'Predicate_Name': {'description': 'brief description', 'types': ['type1', 'type2',...]\}\})"})

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
        return {"triplets": ast.literal_eval(triplets), "predicates": json.loads(predicates)}

    kg = {}
    predicates = {}
    for entity in entity_list:
        kg_triplets = []
        for text_chunk in text_chunks:
            other_entities = entity_list.copy()
            other_entities.remove(entity)
            phrases : str = phrase_selection(entity, text_chunk)
            mentioned_list : [str] = mention_recognition(other_entities, phrases)
            result = relation_extraction(entity, mentioned_list, text_chunk)
            kg_triplets = kg_triplets + result["triplets"]
            for key, value in result["predicates"].items():
                if key not in predicates:
                    predicates[key] = value
                else:
                    print(f"Warning: predicate {key} already exists. Current:\n{predicates[key]}\n\nNew:\n{value}")
                    predicates[key]["description"] += f'{ value["description"]}'
                    predicates[key]["types"] += value["types"]


        kg[entity] = kg_triplets    

    return kg, predicates



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
