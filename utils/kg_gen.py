from typing import Union
import ast
import re
from utils.gpt import gpt_chat
from KnowledgeGraph import KGRelation, KGEntity

# Every 6k char with 1k overlap
# don't split sentences
# could split by '\n\n' or '\n'
def split_text(input: str, window_size: int=6000, overlap: Union[int, None]=1500, delimiter: str='\n'):
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

def entity_disambiguation(text: str) -> str:
    system_prompt : str = 'Given a chunk of text, replace all the pronouns with the names to which they refer to in the context of the paragraph.'
    prompt : str = f"Given Text:\n{text}"

    messages = [{"role": "system", "content": system_prompt}, {"role": "user", "content": prompt}]
    response = gpt_chat(messages=messages, model="gpt-3.5-turbo-16k", max_tokens=4096)
    return response


def entity_extract(text: str, entity_question: bool=False) -> {str: {'description': str, 'types': [str]}}:
    system_prompt : str = "You are an expert in linguistics and knowledge graph. Your task is to examine the given text and extract all identifiable entities. An 'entity' in this context refers to any distinct and identifiable concept, person, place, or thing in the text with specific attributes and relationships. For instance, 'Elon Musk' is an entity as it defines a distinct person.\n\nIn the case of compound entities, such as 'Chancellor of UIUC', consider 'UIUC' as the entity and do not consider 'Chancellor of' as a separate entity but as a relationship between entities.\n\nFor each identified entity, provide a short description based on its context in the text and classify them into one or more types such as person, place, organization, event, etc. Please note that an entity like 'BMW' can be categorized as a 'Car Manufacturer', 'Organization', and 'Thing'.\n\nThe returned output should be in a well-formatted JSON structure: {'Entity_Name': {'description': 'brief description', 'types': ['type1', 'type2',...]}}, ensure that the entities are clearly identified.\n\nDo not incorporate information about the entities from outside the given text. Aim for a comprehensive extraction of all possible entities in the text, and remember to treat compound entities and date ranges as multiple separate entities."
    prompt : str = f"\n\nGiven Text:\n{text}\n\n" + ("(treat [Entity] as an actual entity, use \"an unknown entity\" as its description)" if entity_question else "")

    messages = [{"role": "system", "content": system_prompt}, {"role": "user", "content": prompt}]
    response = gpt_chat(messages=messages, model="gpt-4", max_tokens=4096)
    print("Entity Extract result: ", response)
    result = ast.literal_eval(response)

    for key, value in result.items():
        if key[0] == '\'' and key[-1] == '\'':
            key = f'"key[1:-1]"'
    for res in result:
        if res[0] == '\'' and res[-1] == '\'':
            res = f'"res[1:-1]"'

    valid_result = {}

    for entity_name in result:
        phrase = phrase_selection(entity_name, text)
    
        messages = [{"role": "system", "content": ""}, {"role": "user", "content": f"In the sentence \"{phrase}\", is \"{entity_name}\" a distinct entity or an attribute of a relation"}]
        response = gpt_chat(messages=messages, model = "gpt-4", max_tokens=1024)
        print(response)
        if not ("relation" in response):
            valid_result[entity_name] = result[entity_name]
    print("Entities: ", valid_result)
    return valid_result


# use entities to select the sentences
def phrase_selection(entity: str, text_chunk: str):
    # system_prompt: str = "You are an expert in linguistics and knowledge graph. You are given an entity and a chunks of text. You help extract the relevant sentences about that entity. Do not modify the sentences when extracting. Your output should be a string of sentences separated by a period."
    # prompt: str = f"Entity: {entity}\nText: {text_chunk}\n\n"

    # messages = [{"role": "system", "content": system_prompt}, {"role": "user", "content": prompt}]
    # response = gpt_chat(messages=messages, model = "gpt-3.5-turbo", max_tokens=2048)
    sentences = re.split('[.?!;]', text_chunk)
    sentences = [sentence.strip() for sentence in sentences]
    result = ""
    for sentence in sentences:
        if entity in sentence:
            result += sentence + '. '
    # print("phrase_selection_result: ", result)
    return result.strip()


def mention_recognition(entity_list: [str], text_chunk: str) -> [str]:
    # system_prompt: str = "You are an expert finding whether a word appeared in a sentence. You are given the names of an entity and text. You output a list of names of the entity that appeared in the text. Your output should be a list of strings."
    # prompt: str = f"Entities: {entity_list}\nText: {text_chunk}\n\n"

    # messages = [{"role": "system", "content": system_prompt}, {"role": "user", "content": prompt}]
    # response = gpt_chat(messages=messages, model = "gpt-3.5-turbo", max_tokens=1024)
    # print("Mention recognition result: ", response)
    # result: [str] = response
    # return ast.literal_eval(str(result))
    other_entities = []
    for entity in entity_list:
        if entity in text_chunk:
            other_entities.append(entity)
    return other_entities


