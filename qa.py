import pickle
import openai
import os
import time
from utils.kg_gen import *
from KnowledgeGraph import *
from dotenv import load_dotenv
from utils.gpt import gpt_chat

load_dotenv()
openai.api_key = os.getenv("PROF_OPENAI_API_KEY")


def kg_qa (question: str, knowledge_graph:KnowledgeGraph):
    messages = [{"role": "system", "content": "You are an expert in linguistics and knowledge graph. You will be given a question, output whether the answer to this question would be an distinct entity, relationship between two entities, or properties of a relationship."}, {"role": "user", "content": f"Question: {question}"}]
    question_type_res = gpt_chat(messages, model="gpt-4")

    print(question_type_res)

    if ("propert" in question_type_res) or ("Propert" in question_type_res):
        entities = entity_extract(question, entity_question=True)
        entities_names = list(entities.keys())

        if len(entities_names) != 2:
            raise Exception("there are more than 2 entities in the question")
        
        ## Question about properties/attributes
        messages = [{"role": "system", "content": "You are an expert in linguistics and knowledge graph. You are given two entities, and a text chunk. You help extract relations between the two entities. Do not add any external information outside of the text to the relations. Your output should be a triplet in this list format: ['Head_entity', 'relation', 'Tail_entity']"}, {"role": "user", "content": f"Entity 1: {entities_names[0]}\nEntity 2: {entities_names[1]}\nText: {question}"}]
        triplet_res = gpt_chat(messages, model="gpt-4")
        print(triplet_res)
        triplet: [] = ast.literal_eval(triplet_res)

        triplet[1] = f'{triplet[1].replace(" ", "_")}_Relation'

        data_properties = knowledge_graph.find_data_properties(triplet[0], triplet[2], triplet[1])
        print(data_properties)

        messages = [{"role": "system", "content": "You will get a question about an entity and the answer in knowledge graph, based on that, phrase a final answer to the question"}, {"role": "user", "content": f"Question: {question}\nAnswer in knowledge graph: {str(data_properties)}\n"}]
        
        final_answer = gpt_chat(messages)
        return final_answer

    elif ("relation" in question_type_res) or ("Relation" in question_type_res):
        ## Question about relation
        entities = entity_extract(question, entity_question=True)
        entities_names = list(entities.keys())

        if len(entities_names) != 2:
            raise Exception("there are more than 2 entities in the question")
        
        path = knowledge_graph.find_path(knowledge_graph.entities[entities_names[0]], knowledge_graph.entities[entities_names[1]])

        path_str = "["
        for relation in path:
            path_str += str(relation)
        path_str += "]"

        print(path_str)

        messages = [{"role": "system", "content": "You will get a question about an entity and the answer in knowledge graph, based on that, phrase a final answer to the question"}, {"role": "user", "content": f"Question: {question}\nAnswer in knowledge graph: {path_str}\n"}]
        
        final_answer = gpt_chat(messages)
        return final_answer

    elif ("entit" in question_type_res) or ("Entit" in question_type_res):
        ## Question about entity

        question_modified = None
        is_number_question = False

        messages = [{"role": "system", "content": "You are an expert in linguistics and knowledge graph. You will be given a question, output whether this question is about an entity/entities, or number of entity/entities"}, {"role": "user", "content": question}]
        entity_or_number_res = gpt_chat(messages, model="gpt-4")

        if 'number' in entity_or_number_res:
            is_number_question = True
            messages = [{"role": "system", "content": "You will be given a question of finding the number of something, convert this question to \"Who\" or \"What\" type of question.\n\nExample:\n\"How many presidents were there between 2010-2020?\" Should be converted to \"Who are presidents between 2010-2020?\""}, {"role": "user", "content": question}]
            question_modified = gpt_chat(messages, model="gpt-4")
            
        messages = [{"role": "system", "content": "If the question is about multiple entities, convert it to a question about single entity, else output the same question. don't change content of question.\n\nExample: \n\"Where are all the restaurants in this town?\" should be converted to \"Where is the restaurant in this town?\"\n\n\"Who is the CEO of Meta\" should be the same."}, {"role": "user", "content": question}]
        question_modified = gpt_chat(messages, model="gpt-4")
        print(question_modified)

        messages = [{"role": "system", "content": "You will be given a question related to an entity, convert the question into a statement and replace the entity asked with [ENTITY]\n\nFor example: question \"Who is the Chancellor of UIUC at 2015-2016?\" should be convert to \"[Entity] is the Chancellor of UIUC at 2015-2016.\""}, {"role": "user", "content": question_modified}]
        text = gpt_chat(messages, model="gpt-4")
        print(text)

        # # Read subgraph from the pkl file
        # with open('./kg_save/subgraph.pkl', 'rb') as file:
        #    subgraph: KnowledgeGraph = pickle.load(file)
        subgraph = KnowledgeGraph(entities=dict(), relations=set(), types=set(), vdb_path='./subgraph_vdb')

        entities = entity_extract(text, entity_question=True)
        for entity_name in entities:
            subgraph.add_entity(KGEntity(name=entity_name, description=entities[entity_name]["description"], types=entities[entity_name]["types"], relations=[]))
        
        relations = predicate_extract(text=text, entities=entities, entity_question=True)
        for relation in relations:
            subgraph.add_relation(relation)
        
        print(subgraph)
        with open('./kg_save/subgraph.pkl', 'wb') as file:
            pickle.dump(subgraph, file)
        
        final_entities = None

        for entity_name, entity in subgraph.entities.items():
            if entity_name == "[ENTITY]":
                continue
            path = subgraph.find_path(entity, subgraph.entities["[ENTITY]"])

            result_entities = knowledge_graph.find_matching_entities(relations=path, subgraph=subgraph, question=question_modified)
            print(result_entities)
            if len(result_entities) != 0:
                if final_entities == None:
                     final_entities = result_entities
                else:
                    final_entities = final_entities & result_entities
            else:
                final_entities = set()
        
        entities_str = "["
        for final_entity in final_entities:
            entities_str += str(final_entity)
        entities_str += "]"
        print(entities_str)
        
        messages = [{"role": "system", "content": "You will get a question about an entity and the answer in knowledge graph, based on that, phrase a final answer to the question"}, {"role": "user", "content": f"Question: {question}\nAnswer in knowledge graph: {entities_str if not is_number_question else len(final_entities)}\n"}]
        
        final_answer = gpt_chat(messages)
        return final_answer
    else:
        messages = [{"role": "system", "content": ""}, {"role": "user", "content": question}]
        return gpt_chat(messages, model="gpt-4")


if __name__ == '__main__':
    start_time = time.time()

    question = "Who is the Chancellor of UIUC from 2015-2016?"

    # Read knowledge graph from the pkl file
    with open('./kg_save/knowledge_graph.pkl', 'rb') as file:
       knowledge_graph: KnowledgeGraph = pickle.load(file)
    
    answer = kg_qa(question, knowledge_graph)
    print(answer)

    end_time = time.time()
    print(f"Time elapsed: {end_time - start_time} seconds")