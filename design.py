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
def entity_extract():
    pass


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












def get_embedding():
    pass


def entity_from_q():
    pass


def predicate_from_q():
    pass


# goes thrugh all possible tail entities
def traverse_entity():
    pass


# goes through all possible predicates
def traverse_predicate():
    pass
