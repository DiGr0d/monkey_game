import heapq
import math

def heuristic(a, b):
    return math.hypot(a[0] - b[0], a[1] - b[1])

def a_star(grid, start, goal, return_cost=False):
    """
    Ищет путь по сетке grid от start до goal с использованием A*.
    grid должен иметь метод get_neighbors(x, y, allow_diagonal=True)
    и is_walkable(x, y).
    Если return_cost=False (по умолчанию): возвращает список клеток от start до goal (включая start).
    Если return_cost=True: возвращает кортеж (path, cost), где cost - общая стоимость пути.
    Если путь не найден: при return_cost=False возвращает [], при return_cost=True возвращает ([], float('inf')).
    """
    if not grid.is_walkable(*goal) or start == goal:
        if return_cost:
            return float('inf')
        return []

    open_set = []
    heapq.heappush(open_set, (0, start))
    came_from = {start: None}
    g_score = {start: 0}
    f_score = {start: heuristic(start, goal)}

    while open_set:
        _, current = heapq.heappop(open_set)

        if current == goal:
            break

        for neighbor in grid.get_neighbors(current[0], current[1], allow_diagonal=True):
            dx = neighbor[0] - current[0]
            dy = neighbor[1] - current[1]
            move_cost = math.sqrt(2) * grid.cells[neighbor[0]][neighbor[1]].weight if dx != 0 and dy != 0 else grid.cells[neighbor[0]][neighbor[1]].weight
            tentative_g = g_score[current] + move_cost

            if neighbor not in g_score or tentative_g < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g
                f = tentative_g + heuristic(neighbor, goal)
                f_score[neighbor] = f
                heapq.heappush(open_set, (f, neighbor))

    if goal not in came_from:
        if return_cost:
            return float('inf')
        return []

    if return_cost:
        return g_score[goal]

    # Восстанавливаем путь
    path = []
    current = goal
    while current is not None:
        path.append(current)
        current = came_from[current]
    path.reverse()

    return path
