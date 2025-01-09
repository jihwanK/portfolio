import os
from time import process_time
import pandas as pd
import numpy as np
import fasttext
import fasttext.util


#######################
# FUNCTION DEFINITION #
#######################
def word_list_embedding(model, keyword_list):
    embeddings = [ np.array(list(map(model.get_word_vector, eval(keywords)))) for keywords in keyword_list ]
    return [ np.mean(keywords_embedding, axis=0) for keywords_embedding in embeddings ]


########
# MAIN #
########
DATA_HOME_DIR = "/lyceum/jhk1c21/msc_project/data"
FILTERED_DIR = os.path.join(DATA_HOME_DIR, "graph", "v14")

# load node file
print("[KEYWORD][LOADING] load csv starts")
t_start = process_time()
df = pd.read_csv(os.path.join(FILTERED_DIR, 'nodes_v14.csv'), index_col='id')
t_finish = process_time()
print("[KEYWORD][LOADING] load csv finishes")
print(f"[KEYWORD][LOADING] {t_finish - t_start} seconds\n")

keywords_list = list(df['keywords'])

# load pretrained fasttext model
print("[KEYWORD][LOADING] load fasttext data starts")
t_start = process_time()
fast_model = fasttext.load_model(os.path.join(DATA_HOME_DIR, 'cc.en.300.bin'))
t_finish = process_time()
print("[KEYWORD][LOADING] load fasttext data finishes")
print(f"[KEYWORD][LOADING] {t_finish - t_start} seconds\n")


# keyword embeddings
print("[KEYWORD][EMBEDDING] keyword embedding start")
t_start = process_time()
keywords_embedding_list = word_list_embedding(fast_model, keywords_list)
t_finish = process_time()
print("[KEYWORD][EMBEDDING] keyword embedding finish")
print(f"[KEYWORD][EMBEDDING] {t_finish - t_start} seconds\n")

print("[KEYWORD][SAVE] save file")
keywords_embedding_list = np.array(keywords_embedding_list)
np.save(os.path.join(DATA_HOME_DIR, 'embedding', 'tmp', 'v14', 'tmp_keywords_embedding.npy'), keywords_embedding_list)

print("[KEYWORD] Keyword embedding is finished")
