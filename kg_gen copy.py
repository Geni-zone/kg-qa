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
    result = completion["choices"][0]["message"]["content"]
    num_tokens_used = completion['usage']['total_tokens']
    print(f"Entity Extrac; {num_tokens_used} tokens used.")

    return json.loads(result)

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
    def relation_extraction(entity: str, entity_list: [str], text_chunk: str, n_ary: bool = False) -> {"triplets": [], "predicates": {str: {'description': str, 'source': str}}}:
        # TODO: we could have a more sophisticated text_chunk selection
        n_ary_system_prompt: str = "You are an expert in linguistics, knowledge graph, and Web Ontology Language (OWL). You are making a n-ary relations. Now you are given a target relation, a list of values/literals, and a text excerpt. You help extract data properties of the target relations. All the values and literals are given, but you need to make sense of those values/literals and output a relation that can connect the target relation with each of the values/literals. Do not add any external information outside of the text to the relations. Your output should be a list of triplets in this 2d-list format: [['Target_relaton', 'relation', 'a literal'], ...]"
        n_ary_prompt: str = f"Target Relation: {entity}\nValues/Literals: {entity_list}\Excerpt: {text_chunk}\n\n"
        if n_ary: print(n_ary_prompt)
        # "You are an expert in linguistics, knowledge graph, and Ontology Web Language (OWL). You are given a head entity, relation, tail entity, and a text chunk. You help extract the data properties of the relation for head entity and tail entity. Data properties for a relation means the attributes for that relation. Do not add any external information outside of the given text chunk. Your output should be a well-formatted JSON that has all property names and their respective values and the literal types in this format: {'property_name': ['value', 'type']}\n\nFor example given:\nHead Entity: Christine\nRelation: Diagnosis\nTail Entity: Breast Tumor\nText: At the age of 89, Christine has breast tumor with high probability.\n\nThis 'Diagnosis' relation has attributes like 'age', 'value', 'probability'; so, you should ouput:\n{'age': ['89', 'number'], 'value': ['Breast Tumor', 'string'], 'probability': ['high probability', 'string']."
        system_prompt: str = "You are an expert in linguistics and knowledge graph. You are given a target entity, a list of entities, and a text chunk. You help extract relations between the target entity and each of the entities in the list. Do not add any external information outside of the text to the relations. Your output should be a list of triplets in this 2d-list format: [['Head_entity', 'relation', 'Tail_entity'], ...]"
        prompt: str = f"Target Entity: {entity}\nEntities: {entity_list}\nText: {text_chunk}\n\n"

        model = "gpt-3.5-turbo-16k"
        messages = [{"role": "system", "content": system_prompt}, {"role": "user", "content": prompt}] if n_ary else [{"role": "system", "content": n_ary_system_prompt}, {"role": "user", "content": n_ary_prompt}]
        completion = openai.ChatCompletion.create(
            model=model,
            messages=messages,
            temperature=0.0,
            max_tokens=8192,
            stop=None,
            n=1
        )

        triplets: [] = ast.literal_eval(completion["choices"][0]["message"]["content"])
        # print(126, ast.literal_eval(triplets))
        # {'Relation_Name': {'description': 'brief description', 'source': 'excerpt abut the relation'}}
        # {'Relation_Name': {'description': 'brief description', 'source': 'excerpt abut the relation', 'data_properties': {'property_name': ['value', 'type']}}}
        # relations: {str: {'description': str, 'source': str, 'data_properties': {str: [str, str]}}} = {}
        relations: {str: {'description': str, 'source': str}} = {} # TODO: need better naming of the input variables
        for triplet in triplets:
            print(f'{triplet}\n\n')
            head, relation, tail = triplet # TODO: head will always be the given entity
            # n_ary_this_system_prompt: str = "You are an expert in linguistics and knowledge graph. You are given a head entity, relation, tail entity, and a text chunk. You help extract the only relevant text that may describe that relation for head entity and tail entity. Do not add any external information outside of the given text chunk. Your output should has a brief description of the relation and the excerpt about the relation in this format: {'description': 'brief description', 'source': 'excerpt abut the relation'}" # TODO: here could be done sentence selection (with overlap)
            # n_ary_this_prompt: str = f"Head Entity: {head}\nRelation: {relation}\nTail Entity: {tail}\nText: {text_chunk}\n\n"
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

            relations[relation] = this_result




            # # TODO: here could be done sentence selection (with overlap)
            # # TODO: Need to utilize the returned data properties types
            # next_system_prompt: str = "You are an expert in linguistics, knowledge graph, and Ontology Web Language (OWL). You are given a head entity, relation, tail entity, and a text chunk. You help extract the data properties of the relation for head entity and tail entity. Data properties for a relation means the attributes for that relation. Do not add any external information outside of the given text chunk. Your output should be a well-formatted JSON that has all property names and their respective values and the literal types in this format: {'property_name': ['value', 'type']}\n\nFor example given:\nHead Entity: Christine\nRelation: Diagnosis\nTail Entity: Breast Tumor\nText: At the age of 89, Christine has breast tumor with high probability.\n\nThis 'Diagnosis' relation has attributes like 'age', 'value', 'probability'; so, you should ouput:\n{'age': ['89', 'number'], 'value': ['Breast Tumor', 'string'], 'probability': ['high probability', 'string']."
            # next_prompt: str = f"Head Entity: {head}\nRelation: {relation}\nTail Entity: {tail}\nText: {relation_text_chuck}\n\n"
            # next_messages = [{"role": "system", "content": next_system_prompt}, {"role": "user", "content": next_prompt}]
            # # TODO: maybe directly infer dataProperties from the description is easier
            # next_completion = openai.ChatCompletion.create(
            #     model="gpt-3.5-turbo",
            #     messages=next_messages,
            #     temperature=0.0,
            #     max_tokens=1024,
            #     stop=None,
            #     n=1
            # )
            # this_result["data_properties"] = ast.literal_eval(next_completion["choices"][0]["message"]["content"])
            # print(f"N-ary Relations Extractions; {next_completion['usage']['total_tokens']} tokens used.")

            # relation_ = f'{str(relation).replace(" ", "_")}'
            # relations[f'{relation_}_Relation'] = this_result

            # # TODO: may have a better way
            # triplet[1] = f'has/is {relation_}'

            # # add to triplets
            # for key, value in relations.items():
            #     properties = value["data_properties"]
            #     for property_name, property_value in properties.items():
            #         triplet.append([property_name, property_value])









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



        # print(f"Number of tokens used: {completion['usage']['total_tokens']}")
        # messages.append({"role": "assistant", "content": triplets})
        # messages.append({"role": "user", "content": "Thanks, now you've seen the a knowledge graph triplets. Give me a well-formatted JSON that has all the predicates, their respective description, source text excerpt and types. It should be in this format: {'Predicate_Name': {'description': 'brief description', 'types': ['type1', 'type2',...]}})"})

        # completion = openai.ChatCompletion.create(
        #     model=model,
        #     messages=messages,
        #     temperature=0.0,
        #     max_tokens=8192,
        #     stop=None,
        #     n=1
        # )
        # predicates: {str: {'description': str, 'types': [str]}} = completion["choices"][0]["message"]["content"]
        # print(f"Relation Extraction; {completion['usage']['total_tokens']} tokens used.")
        return {"triplets": triplets, "predicates": relations}
    def n_ary_extract(triplets: [[]], predicates: {str: {'description': str, 'source': str}}):
        for triplet in triplets:
            head, relation, tail = triplet # TODO: we are assuming tail will be present in the new triplets
            predicate: {'description': str, 'source': str} = predicates[relation]
            relation_text_chuck = predicate["source"]
            system_prompt: str = "You are an expert in linguistics. You are given a text excerpt. You extract all nouns in the excerpt. The nouns includes numbers, named entity, excluding pronouns. Do not add any external information outside of the given excerpt. Your output should be a list of strings."
            prompt: str = f"Text Excerpt: {relation_text_chuck}\n\n"
            messages = [{"role": "system", "content": system_prompt}, {"role": "user", "content": prompt}]
            # TODO: maybe directly infer dataProperties from the description is easier
            completion = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=messages,
                temperature=0.0,
                max_tokens=1024,
                stop=None,
                n=1
            )
            nouns: list = ast.literal_eval(completion["choices"][0]["message"]["content"])
            print(f"Noun Extraction; {completion['usage']['total_tokens']} tokens used.")
            print(285, nouns)

            nouns.remove(head)
            new_relation = f'{str(relation).replace(" ", "_")}_Relation'
            result = relation_extraction(new_relation, nouns, relation_text_chuck, True)

            # modify the given triplet and predicates
            triplet[1] = f'has/is {relation}' # TODO: this 'has/is ...' does not have description or any info currently
            triplet[2] = new_relation
            result["triplets"].append(triplet)
            print(289, '\n\n',result,'\n\n')
            return result

    kg = {}
    predicates = {}
    for entity in entity_list:
        kg_triplets = []
        this_predicates = {}
        for text_chunk in text_chunks:
            other_entities = entity_list.copy()
            other_entities.remove(entity)
            phrases : str = phrase_selection(entity, text_chunk)
            mentioned_list : [str] = mention_recognition(other_entities, phrases)
            result = relation_extraction(entity, mentioned_list, text_chunk)
            kg_triplets = kg_triplets + result["triplets"] # TODO: in the future, the names need to be unique labels
            for key, value in result["predicates"].items():
                if key in this_predicates:
                    print(f"Warning: predicate {key} already exists. Current:\n{new_predicates[key]}\n\nNew:\n{value}")
                    this_predicates[key]["description"] += f'{ value["description"]}'
                    # this_predicates[key]["types"] += value["types"]
                elif key in predicates:
                    print(f"Warning: predicate {key} already exists. Current:\n{predicates[key]}\n\nNew:\n{value}")
                    predicates[key]["description"] += f'{ value["description"]}'
                    # predicates[key]["types"] += value["types"]
                else:
                    this_predicates[key] = value

        new_kg_triplets, new_predicates = n_ary_extract(kg_triplets, this_predicates)
        kg[entity] = new_kg_triplets
        predicates.update(new_predicates)

        # kg[entity] = kg_triplets
        # predicates.update(this_predicates)



    return kg, predicates


def n_ary_extract(relation: [str], predicates: {str: {'description': str, 'types': [str]}}, text_chunk: str):
    pass


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
