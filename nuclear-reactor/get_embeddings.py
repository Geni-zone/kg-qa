from scipy.cluster.vq import kmeans, vq
import numpy as np
import os
from dotenv import load_dotenv
import openai
load_dotenv()
openai.api_key = os.getenv("PROF_OPENAI_API_KEY")

import openai

def get_embeddings(words : list):
    """
    Returns a dictionary of word embeddings from OpenAI for the given list of words.
    
    Args:
    - words (list): A list of words for which embeddings are to be generated.
    
    Returns:
    - wordEmbeddings (dict): A dictionary containing word embeddings for each word in the input list.
    """
    wordEmbeddings : dict = {}
    i = 0
    for word in words:
        print(f'{i} / {len(words) - 1}')
        i += 1
        response = openai.Embedding.create(
            input=word,
            model="text-embedding-ada-002"
        )
        wordEmbeddings[word] = response['data'][0]['embedding']
    
    return wordEmbeddings

if __name__ == "__main__":
    import json

    # Load the index.json file
    with open('nuclear-reactor/index/index.json', 'r') as f:
        index = json.load(f)

    # Get the words from the index
    print(len(index))
    words = list(index.keys())
    print(words)

    # Call the get_embeddings function
    word_embeddings = get_embeddings(words)

    # Write the word embeddings to a json file
    with open('nuclear-reactor/embeddings/word_embeddings.json', 'w') as f:
        json.dump(word_embeddings, f, indent=4)

    # Print the word embeddings
    # print(word_embeddings)

    