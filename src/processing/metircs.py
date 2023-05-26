import math
import re


class MetricsCppCode:
    def __init__(self, function_code: str = ''):
        self.__src = function_code
        self.__code_lines = self.__delete_blank_and_comments()

    def set_function_code(self, function_code: str):
        self.__src = function_code
        self.__code_lines = self.__delete_blank_and_comments()

    @staticmethod
    def split_code_by_lines(code: str) -> list[str]:
        return re.split(r'\n(?=[^"]*(?:"[^"]*"[^"]*)*$)', code)

    @staticmethod
    def __get_re_for_comments() -> str:
        return r'(//.*)|(/\*[\s\S]*?\*/)'

    def __delete_blank_and_comments(self):
        clean_code = re.sub(self.__get_re_for_comments(), '', self.__src)
        code_lines = self.split_code_by_lines(clean_code)
        return [line.strip() for line in code_lines if line.strip()]

    def count(self) -> dict[str, int | float]:
        return {
            'loc': self.count_loc(),
            'v(g)': self.count_vg(),
            **self.count_n_metrics(),
            **self.count_halsted_loc_metrics()
        }

    def count_loc(self) -> int:
        return len(self.__code_lines)

    def count_vg(self) -> int:
        """
        v(g) = π − s + 2,
        π — число точек ветвления в программе,
        s — число точек выхода
        """
        def count_occurrences(code_lines: list[str], word: str) -> int:
            return sum([line.count(word) for line in code_lines])

        complexity = 2

        branch_points = ['if', 'for', 'while', 'case', '||', '&&', 'catch', 'goto']
        for point in branch_points:
            complexity += count_occurrences(self.__code_lines, point)

        exit_points = ['return', 'exit', 'throw']
        for point in exit_points:
            complexity -= count_occurrences(self.__code_lines, point)

        # Если void, то в конце можно не делать return, однако complexity должна измениться
        if 'void' in self.__code_lines[0]:
            last_lines = self.__code_lines[-2] + self.__code_lines[-1]
            if 'return' not in last_lines:
                complexity -= 1
            else:
                for point in branch_points + ['else', 'default']:
                    if point in self.__code_lines[-3]:
                        complexity -= 1
                        break

        return complexity if complexity > 0 else 1

    def count_n_metrics(self) -> dict[str, int | float]:
        # Вынесены отдельно, потому что возникают трудности,
        # связанные с типами при объявлении переменных
        equal_operator = r'(?<!=|!|>|<|\+|-|\*|\/|%|&|\||\^)=(?!=)'
        asterisk_operator = r'\*(?!=)'

        # Регулярные выражения написаны для того,
        # чтобы различать операторы, входящие в состав других (н-р, > и >=)
        regex_operators = [
            equal_operator,
            r'(?<!\+)\+(?!\+|=)', r'(?<!-)-(?!-|=)',
            r'\/(?!=)', r'%(?!=)',
            r'(?<!>)>(?!=|>)', r'(?<!<)<(?!=|<)',
            r'==', r'!=', r'(?<!>)>=', r'(?<!<)<=',
            r'(?<!&)&(?!&|=)', r'(?<!\|)\|(?!\||=)', r'\^(?!=)',
            r'<<(?!=)', r'>>(?!=)',
            r'\+=', r'-=', r'\*=', r'\/=', r'%=',
            r'&=', r'\|=', r'\^=', r'<<=', r'>>=',
            r'\[', r'\.(?=[^0-9])', r'->', r',', r'\(',
            r'!(?!=)', r'~',
            r'\+\+', r'--',
            r'&&', r'\|\|',
            r'\bif\b', r'\belse\b', r'\?',
            r'\bfor\b', r'\bwhile\b',
            r'::', r'\bnew\b', r'\bdelete\b', r'\breturn\b',
            r'\bsizeof\b', r'\btypeid\b',
            r'\bswitch\b', r'\bcase\b', r'\bdefault\b',
            r'\bgoto\b', r'\btry\b', r'\bcatch\b', r'\bthrow\b',
            r'\bconst_cast\b', r'\bstatic_cast\b',
            r'\bdynamic_cast\b', r'\breinterpret_cast\b',
        ]

        pattern_operators = '|'.join(regex_operators)
        operators: list[str] = []
        operands: list[str] = []

        for line in self.__code_lines[1:]:
            operators_from_line = re.findall(pattern_operators + rf'|{asterisk_operator}', line)
            if not operators_from_line:
                continue

            operators.extend(operators_from_line)
            line = re.sub(r'(\s+|^)\w+\s*\(|\)|const\s+|{|}|]', r' ', line)

            eq_operands = re.split(equal_operator, line, maxsplit=1)
            if len(eq_operands) > 1 and eq_operands[0]:
                left_eq_operands = [operand.strip() for operand in re.split(pattern_operators, eq_operands[0])
                                    if operand.strip()]
                left_operand = re.split(rf' |{asterisk_operator}', left_eq_operands[0])
                left_operand = [operand.strip() for operand in left_operand if operand.strip()]

                if len(left_operand) > 1:
                    operands.extend(left_operand[1:])
                else:
                    operands.append(left_operand[0])

                for operand in left_eq_operands[1:]:
                    operands.extend(operand.split(' '))
                line = '=' + eq_operands[1]

            if len(re.split(equal_operator, line)) == 1:
                aster_operands = re.split(asterisk_operator, line)
                aster_operands = [operand.strip() for operand in aster_operands]
                if len(aster_operands) > 1:
                    line = ','.join(aster_operands[1:])

            tokens = re.split(pattern_operators + rf'|;|{asterisk_operator}|:', line)
            tokens = [token.strip() for token in tokens if token.strip()]
            if tokens:
                first_token = tokens[0].split(' ', maxsplit=1)
                if len(first_token) > 1:
                    tokens[0] = first_token[1].strip()

            for token in tokens:
                operands.extend(token.split(' '))

        operators = [operator.replace('(', '()').replace('[', '[]').replace('?', '? :')
                     for operator in operators]

        N1 = len(operators)
        N2 = len(operands)
        n1 = len(set(operators))
        n2 = len(set(operands))

        # Необходимые значения метрик
        N = N1 + N2
        V = N * math.log2(n1 + n2) if n1 != 0 or n2 != 0 else 0.
        D = (n1 / 2) * (N2 / n2) if n2 != 0 else 0.
        I = V / D if D != 0. else 0.
        E = V * D
        B = V / 3000
        T = E / 18

        return {
            'n': N,
            'v': round(V, 2),
            'd': round(D, 2),
            'i': round(I, 2),
            'e': round(E, 2),
            'b': round(B, 2),
            't': round(T, 2),
            'uniq_Op': n1,
            'uniq_Opnd': n2,
            'total_Op': N1,
            'total_Opnd': N2,
        }

    def count_halsted_loc_metrics(self) -> dict[str, int]:
        code_lines = self.split_code_by_lines(self.__src)
        blank_lines = [line for line in code_lines if not line.strip()]

        comment_lines = re.findall(self.__get_re_for_comments(), self.__src)
        comment_lines = [next(filter(None, line)) for line in comment_lines]
        comment_lines = [len(self.split_code_by_lines(line)) for line in comment_lines]

        mixed_lines = re.findall(r';\s*//', self.__src)

        return {
            'lOCode': len(code_lines),
            'lOComment': sum(comment_lines),
            'lOBlank': len(blank_lines),
            'lOCodeAndComment': len(mixed_lines),
        }


if __name__ == '__main__':
    metrics = MetricsCppCode('''
void main() {
    // Comment
    
    // prom
    /*
    some
    comments
    */
    int* p = new int(25);  // comm
    int a = 1;
    std::string b = "abc";
    std::string new_word;
    float a1, a2;
    
    if (b != "\n" || a == 1)
        std::cout << b << std::endl;
    else
        return 1;    
    
    int c, d = 4;
    a += c + d + 2;
    
    int array[10];
    int array2[11] = { 0 };
    array[1] = 12;
    
    const int* AA = 1;
    const int* arr, arr2;
    const int** arr3;
    a *= 2;
    a = 2 * 12;
    a = (int) 1.2;
    foo(foo_a, foo_b, foo_c);  // 1234
    Boo::boo(foo_a, foo_b, foo_c);
    c = 1 + 2 * 9;
    for (int i = 0; i < 10; i++)
        array[i] = i;
    delete p;
    
    int b = (a == 1 ? 2 : 3);
    switch (a)
    {
        case 2:
            std::cout << "smth";
            break;
        case 1:
            return;
        default:
            std::cout << "end";
    }
    std::cout << sizeof(array);
    a = static_cast<int,float>(1,2);
}
''')

    print(metrics.count())
