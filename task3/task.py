import json
import numpy as np
from collections import deque
from itertools import combinations


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


def rank_to_dict(rank):
    result = {}
    cnt = 1
    for item in rank:
        if isinstance(item, list):
            for elem in item:
                result[elem] = set([cnt + i for i in range(len(item))])
            cnt += len(item)
        else:
            result[item] = set([cnt])
            cnt += 1
    return result


def get_contradiction_core(json_str1, json_str2):

    rank1 = json.loads(json_str1)
    rank2 = json.loads(json_str2)
    
    dict1 = rank_to_dict(rank1)
    dict2 = rank_to_dict(rank2)
    
    all_elements = dict1.keys()
    
    contradictions = []
    
    for elem1, elem2 in combinations(sorted(all_elements), 2):
        if str(elem1) > str(elem2):
            continue
        
        rank11 = min(dict1[elem1])
        rank12 = min(dict1[elem2])
        rank21 = min(dict2[elem1])
        rank22 = min(dict2[elem2])
        
        if rank11 == rank12 or rank21 == rank22:
            continue
        
        if (rank11 < rank12) == (rank21 < rank22):
            continue
        
        contradictions.append((elem1, elem2))
    
    return contradictions


def get_all_objects(ranking):
    objects = set()
    for item in ranking:
        if isinstance(item, list):
            objects.update(str(x) for x in item)
        else:
            objects.add(str(item))
    return sorted(objects)


def build_relation_matrix(ranking, objects_map):
    n = len(objects_map)
    Y = np.zeros((n, n), dtype=int)
    
    for i in range(n):
        Y[i, i] = 1
    
    clusters = []
    for item in ranking:
        if isinstance(item, list):
            clusters.append([str(x) for x in item])
        else:
            clusters.append([str(item)])
    
    for i, cluster_i in enumerate(clusters):
        for obj_i in cluster_i:
            idx_i = objects_map[obj_i]
            for obj_j in cluster_i:
                idx_j = objects_map[obj_j]
                Y[idx_i, idx_j] = 1
        
        for j, cluster_j in enumerate(clusters):
            if i < j:
                for obj_i in cluster_i:
                    idx_i = objects_map[obj_i]
                    for obj_j in cluster_j:
                        idx_j = objects_map[obj_j]
                        Y[idx_i, idx_j] = 1
    
    return Y


def warshall_algorithm(E):
    n = E.shape[0]
    E_star = E.copy()
    
    for k in range(n):
        for i in range(n):
            for j in range(n):
                if E_star[i, k] == 1 and E_star[k, j] == 1:
                    E_star[i, j] = 1
    
    return E_star


def find_clusters(E_star, objects):
    n = E_star.shape[0]
    visited = [False] * n
    clusters = []
    
    for i in range(n):
        if not visited[i]:
            cluster = []
            for j in range(n):
                if E_star[i, j] == 1 and E_star[j, i] == 1:
                    cluster.append(objects[j])
                    visited[j] = True
            clusters.append(sorted(cluster))
    
    return clusters


def build_consistent_ranking(json_1, json_2):

    ranking_a = json.loads(json_1)
    ranking_b = json.loads(json_2)
    
    # 1. Подготовка данных
    objects_set = set()
    objects_set.update(get_all_objects(ranking_a))
    objects_set.update(get_all_objects(ranking_b))
    objects = sorted(objects_set)
    n = len(objects)
    
    objects_map = {obj: i for i, obj in enumerate(objects)}
    
    
    Y_A = build_relation_matrix(ranking_a, objects_map)
    Y_B = build_relation_matrix(ranking_b, objects_map)
    
    
    S = get_contradiction_core(json_1, json_2)
    
    
    C = Y_A * Y_B
    
    
    for (i, j) in S:
        idx_i = objects_map[str(i)]
        idx_j = objects_map[str(j)]
        C[idx_i, idx_j] = 1
        C[idx_j, idx_i] = 1
    
    
    C_T = C.T
    E = C * C_T
    E_star = warshall_algorithm(E)
    
    clusters = find_clusters(E_star, objects)
    
    
    obj_to_cluster = {}
    for cluster_idx, cluster in enumerate(clusters):
        for obj in cluster:
            obj_to_cluster[obj] = cluster_idx
    
    k = len(clusters)
    cluster_order = np.zeros((k, k), dtype=int)
    
    for i in range(k):
        for j in range(k):
            if i != j:
                order_consistent = True
                for obj_i in clusters[i]:
                    for obj_j in clusters[j]:
                        idx_i = objects_map[obj_i]
                        idx_j = objects_map[obj_j]
                        if C[idx_i, idx_j] == 0:
                            order_consistent = False
                            break
                    if not order_consistent:
                        break
                
                if order_consistent:
                    cluster_order[i, j] = 1
    
    indegree = [0] * k
    for i in range(k):
        for j in range(k):
            if cluster_order[i, j] == 1:
                indegree[j] += 1
    
    queue = deque([i for i in range(k) if indegree[i] == 0])
    sorted_clusters = []
    
    while queue:
        current = queue.popleft()
        sorted_clusters.append(clusters[current])
        
        for j in range(k):
            if cluster_order[current, j] == 1:
                indegree[j] -= 1
                if indegree[j] == 0:
                    queue.append(j)
    
    result = []
    for cluster in sorted_clusters:
        if len(cluster) == 1:
            result.append(int(cluster[0]))
        else:
            int_cluster = []
            for item in cluster:
                int_cluster.append(int(item))
            result.append(int_cluster)
    
    return result


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
    range_b = np.array(build_matrix(rank_b, n))
    
    YAB = range_a * range_b
    range_prime = range_a.T * range_b.T
    
    return find_kernel(YAB.tolist(), range_prime.tolist())


if __name__ == "__main__":

    json_a = read_json_file("a.json")
    json_b = read_json_file("b.json")
    json_c = read_json_file("c.json")
    
    print("Результаты:")
    print(f"Ядро противоречий (range_a range_b): {main(json_a, json_b)}")
    print(f"Ядро противоречий (range_a range_c): {main(json_a, json_c)}")
    print(f"Ядро противоречий (range_b range_c): {main(json_b, json_c)}")
    
    print("\nСогласованные ранжировки:")
    print(f"range_a и range_b: {build_consistent_ranking(json_a, json_b)}")
    print(f"range_a и range_c: {build_consistent_ranking(json_a, json_c)}")
    print(f"range_b и range_c: {build_consistent_ranking(json_b, json_c)}")