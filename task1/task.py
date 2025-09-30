import os
import numpy as np


def main(data: str, eroot: str) -> list[list[int]]:
    rows = data.strip().split("\n")
    edges = []
    verts = set()

    for row in rows:
        v1, v2 = map(str.strip, row.split(","))
        edges.append((v1, v2))
        verts.add(v1)
        verts.add(v2)

    ordered_verts = [eroot] + sorted(v for v in verts if v != eroot)
    n = len(ordered_verts)
    vert_index = {v: i for i, v in enumerate(ordered_verts)}

    mat = np.zeros((n, n), dtype=bool)
    for v1, v2 in edges:
        i, j = vert_index[v1], vert_index[v2]
        mat[i, j] = True
    # Задаем матрицы отношений r1 и r2
    r1 = mat.astype(int)
    r2 = r1.T

    transit_r = mat.copy()
    for _ in range(1, n):
        transit_r |= transit_r @ mat
    # Получили r3 и r4
    r3 = ((transit_r & ~mat) > 0).astype(int)
    r4 = r3.T

    r2_bool = r2.astype(bool)
    r5 = np.zeros((n, n), dtype=int)
    for i in range(n):
        for j in range(i + 1, n):
            if np.any(r2_bool[i] & r2_bool[j]):
                r5[i, j] = r5[j, i] = 1

    return [r1.tolist(), r2.tolist(), r3.tolist(), r4.tolist(), r5.tolist()]


def print_matrices(matrices):
    relations = [
        "r1 (управление)",
        "r2 (подчинение)",
        "r3 (опосредованное управление)",
        "r4 (опосредованное подчинение)",
        "r5 (соподчинение)",
    ]

    for rel_name, matrix in zip(relations, matrices):
        print(f"\nМатрица для {rel_name}:")
        for row in matrix:
            print(row)


if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(current_dir, "task1.csv")
    with open(csv_path, "r") as file:
        input_data = file.read()

    eroot = input("Введите корень:").strip()
    matrices = main(input_data, eroot)
    print_matrices(matrices)
