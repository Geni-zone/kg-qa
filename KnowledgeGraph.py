from __future__ import annotations

import uuid
import openai
from utils.vdb import VDB
from utils.similarity import cosine_similarity
from utils.gpt import gpt3_embedding, gpt_chat
from typing import Union, Optional
from collections import deque

import networkx as nx
from pyvis.network import Network
import pyvis.network as nt


class KGRelation:
   def __init__(
      self,
      name: str,
      head_entity: str,
      tail_entity: str,
      data_properties: {str: str},
      description: str,
      source: str
   ):
      self.id = str(uuid.uuid4())
      self.name: str = name
      self.head_entity: str = head_entity
      self.tail_entity: str = tail_entity
      self.data_properties: {str: str} = data_properties
      self.description: str = description
      self.source: str = source
   
   def __str__(self):
      return f"\nRelation: (\n  id: {self.id}\n  name: {self.name}\n  head: {self.head_entity}\n  tail: {str(self.tail_entity)}\n  data_properties: {str(self.data_properties)}\n  description: {self.description}\n  source: {self.source}\n)\n"


class KGEntity:
   def __init__(
      self,
      name: str,
      description: str,
      types: list[str],
      relations: list[KGRelation]
   ):
      self.id: str = str(uuid.uuid4())
      self.name: str = name
      self.description: str = description
      self.types: list[str] = types
      self.relations: list[KGRelation] = relations

   def __str__(self):
      return_str = f"\nEntity: (\n  id: {self.id}\n  name: {self.name}\n  description: {self.description}\n  types: {str(self.types)}\n  relations: ["
      for relation in self.relations:
         return_str += relation.name + ','
      return_str += "]\n)\n"
      return return_str
   

