import json
import numpy as np

def read_json_file(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read().strip()


def parse_rank(json_str: str) -> list[list[int]]:
    data = json.loads(json_str)
    normalized = []

    for cluster in data:
        if isinstance(cluster, list):
            normalized.append(cluster)
        else:
            normalized.append([cluster])
    return normalized


def build_matrix(rank: list[list[int]], n: int) -> list[list[int]]:
    """Строим матрицу nxn"""
    pos = [0] * n
    current_pos = 0
    for cluster in rank:
        for obj in cluster:
            pos[obj - 1] = current_pos
        current_pos += 1
    mat = [[0] * n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            if pos[i] >= pos[j]:
                mat[i][j] = 1

    return mat


def find_kernel(YAB: list[list[int]], YAB_t: list[list[int]]) -> list[list[int]]:
    """Ищем ядро противоречий"""
    n = len(YAB)
    kernel = []
    for i in range(n):
        for j in range(i + 1, n):
            if YAB[i][j] == 0 and YAB_t[i][j] == 0:
                kernel.append([i + 1, j + 1])

    return kernel


def main(json_a: str, json_b: str) -> list[list[int]]:
    rank_a = parse_rank(json_a)
    rank_b = parse_rank(json_b)

    all_objs = set()
    for rank in (rank_a, rank_b):
        for cluster in rank:
            for obj in cluster:
                all_objs.add(obj)

    if not all_objs:
        return []

    n = max(all_objs)

    range_a = np.array(build_matrix(rank_a, n))
    rabge_b = np.array(build_matrix(rank_b, n))

    YAB = range_a * rabge_b

    range_prime = range_a.T * rabge_b.T

    return find_kernel(YAB, range_prime)


if __name__ == "__main__":
    json_a = read_json_file("range_a.json")
    json_b = read_json_file("range_b.json")
    json_c = read_json_file("range_c.json")

    print("Результаты:")
    print(f"Ядро противоречий (range_a range_b):{main(json_a, json_b)}")
    print(f"Ядро противоречий (range_a range_c): {main(json_a, json_c)}")
    print(f"Ядро противоречий (range_b range_c): {main(json_b, json_c)}")
