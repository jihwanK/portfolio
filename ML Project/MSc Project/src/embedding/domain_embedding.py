import os
from time import process_time
import pandas as pd
import numpy as np
import fasttext
import fasttext.util


#######################
# FUNCTION DEFINITION #
#######################
def word_list_embedding(model, keyword_list, keyword_weight=None):
    embeddings = [ np.array(list(map(model.get_word_vector, keywords))) for keywords in keyword_list ]
    
    if keyword_weight is not None:
        return [ np.average(keywords_embedding, axis=0, weights=keyword_weight[i]) for i, keywords_embedding in enumerate(embeddings) ]

    return [ np.mean(keywords_embedding, axis=0) for keywords_embedding in embeddings ]


########
# MAIN #
########
DATA_HOME_DIR = "/lyceum/jhk1c21/msc_project/data"
FILTERED_DIR = os.path.join(DATA_HOME_DIR, "graph", "v14")


# load node file
print("[DOMAIN][LOADING] load csv starts")
t_start = process_time()
df = pd.read_csv(os.path.join(FILTERED_DIR, 'nodes_v14.csv'), index_col='_id')
t_finish = process_time()
print("[DOMAIN][LOADING] load csv finishes")
print(f"[DOMAIN][LOADING] {t_finish - t_start} seconds\n")


print("[DOMAIN][LOADING] transformation starts")
t_start = process_time()
domains_list = list(df['fos'])
domains_list = list(map(eval, domains_list))
domain_names, domain_weights = [], []
for domains in domains_list:
    tmp_name, tmp_weight = [], []
    for domain in domains:
        tmp_name.append(domain['name'])
        tmp_weight.append(domain['w'])
    domain_names.append(tmp_name)
    domain_weights.append(tmp_weight)
t_finish = process_time()
print("[DOMAIN][LOADING] transformation finishes")
print(f"[DOMAIN][LOADING] {t_finish - t_start} seconds\n")


# load pretrained fasttext model
print("[DOMAIN][LOADING] load fasttext data starts")
t_start = process_time()
fast_model = fasttext.load_model(os.path.join(DATA_HOME_DIR, 'cc.en.300.bin'))
t_finish = process_time()
print("[DOMAIN][LOADING] load fasttext data finishes")
print(f"[DOMAIN][LOADING] {t_finish - t_start} seconds\n")


# keyword embeddings
print("[DOMAIN][EMBEDDING] keyword embedding start")
t_start = process_time()
domains_embedding_list = word_list_embedding(fast_model, domain_names, domain_weights)
t_finish = process_time()
print("[DOMAIN][EMBEDDING] keyword embedding finish")
print(f"[DOMAIN][EMBEDDING] {t_finish - t_start} seconds\n")

print("[DOMAIN][SAVE] save file")
domains_embedding_list = np.array(domains_embedding_list)
np.save(os.path.join(DATA_HOME_DIR, 'embedding', 'tmp', 'v14', 'tmp_domains_embedding.npy'), domains_embedding_list)

print("[DOMAIN] Domain embedding is finished")
