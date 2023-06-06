from random import choice


def generate_line(operators_cnt: int) -> str:
    operators = ['+', '-', '*', '/', '=', '<', '>', 'if', '&&', '||']
    operands = ['a', 'b', 'c', 'd', '1', '2', '3', '4']
    line = [f'{choice(operands)} {choice(operators)}' for _ in range(operators_cnt)]
    return ' '.join(line) + f' {choice(operands)}\n'


def generate_code(lines_cnt: int) -> str:
    code = 'void foo() {\n'

    for _ in range(lines_cnt):
        code += generate_line(4)

    return code + '}\n'
