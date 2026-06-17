num_vertices, num_edges = map(int, input().split())
adjacency_list = [[] for _ in range(num_vertices)]
for _ in range(num_edges):
    vertex_a, vertex_b = map(int, input().split())
    vertex_a -= 1
    vertex_b -= 1
    adjacency_list[vertex_a].append(vertex_b)
    adjacency_list[vertex_b].append(vertex_a)

INFINITY = float('inf')
shortest_cycle_length = INFINITY

distance_from_start = [-1] * num_vertices
parent_vertex = [-1] * num_vertices
bfs_queue = [0] * num_vertices

for start_vertex in range(num_vertices):
    if shortest_cycle_length == 3:
        break

    for vertex in range(num_vertices):
        distance_from_start[vertex] = -1
        parent_vertex[vertex] = -1

    queue_head = 0
    queue_tail = 0
    bfs_queue[queue_tail] = start_vertex
    queue_tail += 1
    distance_from_start[start_vertex] = 0

    while queue_head < queue_tail:
        current_vertex = bfs_queue[queue_head]
        queue_head += 1
        current_distance = distance_from_start[current_vertex]
        if current_distance + 1 >= shortest_cycle_length:
            continue
        for neighbor_vertex in adjacency_list[current_vertex]:
            if distance_from_start[neighbor_vertex] == -1:
                distance_from_start[neighbor_vertex] = current_distance + 1
                parent_vertex[neighbor_vertex] = current_vertex
                bfs_queue[queue_tail] = neighbor_vertex
                queue_tail += 1
            elif parent_vertex[current_vertex] != neighbor_vertex:
                cycle_length = current_distance + distance_from_start[neighbor_vertex] + 1
                if cycle_length < shortest_cycle_length:
                    shortest_cycle_length = cycle_length
                    if shortest_cycle_length == 3:
                        break
        if shortest_cycle_length == 3:
            break

print(-1 if shortest_cycle_length == INFINITY else shortest_cycle_length)
