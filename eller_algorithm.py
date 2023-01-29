import random


def merge_sets(row: list[int], set_number1, set_number2) -> list[int]:
    for i in range(len(row)):
        if row[i] == set_number2:
            row[i] = set_number1
    return row


def generate_right_borders(row: list[int]) -> tuple[list[bool], list[int]]:
    borders: list[bool] = [False for _ in range(len(row))]

    for i in range(len(row) - 1):
        choice: bool = bool(random.randint(0, 1))
        if choice or row[i] == row[i + 1]:
            borders[i] = True
        else:
            row = merge_sets(row, row[i], row[i + 1])
    borders[-1] = True
    return borders, row


def number_of_elements_in_set(row: list[int], set_number: int) -> int:
    count: int = 0
    for i in row:
        if i == set_number:
            count += 1
    return count


def number_of_horizontal_borders_in_set(row: list[int], set_number: int, borders: list[bool]) -> int:
    count: int = 0
    for i in range(len(row)):
        if row[i] == set_number and borders[i]:
            count += 1
    return count


def generate_down_borders(row: list[int]) -> list[bool]:
    borders: list[bool] = [False for _ in range(len(row))]

    for i in range(len(row)):
        choice: bool = bool(random.randint(0, 1))
        if choice and number_of_elements_in_set(row, row[i]) - \
                number_of_horizontal_borders_in_set(row, row[i], borders) != 1:
            borders[i] = True
    return borders


def generate_labyrinth(width: int, height: int) -> tuple[list[list[bool]], list[list[bool]]]:
    # initial setup
    next_set: int = 1
    matrix_right_borders = []
    matrix_down_borders = []

    # create first line with no cells added to any set
    sets: list[int] = [0 for _ in range(width)]

    # main cycle for the algorithm
    for row in range(height):
        # step 2: assign set to cells without it
        for col in range(width):
            if sets[col] == 0:
                sets[col] = next_set
                next_set += 1
        # step 3: add right borders
        cur_right_borders, sets = generate_right_borders(sets)
        matrix_right_borders.append(cur_right_borders)
        # step 4: add down borders
        matrix_down_borders.append(generate_down_borders(sets))
        if row != height - 1:  # not the last line
            for i in range(len(sets)):
                if matrix_down_borders[row][i]:
                    sets[i] = 0
        else:
            for i in range(width):
                matrix_down_borders[row][i] = True
                if i != width - 1 and sets[i] != sets[i + 1]:
                    matrix_right_borders[row][i] = False
                    sets = merge_sets(sets, sets[i], sets[i + 1])

    return matrix_right_borders, matrix_down_borders
