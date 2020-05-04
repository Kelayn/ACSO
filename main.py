from random import random, choice, shuffle
import networkx as nx


def weighted_random(options):
    weights = list(option[0] for option in options)
    if weights.count(weights[0]) == len(weights):
        return choice(options)[1]

    total = sum(weights)
    r = random() * total
    for (weight, value) in options:
        r -= weight
        if r <= 0:
            return value


class Anthill:
    def __init__(self, graph, ants=None):
        self.graph = graph
        self.ants = 50
        self.ko = (1, 1.5, 0.6)
        self.q = 500

    def step(self, best_distances=None):
        ants = []

        for _ in range(self.ants):
            ants.append(self._ant_step())
            if best_distances is not None:
                best_distances.append(ants[-1][1])

        # Evaporate pheromone
        for f, t, key, attrs in self.graph.edges(keys=True, data=True):
            attrs['pheromone'] = attrs['pheromone'] * self.ko[2]

        # Update pheromone
        for _, distance, visited in ants:
            for f, t, key, attrs in self.graph.edges(keys=True, data=True):
                delta = self.q / distance if (f, (t, key)) in visited else 0
                attrs['pheromone'] += delta

        # Return best results
        return (lambda ant: ant[:2])(min(ants, key=lambda ant: ant[1]))

    def _ant_step(self, start_vertex=None):
        # Prepare data
        nodes = list(self.graph.nodes)
        shuffle(nodes)

        if start_vertex is None:
            vertex = nodes.pop()
        else:
            vertex = start_vertex
            nodes.remove(start_vertex)
        path = [(vertex, None)]
        visited = set()

        # Build path
        while nodes:
            options = []
            for target in nodes:
                for key, edge in self.graph.get_edge_data(vertex, target).items():
                    if not edge['distance']:
                        continue
                    a1 = edge['pheromone']**self.ko[0]
                    a2 = (1 / edge['distance'])**self.ko[1]
                    options.append([a1 * a2, (target, key)])
            vertex, key = weighted_random(options)
            path.append((vertex, key))
            visited.add((path[-2][0], path[-1]))
            nodes.remove(vertex)

        # Return home
        options = []
        for key, edge in self.graph.get_edge_data(path[-1][0], path[0][0]).items():
            if not edge['distance']:
                continue
            a1 = edge['pheromone']**self.ko[0]
            a2 = (1 / edge['distance'])**self.ko[1]
            options.append([a1 * a2, (path[0][0], key)])
        vertex, key = weighted_random(options)
        path.append((vertex, key))
        visited.add((path[-2][0], path[-1]))

        # Count distance
        distance = 0
        for i in range(1, len(path)):
            vertex1, _ = path[i - 1]
            vertex2, key = path[i]
            distance += self.graph.get_edge_data(vertex1, vertex2, key)['distance']
        distance += self.graph.get_edge_data(path[-1][0], path[0][0], key)['distance']

        return path, distance, visited


def graph_from_data(data, min_distance=None):
    rows = []
    for row in data.split('\n'):
        rows.append(list(float(val.strip()) for val in row.split()))
    print(rows)
    rows = list(filter(bool, rows))
    print(rows)
    G = nx.MultiDiGraph()
    for i in range(len(rows)):
        for j in range(len(rows[i])):
            G.add_edge(i, j, **{'distance': rows[i][j], 'pheromone': 1/len(rows)})

    return G


if __name__ == "__main__":
    G = graph_from_data("""
        0 633 257  91 412 150  80 134 259 505 353 324  70 211 268 246 121
        633   0 390 661 227 488 572 530 555 289 282 638 567 466 420 745 518
        257 390   0 228 169 112 196 154 372 262 110 437 191  74  53 472 142
        91 661 228   0 383 120  77 105 175 476 324 240  27 182 239 237  84
        412 227 169 383   0 267 351 309 338 196  61 421 346 243 199 528 297
        150 488 112 120 267   0  63  34 264 360 208 329  83 105 123 364  35
        80 572 196  77 351  63   0  29 232 444 292 297  47 150 207 332  29
        134 530 154 105 309  34  29   0 249 402 250 314  68 108 165 349  36
        259 555 372 175 338 264 232 249   0 495 352  95 189 326 383 202 236
        505 289 262 476 196 360 444 402 495   0 154 578 439 336 240 685 390
        353 282 110 324  61 208 292 250 352 154   0 435 287 184 140 542 238
        324 638 437 240 421 329 297 314  95 578 435   0 254 391 448 157 301
        70 567 191  27 346  83  47  68 189 439 287 254   0 145 202 289  55
        211 466  74 182 243 105 150 108 326 336 184 391 145   0  57 426  96
        268 420  53 239 199 123 207 165 383 240 140 448 202  57   0 483 153
        246 745 472 237 528 364 332 349 202 685 542 157 289 426 483   0 336
        121 518 142  84 297  35  29  36 236 390 238 301  55  96 153 336   0
    """)

    a = Anthill(G)

    bpath, bdistance = [], float('inf')

    bds = []

    for i in range(100):
        path, distance = a.step(best_distances=bds)
        if distance < bdistance:
            bpath = path
            bdistance = distance

    import matplotlib.pyplot as plt
    plt.scatter(list(range(len(bds))), bds)
    plt.show()

    print(f'Best distance: {bdistance}\nBest path: {bpath}')