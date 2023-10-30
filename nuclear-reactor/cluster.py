from scipy.cluster.vq import kmeans, vq, whiten
import numpy as np
import json
    

def k_means(lower: int=2, upper: int=7, iterations: int=10, thresh: float=1e-05):
    '''
    construct the obs M by N matrix, M data points, N features
    whiten the features

    ''' 
    word_embeddings = {}
    with open('nuclear-reactor/embeddings/word_embeddings.json', 'r') as f:
        word_embeddings = json.load(f)

    word_array = np.array(list(word_embeddings.values()))
    whiten(word_array)

    kmeans_output = {}
    for k in range(lower, upper+1):
        kmeans_output[k] = kmeans(word_array, k, iter=iterations, thresh=thresh)
        
    out_dict = {}
    for k in range(lower,upper+1):
        out_dict[k] = {}
        for i in range(k):
            out_dict[k][i] = []
        labels = vq(word_array, kmeans_output[k][0])[0]
        words_list = list(word_embeddings.keys())
        for (idx, label) in enumerate(labels):
            out_dict[k][label].append(words_list[idx])

    # Writing dictionary to a JSON file
    file_name = 'nuclear-reactor/kmeans_test_{}_{}_{}.json'.format(lower, upper, iterations)
    with open(file_name, 'w') as json_file:
        print("Output json file: ", file_name)
        json.dump(out_dict, json_file, indent=4)
        
    

if __name__ == "__main__":
    print("Running cluster.py as main script")
    k_means(2, 10, 20)
