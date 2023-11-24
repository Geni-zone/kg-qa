from KnowledgeGraph import KnowledgeGraph
import pickle

with open('./kg_save/knowledge_graph.pkl', 'rb') as file:
       knowledge_graph: KnowledgeGraph = pickle.load(file)

print(knowledge_graph)

knowledge_graph.visualize()

