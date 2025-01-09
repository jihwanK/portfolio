import os
from time import process_time
import pandas as pd
import numpy as np
import fasttext
import fasttext.util


#######################
# FUNCTION DEFINITION #
#######################
def sentence_embedding(model, sentence_list):
    return np.array([ model.get_sentence_vector(' '.join(str(sentence).split())) for sentence in sentence_list ])


########
# MAIN #
########
DATA_HOME_DIR = "/lyceum/jhk1c21/msc_project/data"
FILTERED_DIR = os.path.join(DATA_HOME_DIR, "graph", "v14")

# load node file
print("[TITLE][LOADING] load csv starts")
t_start = process_time()
df = pd.read_csv(os.path.join(FILTERED_DIR, 'nodes_50_v14.csv'), index_col='_id')
t_finish = process_time()
print("[TITLE][LOADING] load csv finishes")
print(f"[TITLE][LOADING] {t_finish - t_start} seconds\n")

title_list = list(df['title'])

# load pretrained fasttext model
print("[TITLE][LOADING] load fasttext data starts")
t_start = process_time()
fast_model = fasttext.load_model(os.path.join(DATA_HOME_DIR, 'cc.en.300.bin'))
t_finish = process_time()
print("[TITLE][LOADING] load fasttext data finishes")
print(f"[TITLE][LOADING] {t_finish - t_start} seconds\n")

# title embeddings
print("[TITLE][EMBEDDING] title embedding start")
t_start = process_time()
title_embedding_list = sentence_embedding(fast_model, title_list)
t_finish = process_time()
print("[TITLE][EMBEDDING] title embedding finish")
print(f"[TITLE][EMBEDDING] {t_finish - t_start} seconds\n")

print("[TITLE][SAVE] save files")
np.save(os.path.join(DATA_HOME_DIR, 'embedding', 'tmp', 'v14', 'tmp_title_embedding.npy'), title_embedding_list)

print("[TITLE] Title embedding is finished")
