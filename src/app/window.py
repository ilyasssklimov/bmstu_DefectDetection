import pandas as pd
from PyQt5.QtWidgets import QMainWindow, QFileDialog, QMessageBox
from PyQt5.QtGui import QColor, QSyntaxHighlighter, QTextCharFormat, QTextDocument
import re
from src.app.design import Ui_MainWindow
from src.model.model import GBDDModel
from src.processing.metircs import MetricsCppCode


class SyntaxHighlighter(QSyntaxHighlighter):
    def __init__(self, document: QTextDocument):
        super().__init__(document)
        self.__highlight_lines: dict[int, QTextCharFormat] = {}

    def highlight_line(self, line: int, line_format: QTextCharFormat):
        self.__highlight_lines[line] = line_format
        block = super().document().findBlockByLineNumber(line)
        super().rehighlightBlock(block)

    def clear(self):
        self.__highlight_lines = {}
        super().rehighlight()

    def highlightBlock(self, text: str):
        line = super().currentBlock().blockNumber()
        line_format = self.__highlight_lines.get(line)
        if line_format is not None:
            super().setFormat(0, len(text), line_format)


class Window(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle('Система обнаружения дефектов ПО')
        self.__highlighter = SyntaxHighlighter(self.program_txt.document())

        self.__model = GBDDModel(model_file='./app/model.pkl')
        self.__metrics = MetricsCppCode()

        self.load_btn.clicked.connect(self.open_file)
        self.clear_btn.clicked.connect(self.clean_editor)
        self.run_btn.clicked.connect(self.run_searching)

    def open_file(self):
        self.__highlighter.clear()

        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        filename, _ = QFileDialog.getOpenFileName(self, 'Открыть файл', '../data/examples',
                                                  'C++ Files (*.cpp)', options=options)

        if filename:
            try:
                with open(filename, 'r', encoding='utf8') as file:
                    self.program_txt.setPlainText(file.read())
                    QMessageBox.information(self, 'Предупреждение', 'Обратите внимание, что анализироваться будут '
                                                                    'функции, содержащие не более 2000 строк')
            except FileNotFoundError:
                QMessageBox.critical(self, 'Ошибка', 'Такого файла не существует')

    def clean_editor(self):
        self.__highlighter.clear()
        self.program_txt.clear()

    def __split_code_by_functions(self) -> list[tuple[int, int, str]]:
        text_program = self.program_txt.toPlainText()
        func_pattern = r'[\w\*]+\s+\w+\(.*\)\s*{([^{}]|{([^{}]|{([^{}]|{([^{}]|{[^{}]})*})*})*})*}'
        func_matches = re.finditer(func_pattern, text_program)
        functions: list[tuple[int, int, str]] = []

        for function in func_matches:
            start_line = len(MetricsCppCode.split_code_by_lines(text_program[:function.start()])) - 1
            end_line = len(MetricsCppCode.split_code_by_lines(text_program[:function.end()]))
            functions.append((start_line, end_line, function.group()))

        return functions

    def run_searching(self):
        functions = self.__split_code_by_functions()
        self.__highlighter.clear()

        for function in functions:
            self.__metrics.set_function_code(function[2])
            metrics = self.__metrics.count()
            defects_proba = self.__model.predict_proba(pd.DataFrame(metrics, index=[0]))[0][1]

            if 0. <= defects_proba < 0.2:
                color = 'lightBlue'
            elif 0.2 <= defects_proba < 0.4:
                color = 'lightGreen'
            elif 0.4 <= defects_proba < 0.6:
                color = 'yellow'
            elif 0.6 <= defects_proba < 0.8:
                color = 'orange'
            else:
                color = 'red'

            line_format = QTextCharFormat()
            line_format.setBackground(QColor(color))

            for line in range(function[0], function[1]):
                self.__highlighter.highlight_line(line, line_format)
