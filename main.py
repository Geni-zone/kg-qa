import pickle
import time
from utils.kg_gen import *
from KnowledgeGraph import *
from dotenv import load_dotenv
import os
import openai
load_dotenv()
openai.api_key = os.getenv("PROF_OPENAI_API_KEY")


if __name__ == '__main__':
    start_time = time.time()
    with open ('source' , 'r') as f:
        text = f.read()
    text_chunks = split_text(text)
    # text_chunks = [text]

    knowledge_graph = KnowledgeGraph(entities=dict(), relations=set(), types=set(), vdb_path='./vdb')

    iter = 0
    for text_chunk in text_chunks:
        print('iter: ', iter)
        # try:
        entities = entity_extract(text_chunk)
        for entity_name in entities:
            knowledge_graph.add_entity(KGEntity(name=entity_name, description=entities[entity_name]["description"], types=entities[entity_name]["types"], relations=[]))
        
        text_chunk = entity_disambiguation(text_chunk)
        
        relations = predicate_extract(text=text_chunk, entities=entities)
        for relation in relations:
            knowledge_graph.add_relation(relation)

        iter += 1
    
    knowledge_graph.relation_completion()
    print(knowledge_graph)
    with open('./kg_save/knowledge_graph.pkl', 'wb') as file:
        pickle.dump(knowledge_graph, file)

    end_time = time.time()
    print(f"Time elapsed: {end_time - start_time} seconds")