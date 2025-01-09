import os
from time import time
import pandas as pd
import numpy as np
import fasttext
import fasttext.util
from keybert import KeyBERT


#######################
# FUNCTION DEFINITION #
#######################
def word_list_embedding(model, keyword_list):
    embeddings = [ np.array(list(map(model.get_word_vector, keywords))) for keywords in keyword_list ]
    return [ np.mean(keywords_embedding, axis=0) for keywords_embedding in embeddings ]


########
# MAIN #
########
DATA_HOME_DIR = "/lyceum/jhk1c21/msc_project/data"
FILTERED_DIR = os.path.join(DATA_HOME_DIR, "graph", "v14")

# load node file
print("[ABSTRACT][LOADING] load csv starts")
t_start = time()
df = pd.read_csv(os.path.join(FILTERED_DIR, 'nodes_v14.csv'), index_col='_id')
t_finish = time()
print("[ABSTRACT][LOADING] load csv finishes")
print(f"[ABSTRACT][LOADING] {t_finish - t_start} seconds\n")

# abstract_dict = df['abstract'].to_dict()
abstract_list = list(df['abstract'])

# load pretrained fasttext model
print("[ABSTRACT][LOADING] load fasttext data starts")
t_start = time()
fast_model = fasttext.load_model(os.path.join(DATA_HOME_DIR, 'cc.en.300.bin'))
t_finish = time()
print("[ABSTRACT][LOADING] load fasttext data finishes")
print(f"[ABSTRACT][LOADING] {t_finish - t_start} seconds\n")


# keyword extraction
t_start = time()
print("[ABSTRACT][KEYWORD EXTRACTION] abstract keyword extraction start")
keywords_from_abstract = []
THRESHOLD = 0.3
KEYWORD_LIMIT = 2
bert_model = KeyBERT('distilbert-base-nli-mean-tokens')

to_eleminate_idx_list = []
for idx, abstract in enumerate(abstract_list):
    if str(abstract).split() == 1:
        to_eleminate_idx_list.append(idx)
        continue

    keywords = bert_model.extract_keywords(str(abstract), top_n=10, use_mmr=True)

    filtered_keywords = [ keyword[0] for keyword in keywords if keyword[1] > THRESHOLD ]
    if len(filtered_keywords) == 0:
        filtered_keywords = [ keyword[0] for keyword in keywords[:KEYWORD_LIMIT] ]

    keywords_from_abstract.append(filtered_keywords)
    if idx % 1000 == 0:
        t_mid = time()
        print(f"[ABSTRACT][KEYWORD EXTRACTION] {idx} is done => shape: {len(filtered_keywords)}")
        print(f"[ABSTRACT][KEYWORD EXTRACTION] {t_mid - t_start} seconds")

t_finish = time()
print("[ABSTRACT][KEYWORD EXTRACTION] abstract keyword extraction finish")
print(f"[ABSTRACT][KEYWORD EXTRACTION] {t_finish - t_start} seconds\n")


# its keyword embedding
t_start = time()
print("[ABSTRACT][EMBEDDING] abstract embedding start")
abstract_embedding_list = word_list_embedding(fast_model, keywords_from_abstract)
t_finish = time()
print("[ABSTRACT][EMBEDDING] abstract embedding finish")
print(f"[ABSTRACT][EMBEDDING] {t_finish - t_start} seconds\n")


# search for the uselesses
t_start = time()
print("[ABSTRACT][ELEMINATE] eleminate useless start")
original_shape = abstract_embedding_list[0].shape
for idx, embedding in enumerate(abstract_embedding_list):
    if original_shape != embedding.shape:
        to_eleminate_idx_list.append(idx)
        print(idx, len(abstract_list[idx]), abstract_list[idx])


# filter out some uselesses
abstract_embedding = []
start = 0

for end in to_eleminate_idx_list:
    abstract_embedding.extend(abstract_embedding_list[start:end])
    start = end + 1

abstract_embedding.extend(abstract_embedding_list[start:])

t_finish = time()
print("[ABSTRACT][ELEMINATE] eleminate useless finish")
print(f"[ABSTRACT][ELEMINATE] {t_finish - t_start} seconds\n")


print("[ABSTRACT][SAVE] save files")

eleminated_idx_list = np.array(to_eleminate_idx_list)
np.save(os.path.join(DATA_HOME_DIR, 'embedding', 'tmp', 'v14', 'eleminated_idx.npy'), eleminated_idx_list)

abstract_embedding_list = np.array(abstract_embedding)
print(abstract_embedding_list.shape)
np.save(os.path.join(DATA_HOME_DIR, 'embedding', 'tmp', 'v14', 'tmp_abstract_embedding.npy'), abstract_embedding_list, allow_pickle=True)
