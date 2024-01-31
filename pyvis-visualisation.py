import networkx as nx
from pyvis.network import Network

N = 1000  # number of nodes
K = 4    # each node is connected to K nearest neighbors in ring topology
P = 0.2  # probability of rewiring each edge
G = nx.watts_strogatz_graph(N, K, P)

G2 = nx.erdos_renyi_graph(N, 0.004)
while G2.size() != G.size():
    G2 = nx.erdos_renyi_graph(N, 0.004)


net1 = Network()
net2 = Network()

net1.from_nx(G)
net2.from_nx(G2)

net1.save_graph("graph1.html")
net2.save_graph("graph2.html")

net1.show("graph1.html")
# net2.show("graph2.html")
