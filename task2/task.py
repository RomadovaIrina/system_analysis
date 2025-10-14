import os
import math
from typing import List, Tuple

def calculate_entropy(matrices: List[List[List[int]]]) -> Tuple[float, float]:
    n = len(matrices[0])
    k = len(matrices)
    total_entropy = 0.0

    for matrix in matrices:
        for i in range(n):
            for j in range(n):
                if i != j:
                    p_ij = matrix[i][j] / (n - 1)
                    if p_ij > 0:
                        total_entropy += p_ij * math.log2(p_ij)

    H = -total_entropy
    H_max = (1 / math.e) * n * k
    h = H / H_max if H_max > 0 else 0.0
    return H, h

def generate_permutations(edges: List[Tuple[str, str]], vertices: List[str]) -> List[List[Tuple[str, str]]]:
    all_possible_edges = [(u, v) for u in vertices for v in vertices if u != v]
    existing_edges_set = set(edges)
    possible_new_edges = [e for e in all_possible_edges if e not in existing_edges_set]

    permutations = []
    for i in range(len(edges)):
        for new_edge in possible_new_edges:
            new_edges = edges.copy()
            new_edges[i] = new_edge
            permutations.append(new_edges)
    return permutations

def build_matrices(edges: List[Tuple[str, str]], vertices: List[str]) -> List[List[List[int]]]:
    n = len(vertices)
    idx = {v: i for i, v in enumerate(vertices)}

    r1 = [[0] * n for _ in range(n)]
    for u, v in edges:
        r1[idx[u]][idx[v]] = 1

    r2 = [[r1[j][i] for j in range(n)] for i in range(n)]

    closure = [row[:] for row in r1]
    for _ in range(n - 1):
        new_closure = [[0] * n for _ in range(n)]
        for i in range(n):
            for j in range(n):
                if closure[i][j]:
                    new_closure[i][j] = 1
                else:
                    for k in range(n):
                        if closure[i][k] and r1[k][j]:
                            new_closure[i][j] = 1
                            break
        closure = new_closure


    r3 = [[(closure[i][j] and not r1[i][j]) for j in range(n)] for i in range(n)]
    r3 = [[int(x) for x in row] for row in r3]


    r4 = [[r3[j][i] for j in range(n)] for i in range(n)]


    r2_bool = [[bool(r2[i][j]) for j in range(n)] for i in range(n)]
    r5 = [[0] * n for _ in range(n)]
    for i in range(n):
        for j in range(i + 1, n):
            if any(r2_bool[i][k] and r2_bool[j][k] for k in range(n)):
                r5[i][j] = r5[j][i] = 1

    return [r1, r2, r3, r4, r5]

def main(data: str, root: str) -> Tuple[float, float]:
    rows = data.strip().split("\n")
    edges = []
    vertices = set()

    for row in rows:
        if row.strip():
            u, v = row.split(",")
            u, v = u.strip(), v.strip()
            edges.append((u, v))
            vertices.add(u)
            vertices.add(v)

    vertices = sorted(v for v in vertices if v != root)
    vertices = [root] + vertices

    best_H, best_h = -float('inf'), 0.0

    for perm in generate_permutations(edges, vertices):
        matrices = build_matrices(perm, vertices)
        H, h = calculate_entropy(matrices)
        if H > best_H:
            best_H, best_h = H, h

    return best_H, best_h

if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(current_dir, "task2.csv")

    with open(csv_path, "r") as file:
        input_data = file.read()

    root_vertex = input("Введите значение корневой вершины: ").strip()
    H, h = main(input_data, root_vertex)

    print(f"\nРезультат:")
    print(f"H(M,R) = {H:.4f}")
    print(f"h(M,R) = {h:.4f}")