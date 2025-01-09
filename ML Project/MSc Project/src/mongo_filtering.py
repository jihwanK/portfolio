import time
import networkx as nx
from pymongo import MongoClient
import pandas as pd
import numpy as np


######################
# Connect to MongoDB #
######################
client = MongoClient('localhost', 27017)
db = client['graph']
citation = db['v14']

THRESHOLD = 100

################
# Filter nodes #
################
print("Filter START")

filter_query = {
    "id": {"$exists": True}, \
    "n_citation": {"$gt": THRESHOLD}, \
    "references": {"$exists": True}, \
    "fos": {"$exists": True}, \
    "keywords": {"$exists": True}, \
    "abstract": {"$exists": True}
}
filter_projection = { "_id": False, "id": True, "fos": True, "title": True, "abstract": True, "keywords": True }
filter_result = citation.find(filter_query, filter_projection)

filtered_nodes = [ doc for doc in filter_result if len(doc["id"]) != 0 and len(doc["fos"]) != 0 and len(doc["keywords"]) != 0 and len(doc["abstract"]) != 0]

print("Filter FINISH")

df = pd.DataFrame(filtered_nodes)
df.to_csv("nodes_v14.csv", index=False)

filtered_ids = [ node["id"] for node in filtered_nodes ]


################################
# Generate edge list (BATCHED) #
################################
print("Generating Edge List START")

BATCH_SIZE = 20_000
num_filtered_nodes = len(filtered_ids)
n_iter = num_filtered_nodes//BATCH_SIZE
edges_set = set()
idx = 1
start = time.time()
for it in range(n_iter+1):
    if it < n_iter:
        batched_filtered_nodes = filtered_ids[it*BATCH_SIZE:(it+1)*BATCH_SIZE]
    else:
        batched_filtered_nodes = filtered_ids[it*BATCH_SIZE:]

    edge_result = citation.find({ "id": {"$in": batched_filtered_nodes} }, { "references": True, "id": True, "_id": False})
    for res_doc in edge_result:
        
        satisfied_references = citation.find({ "id": {"$in": res_doc["references"]}, "n_citation": {"$gt": THRESHOLD}, "references": {"$exists": True}, "fos": {"$exists": True} }, { "id": True, "_id": False })

        for reference in satisfied_references:
            edges_set.add((res_doc["id"], reference["id"]))

        if idx % 1000 == 0:
            end = time.time()
            print(f"{idx}/{num_filtered_nodes} [{idx/num_filtered_nodes*100:.2f}%] - time [{end-start:.5f} s/1000p]")
            start = time.time()

        idx += 1

edges_list = list(edges_set)

print("Generating Edge List FINISH")

print("Save files")
np.save(f"/data/jhk1c21/graph_data/v14/id_list_{THRESHOLD}_v14.npy", np.array(filtered_ids))
np.save(f"/data/jhk1c21/graph_data/v14/edge_list_{THRESHOLD}_v14.npy", np.array(edges_list))