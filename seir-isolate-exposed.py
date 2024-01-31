import networkx as nx
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
import matplotlib.patches as mpatches
import matplotlib.animation as animation
from matplotlib.animation import FFMpegWriter

matplotlib.use('Agg')
# duration of phases of the rubella development and recovering
incubation_period = 3 * 7              # max weeks converted to days
infectious_period_before_rash = 7      # infectious days before the rash
rash_duration = 3                      # max 3 days
infectious_post_rash = 4               # average of 3-5 days after rash


transmission_probability = 0.1  # assuming a 10% transmission probability

# openly infectious period - when it is clearly known that someone caught the disease,
# there aren't any symptoms before the rash
openly_infectious_period = rash_duration + infectious_post_rash

# parameters for the watts strogatz graph
N = 100  # number of nodes
K = 4    # each node is connected to K nearest neighbors in ring topology
P = 0.2  # probability of rewiring each edge

# creating the network
fig1, ax1 = plt.subplots(figsize=(10, 8))
G = nx.watts_strogatz_graph(N, K, P)
pos = nx.spring_layout(G, seed=42)


# creating the other network
fig2, ax2 = plt.subplots(figsize=(10, 8))
G2 = nx.erdos_renyi_graph(N, 0.039)
while G2.size() != G.size():
    G2 = nx.erdos_renyi_graph(N, 0.039)

# print(f'Erdos Renyi - number of edges: {G2.size()}')

# all nodes start as susceptible (S)
for node in G.nodes:
    G.nodes[node]['status'] = 'S'
    G.nodes[node]['original_neighbors'] = list(G.neighbors(node))

# all nodes start as susceptible (S)
for node in G2.nodes:
    G2.nodes[node]['status'] = 'S'
    G2.nodes[node]['original_neighbors'] = list(G2.neighbors(node))

# choosing patient 0 randomly
patient_zero = np.random.choice(G.nodes)
G.nodes[patient_zero]['status'] = 'E'
G.nodes[patient_zero]['day_infected'] = 0

# choosing patient 0 randomly
patient_zero = np.random.choice(G2.nodes)
G2.nodes[patient_zero]['status'] = 'E'
G2.nodes[patient_zero]['day_infected'] = 0

s_progress = []
e_progress = []
i_progress = []
r_progress = []

simulation_days = 150


# remove an edge with someone infectious randomly
def remove_edges_for_infectious_node(G, node, edge_removal_prob=1):
    if G.nodes[node]['status'] == 'E':
        neighbors = list(G.neighbors(node))
        for neighbor in neighbors:
            if np.random.rand() < edge_removal_prob:
                G.remove_edge(node, neighbor)


# restoring original edges between recovered nodes
def restore_edges(G):
    for node in G.nodes:
        if G.nodes[node]['status'] == 'R':
            for original_neighbor in G.nodes[node]['original_neighbors']:
                if (G.nodes[original_neighbor]['status'] == 'R' and not G.has_edge(node, original_neighbor))\
                        or (G.nodes[original_neighbor]['status'] == 'S' and not G.has_edge(node, original_neighbor)):
                    G.add_edge(node, original_neighbor)


# simulation function
def simulate_seir(G, total_days):
    for day in range(total_days):
        new_infections = []

        for node in G.nodes:
            status = G.nodes[node]['status']
            if 'day_infected' in G.nodes[node]:
                days_infected = day - G.nodes[node]['day_infected']

                if status == 'E':
                    remove_edges_for_infectious_node(G, node)

                elif status == 'E' and days_infected >= incubation_period:
                    G.nodes[node]['status'] = 'I'
                    # remove_edges_for_infectious_node(G, node)
                elif status == 'I' and days_infected >= incubation_period + openly_infectious_period:
                    G.nodes[node]['status'] = 'R'

        for node in G.nodes:
            status = G.nodes[node]['status']
            if 'day_infected' in G.nodes[node]:
                days_infected = day - G.nodes[node]['day_infected']
                if status == 'I':
                    for neighbor in G.neighbors(node):
                        if G.nodes[neighbor]['status'] == 'S' and np.random.rand() < transmission_probability:
                            new_infections.append(neighbor)
                elif status == 'E' and incubation_period - days_infected <= infectious_period_before_rash:
                    for neighbor in G.neighbors(node):
                        if G.nodes[neighbor]['status'] == 'S' and np.random.rand() < transmission_probability:
                            new_infections.append(neighbor)

        for node in new_infections:
            G.nodes[node]['status'] = 'E'
            G.nodes[node]['day_infected'] = day

        restore_edges(G)


# visualising the network
def plot_network(G, pos, day, ax):
    color_map = {'S': 'blue', 'E': 'yellow', 'I': 'red', 'R': 'green'}
    status_labels = {'S': 'Susceptible', 'E': 'Exposed', 'I': 'Infectious', 'R': 'Recovered'}
    colors = [color_map[G.nodes[node]['status']] for node in G.nodes]

    ax.clear()
    nx.draw(G, pos, ax=ax, node_color=colors, with_labels=True, node_size=50)

    patches = [mpatches.Patch(color=color, label=status_labels[label]) for label, color in color_map.items()]
    ax.legend(handles=patches, title='Status', loc='upper right')
    ax.set_title(f"Day {day}")
    # plt.savefig(f"{directory}/day{day}.jpg")
    # plt.show()


# function for counting nodes for every status
def count_nodes_status(G, status_to_count):
    count = 0
    for node in G.nodes:
        if G.nodes[node]['status'] == status_to_count:
            count += 1
    # print(count)
    return count


# plotting the number of patients in every state over the days of simulation
def plot_progress(s, e, i, r, file_name):
    plt.figure(figsize=(10, 8))
    plt.plot(s, color='#1f77b4')
    plt.plot(e, color='#ff7f0e')
    plt.plot(i, color='#d62728')
    plt.plot(r, color='#2ca02c')
    plt.title("Number of patients in all states over time")
    plt.legend(["Suspectible", "Exposed", "Infectious", "Recovered"])
    plt.savefig(file_name)
    # plt.show()


def update_ws(day, G, pos, ax):
    ax.clear()
    simulate_seir(G, day)
    plot_network(G, pos, day, ax)


def update_er(day, G2, pos, ax):
    ax.clear()
    simulate_seir(G2, day)
    plot_network(G2, pos, day, ax)


# plt.rcParams['animation.ffmpeg_path'] = "C:\ffmpeg\bin\ffmpeg.exe"


# writer = FFMpegWriter(fps=5, metadata=dict(artist='Me'), bitrate=1800)
ani_ws = animation.FuncAnimation(fig1, update_ws, frames=simulation_days, interval=60, fargs=(G, pos, ax1))
ani_ws.save('1_isolated_ws.gif')
plt.close(fig1)


ani_er = animation.FuncAnimation(fig2, update_er, frames=simulation_days, interval=60, fargs=(G2, pos, ax2))
ani_er.save('1_isolated_er.gif')
plt.close(fig2)