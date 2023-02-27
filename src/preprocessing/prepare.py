import pandas as pd
from scipy.io import arff


def prepare_nasa_dataset(filename: str):
    """
    1. loc              : numeric % McCabe's line count of code
                          количество всех непустых строк исходного кода без комментариев (PLOC)
    2. v(g)             : numeric % McCabe "cyclomatic complexity"
                          цикломатическая сложность
    3. ev(g)            : numeric % McCabe "essential complexity"
                          существенная сложность
    4. iv(g)            : numeric % McCabe "design complexity"
                          сложность проекта
    5. n                : numeric % Halstead total operators + operands
                          всего операторов и операндов
    6. v                : numeric % Halstead "volume"
                          объем (описывает размер реализации алгоритма)
    7. l                : numeric % Halstead "program length"
                          длина программы (размер программы только с операторами и операндами)
    8. d                : numeric % Halstead "difficulty"
                          сложность (пропорциональна количеству уникальных операторов)
    9. i                : numeric % Halstead "intelligence"
                          информационное содержание программы
    10. e               : numeric % Halstead "effort"
                          оценка необходимых усилий
    11. b               : numeric % Halstead "number of delivered bugs"
                          количество предполагаемых ошибок
    12. t               : numeric % Halstead's time estimator
                          время реализации программы
    13. lOCode          : numeric % Halstead's line count
                          количество строк кода (LLOC)
    14. lOComment       : numeric % Halstead's count of lines of comments
                          количество строк комментариев
    15. lOBlank         : numeric % Halstead's count of blank lines
                          количество пустых строк
    16. lOCodeAndComment: numeric % Halstead’s count of lines which contain both code and comments
                          количество строк, содержащих как код, так и комментарии
    17. uniq_Op         : numeric % unique operators
                          уникальные операторы
    18. uniq_Opnd       : numeric % unique operands
                          уникальные операнды
    19. total_Op        : numeric % total operators
                          всего операторов
    20. total_Opnd      : numeric % total operands
                          всего операндов
    21: branchCount     : numeric % branch count of the flow graph
                          количество ветвей потокового графа
    22. defects         : {false,true} % module has/has not one or more reported defects
                          модуль имеет/не имеет одного или нескольких зарегистрированных дефектов
    """
    dataset = arff.loadarff(filename)
    df = pd.DataFrame(dataset[0])

    return df