def predicate_extract(text: str, entities: {str: {'description': str, 'types': [str]}}, entity_question: bool=False):
    entity_list = list(entities.keys())
    text_chunks = split_text(text, 600, 150, '.')
    
    def relation_extraction(entity: str, entity_list: [str], text_chunk: str, n_ary = False) -> {"triplets": [], "predicates": {str: {'description': str, 'types': list}}}:

        result_relations: list[KGRelation] = []
        
        # TODO: we could have a more sophisticated text_chunk selection
        system_prompt: str = "You are an expert in linguistics and knowledge graph. You are given a target entity, a list of entities, and a text chunk. You help extract relations between the target entity and each of the entities in the list. Do not add any external information outside of the text to the relations. Your output should be a list of triplets in this 2d-list format: [['Head_entity', 'relation', 'Tail_entity'], ...]"
        prompt: str = f"Target Entity: {entity}\nEntities: {entity_list}\nText: {text_chunk}\n\n" + ("(treat [Entity] as an actual entity)" if entity_question else "")

        messages = [{"role": "system", "content": system_prompt}, {"role": "user", "content": prompt}]
        response = gpt_chat(messages=messages, model = ("gpt-4" if entity_question else "gpt-3.5-turbo-16k"), max_tokens=4096)
        
        triplets: [] = ast.literal_eval(response)
        triplets_tmp = []
        for triplet in triplets:
            if triplet[0] == entity and triplet[2] in entity_list and triplet[2] in text_chunk:
                triplets_tmp.append(triplet)
        triplets = triplets_tmp
        print("relation extraction pt1 result: ", triplets)
        if (not n_ary):
            messages.append({"role": "assistant", "content": triplets})
            messages.append({"role": "user", "content": "Thanks, now you've seen the a knowledge graph triplets. Give me a well-formatted JSON that has all the predicates, their respective description, source text excerpt and types. It should be in this format: {'Predicate_Name': {'description': 'brief description', 'types': ['type1', 'type2',...]}})"})

            response = gpt_chat(messages=messages, model = "gpt-3.5-turbo-16k", max_tokens=8192)

            # print("relation extraction pt2(1): ", response)
            predicates: {str: {'description': str, 'types': [str]}} = response
            
            return {"triplets": triplets, "predicates": predicates}
        elif (n_ary):
            # relations: {str: {'description': str, 'source': str, 'data_properties': {str: [str, str]}}} = {} # TODO: need better naming of the input variables
            for triplet in triplets:
                head = ''
                relation = ''
                tail = ''
                if len(triplet) != 3:
                    head, relation = triplet
                    tail = ''
                elif len(triplet) == 3: head, relation, tail = triplet # TODO: head will always be the given entity

                sentences = re.split('[.?!;]', text_chunk)
                sentences = [sentence.strip() for sentence in sentences]
                possible_sentences = ""
                for sentence in sentences:
                    if head in sentence and tail in sentence:
                        possible_sentences += sentence + '. '
                
                this_system_prompt: str = "You are an expert in linguistics and knowledge graph. You are given a head entity, relation, tail entity, and a text chunk. You help extract the only relevant text that may describe that relation between head entity and tail entity. Do not add any external information outside of the given text chunk. Your output should has a brief description of the relation and the excerpt about the relation in this format: {'description': 'brief description', 'source': 'excerpt abut the relation'}" # TODO: here could be done sentence selection (with overlap)
                this_prompt: str = f"Head Entity: {head}\nRelation: {relation}\nTail Entity: {tail}\nText: {possible_sentences}\n\n" + ("(treat [Entity] as an actual entity)" if entity_question else "")

                messages = [{"role": "system", "content": this_system_prompt}, {"role": "user", "content": this_prompt}]
                response = gpt_chat(messages=messages, model = "gpt-3.5-turbo", max_tokens=1024)
                # print("relation extraction pt2(2.1) result: ", response)
                # this_result = json.loads(response)
                this_result = ast.literal_eval(response)

                relation_text_chunk = this_result["source"]
                
                # TODO: here could be done sentence selection (with overlap)
                # TODO: Need to utilize the returned data properties types
                next_system_prompt: str = "You are an expert in linguistics, knowledge graph, and Ontology Web Language (OWL). You are given a head entity, relation, tail entity, and a text chunk. You will help extract the data properties of the relation between head and tail entity. Data properties for a relation means the attributes for that relation. Do not add any external information outside of the given text chunk. Your output should be a well-formatted JSON that has all property names and their respective values in this format: {'property_name': 'value'}\n\nFor example given:\nHead Entity: Christine\nRelation: Diagnosis\nTail Entity: Breast Tumor\nText: At the age of 89, Christine has breast tumor with high probability.\n\nThis 'Diagnosis' relation should have attributes for example 'age' and 'probability'; so, you should output:\n{'age': '89', 'probability': 'high probability'}"
                
                next_prompt: str = f"Head Entity: {head}\nRelation: {relation}\nTail Entity: {tail}\nText: {relation_text_chunk}\n\n" + ("(treat [Entity] as an actual entity)" if entity_question else "")
                next_messages = [{"role": "system", "content": next_system_prompt}, {"role": "user", "content": next_prompt}]
                # TODO: maybe directly infer dataProperties from the description is easier
                next_response = gpt_chat(messages=next_messages, model = "gpt-4", max_tokens=1024)
                # print("relation extraction pt2(2.2) result: ", next_response)
                attributes = ast.literal_eval(next_response)
               

                triplet[1] = f'{triplet[1].replace(" ", "_")}_Relation'
                
                relation_to_add = KGRelation(name=triplet[1], head_entity=triplet[0], tail_entity=triplet[2], data_properties=attributes, description=this_result["description"], source=this_result["source"])
                print("Relation to add: ", relation_to_add)
                result_relations.append(relation_to_add)

            return result_relations

    result = []
    for entity in entity_list:
        for text_chunk in text_chunks:
            other_entities = entity_list.copy()
            other_entities.remove(entity)
            phrases : str = phrase_selection(entity, text_chunk)
            mentioned_list : [str] = mention_recognition(other_entities, phrases)
            result += relation_extraction(entity, mentioned_list, text_chunk, True)
    return result




# Tiger
def entity_aggregate():
    pass

# Isaac
def predicate_aggregate():
    pass

# All
def merge_kg():
    pass

def infer_schema():
    pass
