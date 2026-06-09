import random
from structures import Stack, merge_sort, binary_search
from field import (SIZE, new_game, fix_loaded, build_free_tree, targets_from_hits,
                   print_field, find_ship, is_sunk, remaining_sizes)
from saving import save_to_file, load_from_file


def show_help():
    """Печатает список доступных команд"""
    print("Команды:")
    print("  <строка> <столбец>  - выстрел, например: 3 5")
    print("  undo                - отменить свой последний выстрел")
    print("  stats               - статистика по кораблям компьютера")
    print("  save                - сохранить партию в файл")
    print("  myfield             - показать свое поле")
    print("  help                - показать команды")
    print("  quit                - выход")


def start_game():
    """Спрашивает игрока, загрузить партию из файла или начать новую"""
    answer = input("Загрузить сохраненную партию? (д/н): ").strip().lower()
    if answer == 'д':
        name = input("Имя файла: ").strip()
        try:
            g = load_from_file(name)
            fix_loaded(g)
            print("Партия загружена.")
            return g
        except FileNotFoundError:
            print("Файл не найден, начинаем новую партию.")
    return new_game()


def computer_turn(g, free, targets):
    """Делает ход компьютера и возвращает обновленную очередь добивания"""
    target = None
    while not targets.is_empty():              # сначала клетки из очереди добивания
        cell = targets.dequeue()
        node = free.search(cell[0])
        if node is not None and cell[1] in node.value:
            target = cell
            break
    if target is None:                         # иначе случайная свободная клетка
        free_cells = free.all_cells()
        if free_cells:
            target = random.choice(free_cells)
    if target is None:
        return targets

    tr, tc = target
    node = free.search(tr)
    if node is not None:
        node.value.discard(tc)                 # клетка больше не свободна
    if g["player_field"][tr][tc] == 'S':
        g["player_field"][tr][tc] = 'X'
        g["cells_left_player"] -= 1
        g["current_hits"].append((tr, tc))
        if is_sunk(g["player_field"], find_ship(g["player_ships"], tr, tc)):
            print(f"Компьютер стреляет ({tr}, {tc}) - потопил ваш корабль!")
            g["current_hits"] = []
            return targets_from_hits([], free)
        print(f"Компьютер стреляет ({tr}, {tc}) - попал!")
        return targets_from_hits(g["current_hits"], free)
    g["player_field"][tr][tc] = '*'
    print(f"Компьютер стреляет ({tr}, {tc}) - мимо.")
    return targets


def show_stats(g):
    """Показывает статистику с сортировкой и бинарным поиском"""
    sizes = merge_sort(remaining_sizes(g["comp_field"], g["comp_ships"]))
    print(f"Выстрелов: {g['shots']}, попаданий: {g['hits']}")
    print(f"Осталось кораблей у компьютера: {len(sizes)}")
    print(f"Их размеры по возрастанию: {sizes}")
    for size in (1, 2, 3, 4):                  # бинарный поиск размеров еще на плаву
        print(f"  корабль размера {size} еще на плаву: {binary_search(sizes, size)}")


def undo_move(g, undo_stack):
    """Отменяет последний выстрел игрока и возвращает счетчики назад"""
    last = undo_stack.pop()
    if last is None:
        print("Отменять нечего.")
        return
    r, c, old, was_hit = last
    g["comp_field"][r][c] = old
    g["shots"] -= 1
    if was_hit:
        g["cells_left_comp"] += 1
        g["hits"] -= 1
    print(f"Выстрел ({r}, {c}) отменен.")


def player_shot(g, undo_stack, command):
    """Разбирает команду выстрела, стреляет по полю компьютера, возвращает True при удачном выстреле"""
    parts = command.split()
    if len(parts) != 2 or not parts[0].isdigit() or not parts[1].isdigit():
        print("Неизвестная команда. Введите номер строки и столбца, например: 3 5.")
        return False
    r, c = int(parts[0]), int(parts[1])
    if not (0 <= r < SIZE and 0 <= c < SIZE):
        print("Координаты вне поля (0..9).")
        return False
    if g["comp_field"][r][c] in ('X', '*'):
        print("Сюда уже стреляли.")
        return False

    g["shots"] += 1
    if g["comp_field"][r][c] == 'S':
        g["comp_field"][r][c] = 'X'
        g["cells_left_comp"] -= 1
        g["hits"] += 1
        undo_stack.push([r, c, 'S', True])     # запоминаем ход для отмены
        print("Потопил!" if is_sunk(g["comp_field"], find_ship(g["comp_ships"], r, c)) else "Попал!")
    else:
        g["comp_field"][r][c] = '*'
        undo_stack.push([r, c, '~', False])
        print("Мимо.")
    return True


def main():
    """Главный цикл игры"""
    print("            МОРСКОЙ БОЙ")
    g = start_game()

    undo_stack = Stack()
    undo_stack.items = g["undo"]               # стек отмены работает прямо со списком партии
    free = build_free_tree(g["player_field"])  # дерево свободных клеток компьютера
    targets = targets_from_hits(g["current_hits"], free)

    show_help()
    print("\nВаши корабли расставлены автоматически:")
    print_field(g["player_field"], hide_ships=False)

    while True:
        print("\nПоле компьютера (стреляете сюда):")
        print_field(g["comp_field"], hide_ships=True)
        command = input("\nВаш ход: ").strip().lower()

        if command == "quit":
            print("Игра завершена.")
            break
        if command == "help":
            show_help()
            continue
        if command == "myfield":
            print("\nВаше поле, X это попадания компьютера, * это его промахи:")
            print_field(g["player_field"], hide_ships=False)
            continue
        if command == "save":
            name = input("Имя файла (например game.json): ").strip() or "save.json"
            save_to_file(name, g)
            print(f"Партия сохранена в {name}.")
            continue
        if command == "stats":
            show_stats(g)
            continue
        if command == "undo":
            undo_move(g, undo_stack)
            continue

        # обычный выстрел игрока
        if not player_shot(g, undo_stack, command):
            continue
        if g["cells_left_comp"] == 0:
            print("\nВЫ ПОБЕДИЛИ! Все корабли компьютера потоплены.")
            break

        # ответный ход компьютера
        targets = computer_turn(g, free, targets)
        if g["cells_left_player"] == 0:
            print("\nКомпьютер победил. Все ваши корабли потоплены.")
            print_field(g["player_field"], hide_ships=False)
            break


if __name__ == "__main__":
    main()