class KnowledgeGraph:
   def __init__(
      self,
      entities: {str: KGEntity},
      relations: set[KGRelation],
      types: set[str],
      vdb_path: str='./vdb'
   ):
      self.entities: {str: KGEntity} = entities
      self.relations: set[KGRelation] = relations
      self.entities_vdb_map: {str: KGEntity} = dict()
      self.relations_vdb_map: {str: KGRelation} = dict()
      self.types: set[str] = types
      self.entity_vdb: VDB = VDB(f'{vdb_path}/entity_vdb.json')
      self.relation_vdb: VDB = VDB(f'{vdb_path}/relation_vdb.json')
      self.types_vdb: VDB = VDB(f'{vdb_path}/types_vdb.json')

   
   def add_entity(self, entity: KGEntity):
      if not entity.name in self.entities:
         self.entities.update({entity.name: entity})
         self.entities_vdb_map.update({entity.id: entity})

         vector = gpt3_embedding(content=entity.name)

         self.entity_vdb.insert_index({entity.id: vector})
      for type in entity.types:
         self.types.add(type)


   def add_relation(self, relation: KGRelation):
      self.relations.add(relation)
      self.relations_vdb_map.update({relation.id: relation})
      self.entities[relation.head_entity].relations.append(relation)

      vector = gpt3_embedding(content=relation.name)

      self.relation_vdb.insert_index({relation.id: vector})


   def __str__(self):
      return_str = "Knowledge Graph:\n\nEntities:\n"
      for entity_name, entity in self.entities.items():
         return_str += str(entity)
      return_str += "\nRelations:\n"
      for relation in self.relations:
         return_str += str(relation)
      return_str += "\nTypes:\n["
      for type in self.types:
         return_str += type + ","
      return_str += ']\n'
      return return_str
   
   def relation_completion(self):
      visited = set()
      def bfs(start: KGEntity, visited: set) -> None:
         q = deque()
         q.append(start)

         visited.add(start)
         while len(q) != 0:
            current = q.popleft()
            for relation in current.relations:
               next_entity = self.entities[relation.tail_entity]
               if not next_entity in visited:
                  has_inverse_relation = False
                  for next_relation in next_entity.relations:
                     if next_relation.tail_entity == relation.head_entity:
                        has_inverse_relation = True
                  if not has_inverse_relation:
                     messages = [{"role": "system", "content": "You are an expert in linguistics and knowledge graph. You will be given a relation between two entities, and you will output a name for the inverse relation between them. Output only the relation name"}, {"role": "user", "content": f"Head Entity:{relation.head_entity}\nTail Entity: {relation.tail_entity}\nRelation: {relation.name}"}]
                     inverse_relation = gpt_chat(messages, model="gpt-4")
                     if inverse_relation.startswith('Inverse Relation: '):
                        inverse_relation = inverse_relation[18:]
                     if not inverse_relation.endswith('Relation'):
                        inverse_relation += "_Relation"
                     self.add_relation(KGRelation(name=inverse_relation, head_entity=relation.tail_entity, tail_entity=relation.head_entity, data_properties=relation.data_properties, description=relation.description, source=relation.source))

                  q.append(next_entity)
                  visited.add(next_entity)
   
      return bfs(list(self.entities.values())[0], visited)
   
   
   def find_path(self, e1: KGEntity, e2: KGEntity) -> list[KGRelation]:
      visited = set()
      def dfs_find_path(current: KGEntity, target: KGEntity, visited: set) -> list[KGRelation]:
         if current.id in visited: 
            return None
         if current.id == target.id: 
            return []

         visited.add(current.id)

         for relation in current.relations:
            next_entity = self.entities[relation.tail_entity]
            path_result = dfs_find_path(next_entity, target, visited)
            if path_result is not None:
               return [relation] + path_result
         
         return None
      return dfs_find_path(e1, e2, visited)
   
   
   def find_matching_entities(self, question: str, start_entity: KGEntity, relations: list[KGRelation], subgraph: KnowledgeGraph) -> set[KGEntity]:
      visited = set()
      matching_entities = set()
      def dfs_find_matching_entities(current: KGEntity, relation_idx: int, visited: set) -> None:
         if current.id in visited: 
            return
         
         if relation_idx == len(relations):
            matching_entities.add(current)
            return

         visited.add(current.id)

         for relation in current.relations:
            input_relation_vector = subgraph.relation_vdb.query_id(relations[relation_idx].id)
            curr_relation_vector = self.relation_vdb.query_id(relation.id)
            similarity = cosine_similarity(input_relation_vector, curr_relation_vector)
            if similarity < 0.90:
               continue

            if relation_idx != len(relations) - 1:
               if relations[relation_idx].tail_entity == relation.tail_entity:
                  next_entity = self.entities[relation.tail_entity]
                  dfs_find_matching_entities(next_entity, relation_idx + 1, visited)
               else:
                  input_tail_entity_vector = subgraph.entity_vdb.query_id(self.entities[relations[relation_idx].tail_entity].id)
                  tail_entity_vector = self.entity_vdb.query_id(self.entities[relation.tail_entity].id)
                  next_entity_similarity = cosine_similarity(input_tail_entity_vector, tail_entity_vector)
                  if next_entity_similarity >= 0.90:
                     next_entity = self.entities[relation.tail_entity]
                     dfs_find_matching_entities(next_entity, relation_idx + 1, visited)
            else:
               system_prompt = "You are an expert in linguistics and knowledge graph. You will help determine that whether a relation is involved in the question. You should only output True or False."
               prompt = f"Question: {question}\n\n{str(relation)}"
               messages = [{"role": "system", "content": system_prompt}, {"role": "user", "content": prompt}]
               response = gpt_chat(messages=messages, model="gpt-4")
               if response == "True":
                  next_entity = self.entities[relation.tail_entity]
                  dfs_find_matching_entities(next_entity, relation_idx + 1, visited)
         
         return None
      
      dfs_find_matching_entities(start_entity, 0, visited)
      return matching_entities
   
   
   def find_data_properties(self, head_name: str, tail_name: str, target_relation_name: str) -> Optional[dict]:
      head = None
      if head_name in self.entities:
         head = self.entities[head_name]
      else:
         target_head_entity_vector = gpt3_embedding(content=tail_name)
         most_similar_pair = self.entity_vdb.query_index(input_vector=target_head_entity_vector, count=1)
         if most_similar_pair["score"] >= 0.90:
            head = self.entities_vdb_map[most_similar_pair["id"]]
   
      if head == None:
         return None    
      
      for relation in head.relations:
         if tail_name == relation.tail_entity:
            if target_relation_name == relation.name:
               return relation.data_properties
            else:
               target_relation_vector = gpt3_embedding(content=target_relation_name)
               curr_relation_vector = self.relation_vdb.query_id(relation.id)
               similarity = cosine_similarity(target_relation_vector, curr_relation_vector)
               if similarity < 0.90:
                  continue
               return relation.data_properties
         else:
            target_tail_entity_vector = gpt3_embedding(content=tail_name)
            curr_tail_entity_vector = self.entity_vdb.query_id(self.entities[relation.tail_entity].id)
            tail_entity_similarity = cosine_similarity(target_tail_entity_vector, curr_tail_entity_vector)
            if tail_entity_similarity >= 0.90:
               if target_relation_name == relation.name:
                  return relation.data_properties
               else:
                  target_relation_vector = gpt3_embedding(content=target_relation_name)
                  curr_relation_vector = self.relation_vdb.query_id(relation.id)
                  similarity = cosine_similarity(target_relation_vector, curr_relation_vector)
                  if similarity < 0.90:
                     continue
                  return relation.data_properties
      
      return None
   
   def visualize(self, path="./kg_visualization/knowledge_graph.html"):
      # Create a directed graph
      G = nx.DiGraph()

      # Add nodes and edges from both lists
      for relation in self.relations:
         G.add_edge(relation.head_entity, relation.tail_entity, label=relation.name)

      # Create a Network instance
      nt_graph = nt.Network(height="1000px", width="100%", bgcolor="#ffffff", font_color="white")

      # Add nodes to the NetworkX graph
      for node in G.nodes():
         label = str(node)
         color = "blue" if label.startswith("l(") else "black"
         shape = "box" if color == "blue" else "ellipse"
         nt_graph.add_node(label, label=label, color=color, shape=shape)

      # Use a different layout algorithm with adjustable parameters
      pos = nx.spring_layout(G, k=0.1)  # Adjust the 'k' parameter to control the force

      # Add edges to the NetworkX graph
      for u, v in G.edges():
         label = G[u][v]['label']
         nt_graph.add_edge(str(u), str(v), title=label)

      # Show the graph in an HTML file
      nt_graph.write_html(path)
         
        
