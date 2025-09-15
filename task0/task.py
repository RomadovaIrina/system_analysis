# на вход строка 1,2,5\n 2,3, такого вида. Вернуть list из list
# кр примерно через 2-3 лабы


def main(data: str) -> list[list[int]]:
    # Сплитим данные по переводу строки
    rows = data.strip().split('\n')

    # Ребра и вершины
    edges = []
    vertices = set()

    for row in rows:
        v_1, v_2 = row.split(",")

        edges.append((v_1, v_2))
        vertices.add(v_1)
        vertices.add(v_2)

    vertices = sorted(vertices)
    num_verts = len(vertices)

    mat = [ [0] * num_verts for _ in range(num_verts)]

    for v1, v2 in edges:
        i , j = vertices.index(v1), vertices.index(v2)
        mat[i][j] = mat[j][i] = 1

    return mat








if __name__ == "__main__":

    data_path = ('task0.csv')
    with open(data_path, "r") as file:
        input_data = file.read()
    result = main(input_data)

    for i in result:
        print(i)