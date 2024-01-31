import networkx as nx
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
import matplotlib.patches as mpatches

matplotlib.use('Agg')
# duration of phases of the rubella development and recovering
incubation_period = 3 * 7           # max weeks converted to days
infectious_period_before_rash = 7   # infectious days before the rash
rash_duration = 3                   # max 3 days
infectious_post_rash = 4            # average of 3-5 days after rash

transmission_probability = 0.1  # assuming a 10% transmission probability

# openly infectious period - when it is clearly known that someone caught the disease,
# there aren't any symptoms before the rash
openly_infectious_period = rash_duration + infectious_post_rash

# parameters for the watts strogatz graph
N = 100  # number of nodes
K = 4    # each node is connected to K nearest neighbors in ring topology
P = 0.2  # probability of rewiring each edge

# creating the network
G = nx.watts_strogatz_graph(N, K, P)
pos = nx.spring_layout(G, seed=42)

# all nodes start as susceptible (S)
for node in G.nodes:
    G.nodes[node]['status'] = 'S'

# choosing patient 0 randomly
patient_zero = np.random.choice(G.nodes)
G.nodes[patient_zero]['status'] = 'E'
G.nodes[patient_zero]['day_infected'] = 0

s_progress = []
e_progress = []
i_progress = []
r_progress = []


# simulation function
def simulate_seir(G, days):
    for day in range(days):
        new_infections = []
        for node in G.nodes:
            status = G.nodes[node]['status']
            if 'day_infected' in G.nodes[node]:
                days_infected = day - G.nodes[node]['day_infected']
                if status == 'E' and day - G.nodes[node]['day_infected'] >= incubation_period:
                    G.nodes[node]['status'] = 'I'
                elif status == 'I' and day - G.nodes[node]['day_infected'] >= incubation_period + openly_infectious_period:
                    G.nodes[node]['status'] = 'R'

                # infecting susceptible neighbors if the node is infectious
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


# function for counting nodes for every status
def count_nodes_status(G, status_to_count):
    count = 0
    for node in G.nodes:
        if G.nodes[node]['status'] == status_to_count:
            count += 1
    return count


# visualising the network
def plot_network(G, day):
    color_map = {'S': 'blue', 'E': 'yellow', 'I': 'red', 'R': 'green'}
    status_labels = {'S': 'Susceptible', 'E': 'Exposed', 'I': 'Infectious', 'R': 'Recovered'}
    colors = [color_map[G.nodes[node]['status']] for node in G.nodes]

    plt.figure(figsize=(10, 8))
    nx.draw(G, pos=pos, node_color=colors, with_labels=True, node_size=50)

    patches = [mpatches.Patch(color=color, label=status_labels[label]) for label, color in color_map.items()]
    plt.legend(handles=patches, title='Status', loc='upper right')
    plt.title(f"Day {day}")
    plt.savefig(f"plots/day{day}.jpg")
    # plt.show()


# plotting the number of patients in every state over the days of simulation
def plot_progress(s, e, i, r):
    plt.figure(figsize=(10, 8))
    plt.plot(s, color='#1f77b4')
    plt.plot(e, color='#ff7f0e')
    plt.plot(i, color='#d62728')
    plt.plot(r, color='#2ca02c')
    plt.title("Number of patients in all states over time (no edges lost)")
    plt.legend(["Suspectible", "Exposed", "Infectious", "Recovered"])
    plt.savefig("progress_no_edges_lost.png")
    plt.show()


simulation_days = 150
for day in range(simulation_days + 1):
    simulate_seir(G, day)
    s_progress.append(count_nodes_status(G, 'S'))
    e_progress.append(count_nodes_status(G, 'E'))
    i_progress.append(count_nodes_status(G, 'I'))
    r_progress.append(count_nodes_status(G, 'R'))
    if day in range(simulation_days + 1):  # [0, simulation_days // 2, simulation_days]:
        plot_network(G, day)

plot_progress(s_progress, e_progress, i_progress, r_progress)
