import torch
import torch.nn as nn
import torch.nn.functional as F
# from sklearn.metrics.pairwise import cosine_similarity
import dgl
from dgl.nn import GATv2Conv
from dgl.nn import Conv

import os
import pandas as pd
import numpy as np

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

DATA_HOME = "/lyceum/jhk1c21/msc_project/data"
V14_PATH = os.path.join(DATA_HOME, "graph", "v14")
FILTERED_PATH = os.path.join(V14_PATH, "filtered")

# Load the data
nodes = pd.read_csv(os.path.join(V14_PATH, "nodes_v14.csv"), index_col='id')
similarity = pd.read_csv(os.path.join(FILTERED_PATH, "similarity_edges.csv"))

titles = np.load(os.path.join(FILTERED_PATH, 'title_embedding.npy'))
abstracts = np.load(os.path.join(FILTERED_PATH, 'abstract_embedding.npy'))
keywords = np.load(os.path.join(FILTERED_PATH, 'keywords_embedding.npy'))
domains = np.load(os.path.join(FILTERED_PATH, 'domains_embedding.npy'))

ids = np.load(os.path.join(FILTERED_PATH, "filtered_id.npy"))
edges = np.load(os.path.join(FILTERED_PATH, 'filtered_edge.npy'))


df = pd.DataFrame()
df['src'] = edges[:, 0]
df['dst'] = edges[:, 1]

# convert id from str to numbers
id_to_int = {original_id: i for i, original_id in enumerate(ids)}
int_to_id = {i: original_id for original_id, i in id_to_int.items()}

df['src'] = df['src'].apply(lambda x: id_to_int[x])
df['dst'] = df['dst'].apply(lambda x: id_to_int[x])

node_features = np.concatenate([titles, abstracts, keywords, domains], axis=1)
tensor_node_features = torch.FloatTensor(node_features)

citation_network = dgl.graph( (df['src'], df['dst']) )
citation_network.ndata['features'] = tensor_node_features


def similarity_score(pair, linked_pair, features):
    w1, w2, w3, w4, w5 = 0.2, 0.2, 0.2, 0.4, 0.05

    titles, abstracts, keywords, domains = features[:, :300], features[:, 300:600], features[:, 600:900], features[:, 900:1200]
    titles_similarity = F.cosine_similarity(titles[pair[:,0]], titles[pair[:,1]])
    abstracts_similarity = F.cosine_similarity(abstracts[pair[:,0]], abstracts[pair[:,1]])
    keywords_similarity = F.cosine_similarity(keywords[pair[:,0]], keywords[pair[:,1]])
    domains_dissimilarity = 1 - F.cosine_similarity(domains[pair[:,0]], domains[pair[:,1]])

    if linked_pair.shape[0] == 0:
        weighted_link_similarity = torch.zeros((pair.shape[0],), dtype=torch.float32)
    else:
        overlap_mask = (linked_pair[:, None, :] == pair[None, :, :]).all(dim=2)
        overlap_mask_1d = overlap_mask.any(dim=0)
        weighted_link_similarity = overlap_mask_1d.float()

    return w1*titles_similarity + w2*abstracts_similarity + w3*keywords_similarity + w4*domains_dissimilarity + w5*weighted_link_similarity


def generate_positive_negative_pairs(graph, node_features, high_threshold = 0.5, low_threshold = 0.35, n_samples=10_000):

    n_nodes = graph.number_of_nodes()
    random_pair = torch.randint(0, n_nodes, (n_samples, 2))

    src = random_pair[:, 0].numpy()
    dst = random_pair[:, 1].numpy()

    dfs = df.set_index(['src', 'dst'])
    linked_random_pair = dfs[dfs.index.isin(list(zip(src, dst)))].reset_index()[['src', 'dst']].to_numpy()
    linked_random_pair = torch.FloatTensor(linked_random_pair)

    scores = similarity_score(random_pair, linked_random_pair, node_features)
    positive_pairs = random_pair[scores > high_threshold]
    negative_pairs = random_pair[scores < low_threshold]

    return positive_pairs, negative_pairs


def compute_loss(output, positive_pairs, negative_pairs, criterion):
    loss = 0
    for pairs, label in [(positive_pairs, torch.Tensor([0])), (negative_pairs, torch.Tensor([1]))]:
        for pair in pairs:
            output1, output2 = output[pair[0]], output[pair[1]]
            loss += criterion(output1.unsqueeze(0), output2.unsqueeze(0), label)

    loss /= (len(positive_pairs) + len(negative_pairs))
    return loss


def train_model(model, graph, node_features, optimizer, criterion, epochs=100):
    loss_values = []

    for epoch in range(epochs):
        model.train()

        optimizer.zero_grad()

        output = model(graph, graph.ndata['features'])

        positive_pairs, negative_pairs = generate_positive_negative_pairs(graph, node_features, n_samples=10_000)

        loss = compute_loss(output, positive_pairs, negative_pairs, criterion)
        loss_values.append(loss.item())

        loss.backward()
        optimizer.step()

        print(f'Epoch [{epoch+1}/{epochs}], Loss: {loss.item()}')

    return loss_values, output


class GAT(nn.Module):
    def __init__(self, in_dim, hidden_dim, out_dim, num_heads):
        super(GAT, self).__init__()
        self.layer1 = GATv2Conv(in_dim, hidden_dim, num_heads=num_heads, allow_zero_in_degree=True)
        self.layer2 = GATv2Conv(hidden_dim * num_heads, out_dim, num_heads=1, allow_zero_in_degree=True)

    def forward(self, graph, features):
        h = self.layer1(graph, features).flatten(1)
        h = F.elu(h)
        h = self.layer2(graph, h).squeeze(1)
        return h


class ContrastiveLoss(nn.Module):
    def __init__(self, margin=1.0):
        super(ContrastiveLoss, self).__init__()
        self.margin = margin

    # as output dimension is different
    def forward(self, output1, output2, label):
        euclidean_distance = F.pairwise_distance(output1, output2, keepdim=True)
        loss_contrastive = torch.mean((1-label) * torch.pow(euclidean_distance, 2) +
                                      (label) * torch.pow(torch.clamp(self.margin - euclidean_distance, min=0.0), 2))
        return loss_contrastive


# main
model = GAT(in_dim=1200, hidden_dim=300, out_dim=50, num_heads=4)
optimizer_fn = torch.optim.Adam(model.parameters(), lr=0.005)
loss_fn = ContrastiveLoss()
loss_values, output = train_model(model, citation_network, tensor_node_features, optimizer_fn, loss_fn, epochs=1000)
torch.save(output, 'result_1000.pt')

