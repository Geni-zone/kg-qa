"""
Implementation of a vector database, not used in the final version
"""
from utils.similarity import cosine_similarity
import json
import os

class VDB:
    def __init__(self, vdb_file: str, empty_db=True):
        self.vdb_file = vdb_file
        if empty_db:
            self.empty_db()

    # query the vector of the id
    def query_id(self, id: str):
        with open(self.vdb_file, 'r') as infile:
            data = json.load(infile)
        return data[id]
        

    # query the most similar vectors from the vector database
    def query_index(self, input_vector: list[int], count: int=15):
        with open(self.vdb_file, 'r') as infile:
            data = json.load(infile)
        
        scores = list()
        for id, vector in data.items():
            score = cosine_similarity(input_vector, vector)
            #print(score)
            scores.append({'id': id, 'score': score})
        ordered = sorted(scores, key=lambda d: d['score'], reverse=True)
        # ordered_id = [x['id'] for x in ordered]
        return ordered[0:count]

    # insert data into the vector database
    def insert_index(self, in_data: {str: list[int]}):
        data = {}
        # Read existing data from file
        with open(self.vdb_file, 'r') as infile:
            data = json.load(infile)

        # append new data to the old data
        data.update(in_data)

        # Write updated data back to file
        with open(self.vdb_file, 'w') as outfile:
            json.dump(data, outfile, indent=2)

    # empty the current database file
    def empty_db(self):
        with open(self.vdb_file, 'w') as f:
            json.dump({}, f)