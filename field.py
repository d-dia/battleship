"""Игровое поле, корабли и логика хода компьютера"""

import random
from structures import BST, Queue

SIZE = 10                                      # поле 10 на 10
SHIP_SIZES = [4, 3, 3, 2, 2, 2, 1, 1, 1, 1]    # размеры всех кораблей флота


def make_field():
    """Создает пустое поле, заполненное водой"""
    return [['~' for _ in range(SIZE)] for _ in range(SIZE)]


def cells_free(field, cells):
    """Проверяет, что клетки и их соседи свободны, корабли не должны касаться"""
    for (r, c) in cells:
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                nr, nc = r + dr, c + dc
                if 0 <= nr < SIZE and 0 <= nc < SIZE and field[nr][nc] == 'S':
                    return False
    return True


def place_ships(field):
    """Случайно расставляет корабли и возвращает список их клеток"""
    ships = []
    for size in SHIP_SIZES:
        while True:
            row = random.randint(0, SIZE - 1)
            col = random.randint(0, SIZE - 1)
            horizontal = random.choice([True, False])
            cells = []
            for i in range(size):
                r = row if horizontal else row + i
                c = col + i if horizontal else col
                cells.append((r, c))
            inside = all(0 <= r < SIZE and 0 <= c < SIZE for (r, c) in cells)
            if inside and cells_free(field, cells):
                for (r, c) in cells:
                    field[r][c] = 'S'
                ships.append(cells)
                break
    return ships


def print_field(field, hide_ships):
    """Выводит поле, при hide_ships чужие корабли показываются как вода"""
    print("    " + " ".join(str(c) for c in range(SIZE)))
    for r in range(SIZE):
        row = []
        for c in range(SIZE):
            cell = field[r][c]
            if cell == 'S' and hide_ships:
                cell = '~'
            row.append(cell)
        print(f"{r}   " + " ".join(row))


def find_ship(ships, r, c):
    """Находит корабль, которому принадлежит клетка"""
    for ship in ships:
        if (r, c) in ship:
            return ship
    return None


def is_sunk(field, ship):
    """Проверяет, потоплен ли корабль целиком"""
    return all(field[r][c] == 'X' for (r, c) in ship)


def remaining_sizes(field, ships):
    """Возвращает размеры еще не потопленных кораблей"""
    return [len(ship) for ship in ships if not is_sunk(field, ship)]


def next_targets(hits):
    """Подсказывает соседние клетки для добивания корабля"""
    if len(hits) == 1:                         # ориентация еще неизвестна
        r, c = hits[0]
        return [(r - 1, c), (r + 1, c), (r, c - 1), (r, c + 1)]
    rows = [r for r, c in hits]
    cols = [c for r, c in hits]
    if rows.count(rows[0]) == len(rows):       # все попадания в одной строке, корабль лежит вдоль
        r = rows[0]
        return [(r, min(cols) - 1), (r, max(cols) + 1)]
    c = cols[0]                                # иначе корабль стоит вертикально
    return [(min(rows) - 1, c), (max(rows) + 1, c)]


def build_free_tree(player_field):
    """Строит ровное дерево свободных клеток компьютера по полю игрока"""
    pairs = []
    for row in range(SIZE):
        free_cols = {c for c in range(SIZE) if player_field[row][c] in ('~', 'S')}
        pairs.append((row, free_cols))     # строки идут по порядку, ключи уже отсортированы
    tree = BST()
    tree.build_balanced(pairs)
    return tree


def targets_from_hits(hits, free):
    """Собирает очередь клеток для добивания по уже известным попаданиям"""
    queue = Queue()
    if hits:
        for (r, c) in next_targets(hits):
            if 0 <= r < SIZE and 0 <= c < SIZE:
                node = free.search(r)
                if node is not None and c in node.value:
                    queue.enqueue((r, c))
    return queue


def new_game():
    """Создает новую партию и возвращает словарь со всеми ее данными"""
    comp_field = make_field()
    player_field = make_field()
    fleet = sum(SHIP_SIZES)
    return {
        "comp_field": comp_field,
        "comp_ships": place_ships(comp_field),
        "player_field": player_field,
        "player_ships": place_ships(player_field),
        "cells_left_comp": fleet,
        "cells_left_player": fleet,
        "shots": 0,
        "hits": 0,
        "undo": [],            # список выстрелов игрока для отмены
        "current_hits": [],    # попадания по недобитому кораблю игрока
    }


def fix_loaded(g):
    """Превращает координаты из JSON списков обратно в кортежи"""
    g["comp_ships"] = [[tuple(cell) for cell in ship] for ship in g["comp_ships"]]
    g["player_ships"] = [[tuple(cell) for cell in ship] for ship in g["player_ships"]]
    g["current_hits"] = [tuple(cell) for cell in g["current_hits"]]