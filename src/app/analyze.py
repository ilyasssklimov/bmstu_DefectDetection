import matplotlib
import matplotlib.pyplot as plt
import pandas as pd
from random import randint, choice
from src.model.model import GBDDModel
from src.processing.metircs import MetricsCppCode
from time import time

REPEAT_TIMES = 30


def generate_line(operators_cnt: int) -> str:
    operators = ['+', '-', '*', '/', '=', '<', '>', 'if', '&&', '||']
    operands = ['a', 'b', 'c', 'd', '1', '2', '3', '4']
    line = [f'{choice(operands)} {choice(operators)}' for _ in range(operators_cnt)]
    return ' '.join(line) + f' {choice(operands)}\n'


def generate_code(lines_cnt: int) -> str:
    code = 'void foo() {\n'

    for i in range(lines_cnt):
        code += generate_line(randint(1, 5))

    return code + '}\n'


def count_time(metrics: MetricsCppCode, model: GBDDModel, function: str) -> float:
    get_time = time
    result_time = 0.

    for _ in range(REPEAT_TIMES):
        start_time = get_time()
        metrics.set_function_code(function)
        metric_values = metrics.count()
        _ = model.predict_proba(pd.DataFrame(metric_values, index=[0]))[0][1]
        result_time += get_time() - start_time

    return result_time / REPEAT_TIMES


def main():
    metrics = MetricsCppCode()
    model = GBDDModel(model_file='./model.pkl')
    times: list[float] = []

    for lines_cnt in range(0, 2000, 20):
        print(f'LINES = {lines_cnt}')
        function = generate_code(lines_cnt)
        times.append(count_time(metrics, model, function))

    print(times)
    matplotlib.use('Qt5Agg')
    plt.plot(list(range(0, 2000, 20)), times)
    plt.xlabel('Количество строк')
    plt.ylabel('Время выполнения, сек')
    plt.show()


if __name__ == '__main__':
    main()
