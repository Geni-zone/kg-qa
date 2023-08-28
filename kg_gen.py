from typing import Union

# Every 4k tokens with 1k overlap
# don't split sentences
# could split by '\n\n' or '\n'
def split_text(input: str, window_size: int=6000, overlap: Union[int, None]=3000):
    stride = window_size - overlap
    start = 0
    end = 0
    result = list()
    while start + window_size <= len(input):
        end = start + window_size
        while input[end - 1] != '\n' and end > start:
            end -= 1
        if end <= start:
            end = start + window_size
        result.append(input[start:end])
        if stride == 0 or stride is None:
            start = end
        else:
            start_tmp = start
            start += stride
            while input[start - 1] != '\n' and start > start_tmp:
                start -= 1
            if start <= start_tmp:
                start = start_tmp + stride
    
    if start + window_size > len(input):
        result.append(input[start:len(input)])
    return result


# Every 4k tokens with 1k overlap
# Tiger
def entity_extract(text: str):
    system_prompt : str = "You are an expert in linguistics and knowledge graph. You help examine text and extract all identifiable entities. You provide a brief, in-context description for each and classify them under appropriate types. Ensure the results are formatted as follows: {'Entity_Name': {'description':'brief description based on the given text', 'types':['type1', 'type2',...]}}, and that no external information is added to these descriptions."
    prompt : str = "An 'entity' in knowledge graph construction refers to any distinct and identifiable concept, person, place, or thing in the text with specific attributes and relationships. For instance, 'Elon Musk' is an entity as it defines a distinct person.\n\nAnalyze the given text and extract all entity mentions. For each identified entity, provide a short description based on its context in the text and classify them into one or more types such as person, place, organization, event, etc. Please note that an entity like 'BMW' can be categorized as a 'Car Manufacturer', 'Organization', and 'Thing'.\n\nThe returned output should be in a well-formatted JSON structure: {'Entity_Name': {'description': 'brief description', 'types': ['type1', 'type2',...]}}, ensure that the entities are clearly identified.\n\nDo not incorporate information about the entities from outside the given text. Aim for a comprehensive extraction of all possible entities in the text.\n\nGiven Text:\n{text}\n\n"


# gather the excepts about the entity
# ask GPT
# Phrase Selection & Mention Recognition & Relation Extraction
# Philip: suppose you have a list of entities.
def predicate_extract():
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