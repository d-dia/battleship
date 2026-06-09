"""Базовые структуры данных для игры Морской бой"""


class Stack:
    """Стек для отмены последнего выстрела игрока"""

    def __init__(self):
        self.items = []

    def push(self, item):
        self.items.append(item)

    def pop(self):
        # снимаем верхний элемент, если стек пуст возвращаем None
        return self.items.pop() if self.items else None

    def is_empty(self):
        return len(self.items) == 0


class Queue:
    """Очередь клеток для добивания корабля компьютером"""

    def __init__(self):
        self.items = []

    def enqueue(self, item):
        self.items.append(item)

    def dequeue(self):
        # берем элемент из начала очереди, если пусто возвращаем None
        return self.items.pop(0) if self.items else None

    def is_empty(self):
        return len(self.items) == 0


class Node:
    """Узел дерева, ключ это номер строки, значение это множество свободных столбцов"""

    def __init__(self, key, value):
        self.key = key
        self.value = value
        self.left = None
        self.right = None


class BST:
    """Бинарное дерево поиска свободных клеток по номеру строки"""

    def __init__(self):
        self.root = None

    def insert(self, key, value):
        """Добавляет строку с множеством свободных столбцов"""
        self.root = self._insert(self.root, key, value)

    def _insert(self, node, key, value):
        if node is None:
            return Node(key, value)
        if key < node.key:
            node.left = self._insert(node.left, key, value)
        elif key > node.key:
            node.right = self._insert(node.right, key, value)
        return node

    def build_balanced(self, pairs):
        """Строит ровное дерево из отсортированного по ключу списка пар ключ значение"""
        if pairs:
            mid = len(pairs) // 2            # середину берем корнем, дерево не вытягивается в цепочку
            key, value = pairs[mid]
            self.insert(key, value)
            self.build_balanced(pairs[:mid])
            self.build_balanced(pairs[mid + 1:])

    def search(self, key):
        """Ищет узел по номеру строки спуском по дереву"""
        node = self.root
        while node is not None:
            if key == node.key:
                return node
            node = node.left if key < node.key else node.right
        return None

    def all_cells(self):
        """Возвращает все свободные клетки симметричным обходом дерева"""
        result = []
        self._inorder(self.root, result)
        return result

    def _inorder(self, node, result):
        if node is not None:
            self._inorder(node.left, result)
            for col in node.value:
                result.append((node.key, col))
            self._inorder(node.right, result)


def binary_search(sorted_list, value):
    """Бинарный поиск значения в отсортированном по возрастанию списке"""
    low, high = 0, len(sorted_list) - 1
    while low <= high:
        mid = (low + high) // 2
        if sorted_list[mid] == value:
            return True
        if sorted_list[mid] < value:
            low = mid + 1
        else:
            high = mid - 1
    return False


def merge_sort(data):
    """Сортировка слиянием, возвращает новый отсортированный список"""
    if len(data) <= 1:
        return list(data)
    mid = len(data) // 2
    left = merge_sort(data[:mid])
    right = merge_sort(data[mid:])
    result = []
    i = j = 0
    while i < len(left) and j < len(right):     # сливаем две отсортированные половины
        if left[i] <= right[j]:
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1
    result.extend(left[i:])
    result.extend(right[j:])
    return result