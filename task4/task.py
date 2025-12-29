import json
import os
import numpy as np


def find_min_x(points: list[list[float]], z: float):
    if not points:
        return None

    if points[0][1] >= z:
        return points[0][0], z

    for i in range(len(points) - 1):
        x1, y1 = points[i]
        x2, y2 = points[i + 1]

        if y1 >= z:
            return x1, z

        if x2 == x1 or y2 == y1:
            continue

        crosses = (y1 < z <= y2) or (y1 > z >= y2)
        if not crosses:
            continue

        k = (y2 - y1) / (x2 - x1)
        x_intersect = x1 + (z - y1) / k
        return x_intersect, z

    max_y = max(y for x, y in points)
    for x, y in points:
        if y == max_y:
            return x, y

    return None


def member_ratio(x: float, points: list[list[float]]) -> float:
    if not points:
        return 0.0

    if x <= points[0][0]:
        return float(points[0][1])
    if x >= points[-1][0]:
        return float(points[-1][1])

    for i in range(len(points) - 1):
        x1, y1 = points[i]
        x2, y2 = points[i + 1]

        if x1 <= x <= x2:
            if x1 == x2:
                return float(max(y1, y2))
            return float(y1 + (y2 - y1) * (x - x1) / (x2 - x1))

    return 0.0


def faze_temperature(temp: float, temp_terms: list[dict]) -> dict[str, float]:
    fuzzy = {}
    for term in temp_terms:
        term_id = term["id"]
        points = term["points"]
        fuzzy[term_id] = member_ratio(temp, points)
    return fuzzy


def apply_rules(fuzzy_temp: dict[str, float], rules: list, heat_terms: list[dict]) -> list[dict]:
    heat_by_id = {term["id"]: term for term in heat_terms}

    activated_sets = []
    for temp_term, heat_term in rules:
        activation = float(fuzzy_temp.get(temp_term, 0.0))
        if activation <= 0:
            continue

        heat_mf = heat_by_id.get(heat_term)
        if not heat_mf:
            continue

        activated_sets.append(
            {
                "term": heat_term,
                "activation": activation,
                "points": heat_mf["points"],
            }
        )

    return activated_sets


def main(temp_mf_json: str, heat_mf_json: str, rules_json: str, current_temp: float) -> float:
    temp_data = json.loads(temp_mf_json)
    heat_data = json.loads(heat_mf_json)
    rules = json.loads(rules_json)

    temp_terms = temp_data.get("температура", [])
    heat_terms = heat_data.get("температура", [])

    faze_temp = faze_temperature(float(current_temp), temp_terms)
    activated_sets = apply_rules(faze_temp, rules, heat_terms)

    if not activated_sets:
        return 0.0

    candidates = []
    for s in activated_sets:
        p = find_min_x(s["points"], s["activation"])
        if p is not None:
            candidates.append(p)

    if not candidates:
        return 0.0

    max_val = max(y for x, y in candidates)

    optimal_control = 0.0
    for x, y in candidates:
        if y == max_val:
            optimal_control = x

    return float(optimal_control)


if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))

    temp_path = os.path.join(current_dir, "temps.json")
    heat_path = os.path.join(current_dir, "heats.json")
    rules_path = os.path.join(current_dir, "rules.json")

    with open(temp_path, "r", encoding="utf-8") as file:
        temps = file.read()

    with open(heat_path, "r", encoding="utf-8") as file:
        heats = file.read()

    with open(rules_path, "r", encoding="utf-8") as file:
        rules = file.read()

    test_tempes = [15, 20, 23, 25, 30]

    for t in test_tempes:
        control = main(temps, heats, rules, float(t))
        print(f"Температура: {t} -> Управление: {control}")
