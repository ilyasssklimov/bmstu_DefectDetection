import os
import pandas as pd
from random import choice, randint, shuffle
from src.model.model import GBDDModel
from src.processing.metircs import MetricsCppCode
from utils import generate_line

TEST_PATH = r'..\..\data\test'
LINES_CNT = 1000


def get_defect() -> str:
    defects = [
        'double a = 1 / 33;\n'
        'std::cout << "Count sum..." << std::endl;\n'
        'for (double b = 0; b < 1; b += a) {}\n',

        'int sum = 0;\n'
        'int i = 0, j = 0;  // Неверное место инициализации\n'
        'for (; i < 10; i++) {\n'
        'for (; j < n, j++) {\n'
        'sum += i + j;\n'
        '}\n'
        '}\n',

        'int array[5] = {-1, -2, -3, -4, -5};\n'
        'int max = 0;  // Неверная инициализация\n'
        'for (int i = 0; i < 5; i++) {\n'
        'if (array[i] > max)\n'
        'max = array[i];\n'
        '}\n',

        'std::string name = "file";\n'
        '// Отсутствует обработка else, что может привести к неверному расширению\n'
        'if (idx == 0)\n'
        'name += ".txt";\n'
        'else if (idx == 1)\n'
        'name += ".cpp"\n'
        'create_file(name);\n',

        'int array[3] = { 0, 1, 2 };\n'
        'for (int i = 0; i < 3; i++) {\n'
        'if (i % 2 != 0) {\n'
        '// Необходимо дополнительно аллоцировать память\n'
        'array[i * 2] = i;\n'
        '}\n'
        '}\n',

        'int a = 5;\n'
        'if (name == "file" || a > 4) {\n'
        'a = 10;\n'
        'return &a;  // указатель на локальную переменную\n'
        '}\n',
    ]
    return choice(defects)


def generate_test(lines_cnt: int) -> tuple[str, float]:
    code_lines: list[str] = []
    defects_cnt = randint(1, 10)

    for _ in range(lines_cnt):
        code_lines.append(generate_line(randint(1, 4)))
    for _ in range(defects_cnt):
        code_lines.append(get_defect())

    shuffle(code_lines)
    proba = sum([len(line.split('\n')) for line in code_lines[-defects_cnt:]]) / lines_cnt * 6
    proba = proba if proba <= 1. else 1.
    return 'void foo() {\n' + ''.join(code_lines) + '}', proba


def generate_tests():
    expected_proba = ''

    for i in range(LINES_CNT):
        test = generate_test(randint(10, 100))
        with open(os.path.join(TEST_PATH, f'{i}.cpp'), 'w', encoding='UTF8') as f:
            f.write(test[0])
        expected_proba += str(test[1]) + '\n'

    with open(os.path.join(TEST_PATH, 'proba.txt'), 'w', encoding='UTF8') as f:
        f.write(expected_proba)


def check_results():
    model = GBDDModel(model_file=r'..\app\model.pkl')
    metrics = MetricsCppCode()
    incorrect_cnt = 0
    errors = 0.

    with open(os.path.join(TEST_PATH, 'proba.txt'), encoding='UTF8') as f:
        expected_proba = list(map(float, f.read().split()))

    for i in range(LINES_CNT):
        with open(os.path.join(TEST_PATH, f'{i}.cpp'), encoding='UTF8') as f:
            code = f.read()

        metrics.set_function_code(code)
        code_metrics = metrics.count()
        defects_proba = model.predict_proba(pd.DataFrame(code_metrics, index=[0]))[0][1]

        if abs(defects_proba - expected_proba[i]) > 0.2:
            print(f'LINE #{i}: expected = {expected_proba[i]}, calculated = {defects_proba}')
            incorrect_cnt += 1
            errors += abs(expected_proba[i] - defects_proba)

    print(f'{incorrect_cnt = }, {incorrect_cnt / LINES_CNT:.2f}%, {errors = :.2f}')


def main():
    # generate_tests()
    check_results()


if __name__ == '__main__':
    main()
