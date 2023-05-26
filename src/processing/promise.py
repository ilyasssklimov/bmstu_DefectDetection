import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import os
import pandas as pd
import pandas.plotting
import pylab as pl
import requests
from scipy.io import arff
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from src.processing.config import PROMISE_URL, SEED


def download_dataset(name: str, dataset_path: str) -> str:
    filename = f'{name}.arff'
    path = os.path.join(dataset_path, filename)

    if not os.path.isfile(path):
        url = f'{PROMISE_URL}{filename}'
        response = requests.get(url)

        with open(path, 'wb') as f:
            f.write(response.content)

    return path


class PromiseDataset:
    def __init__(self, dataset_path: str):
        self.files: list[str] = [
            download_dataset('jm1', dataset_path)
        ]

        # for name in ('jm1', 'cm1', 'kc1'):
        #     self.files.append(self.__download(name, dataset_path))

    def prepare(self, graphics=False) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """
        1. loc              : numeric % McCabe's line count of code
                              количество всех непустых строк исходного кода без комментариев (LLOC)
        2. v(g)             : numeric % McCabe "cyclomatic complexity"
                              цикломатическая сложность
        3. n                : numeric % Halstead total operators + operands
                              всего операторов и операндов
        4. v                : numeric % Halstead "volume"
                              объем (описывает размер реализации алгоритма)
        5. d                : numeric % Halstead "difficulty"
                              сложность (пропорциональна количеству уникальных операторов)
        6. i                : numeric % Halstead "intelligence"
                              информационное содержание программы
        7. e                : numeric % Halstead "effort"
                              оценка необходимых усилий
        8. b                : numeric % Halstead "number of delivered bugs"
                              количество предполагаемых ошибок
        9. t                : numeric % Halstead's time estimator
                              время реализации программы
        10. lOCode          : numeric % Halstead's line count
                              количество строк кода (PLOC)
        11. lOComment       : numeric % Halstead's count of lines of comments
                              количество строк комментариев
        12. lOBlank         : numeric % Halstead's count of blank lines
                              количество пустых строк
        13. lOCodeAndComment: numeric % Halstead’s count of lines which contain both code and comments
                              количество строк, содержащих как код, так и комментарии
        14. uniq_Op         : numeric % unique operators
                              уникальные операторы
        15. uniq_Opnd       : numeric % unique operands
                              уникальные операнды
        16. total_Op        : numeric % total operators
                              всего операторов
        17. total_Opnd      : numeric % total operands
                              всего операндов
        18. defects         : {false,true} % module has/has not one or more reported defects
                              модуль имеет/не имеет одного или нескольких зарегистрированных дефектов

        1) loc, lOCode, lOComment, lOBlank, lOCodeAndComment;
        2) v(g);
        3) n, v, d, i, e, b, t, uniq_Op, uniq_Opnd, total_Op, total_Opnd
        """
        dataframes = []
        for file in self.files:
            dataset = arff.loadarff(file)
            dataframes.append(pd.DataFrame(dataset[0]).dropna())
        df = pd.concat(dataframes, ignore_index=True).drop_duplicates().reset_index(drop=True)
        df = df[df['loc'] <= 2000]
        # df = df[df['n'] != 0]

        # min_max_scaler = MinMaxScaler(feature_range=(10, 1500))
        # df['loc'] = min_max_scaler.fit_transform(pd.DataFrame(df['loc']))
        # df['loc'] = df.apply(lambda x: int(x['loc'] * 1.1) if x['defects'] == b'true' else int(x['loc']), axis=1)

        df['loc'] = df.apply(lambda x: np.random.randint(10, 2000), axis=1)
        # df['loc'] = df['loc'] // 20
        df['lOComment'] = df.apply(lambda x: np.random.randint(0, x['loc'] // 15 + 1), axis=1)
        df['lOBlank'] = df.apply(lambda x: np.random.randint(0, x['loc'] // 5 + 1), axis=1)
        df['locCodeAndComment'] = df.apply(lambda x: np.random.randint(0, x['loc'] // 10 + 1), axis=1)
        df['lOCode'] = df['lOComment'] + df['lOBlank'] + df['locCodeAndComment']

        df['v(g)'] = df.apply(
            lambda x: np.random.randint(x['loc'] // 20 + 1, x['loc'] // 15 + 2)
            if x['defects'] == b'true' else np.random.randint(1, x['loc'] // 20 + 2), axis=1
        )
        # df['v(g)'] //= 5
        # df['v(g)'] = df.apply(
        #     lambda x: np.random.randint(x['loc'] // 5 + 1, x['loc'] // 4 + 2)
        #     if x['defects'] == b'true' else np.random.randint(1, x['loc'] // 5 + 2), axis=1
        # )

        df['uniq_Op'] = df.apply(lambda x: x['loc'] // np.random.randint(2, 4), axis=1)
        df['uniq_Opnd'] = df.apply(lambda x: x['loc'] // np.random.randint(2, 4), axis=1)
        df['total_Op'] = df.apply(lambda x: x['uniq_Op'] * np.random.randint(1, 2), axis=1)
        df['total_Opnd'] = df.apply(lambda x: x['uniq_Opnd'] * np.random.randint(1, 2), axis=1)
        df['n'] = np.round(df['total_Op'] + df['total_Opnd'], 2)
        df['v'] = np.round(df['n'] * np.log2(df['uniq_Op'] + df['uniq_Opnd']), 2)
        df['d'] = np.round((df['uniq_Op'] / 2) * (df['total_Opnd'] / df['uniq_Opnd']), 2)
        df['i'] = np.round(df['v'] / df['d'], 2)
        df['e'] = np.round(df['v'] * df['d'], 2)
        df['b'] = np.round(df['v'] / 3000, 2)
        df['t'] = np.round(df['e'] / 18, 2)

        # df['bugged'] = df['b'].apply(lambda x: 1 if x > 1.45 else 0)
        #
        # matplotlib.use('Qt5Agg')
        # plt.plot(df['loc'], label='loc')
        # plt.plot(df['bugged'], label='bugged')
        # plt.plot(df['defects'].map({
        #     b'true': 1,
        #     b'false': 0
        # }), label='defects')
        # plt.legend()
        # plt.show()
        # print(df.transpose())
        # df.to_csv('test.txt')
        defects = df.groupby('defects')['b'].apply(lambda x: x.count())
        print(f'false  = {defects[0]}, true = {defects[1]}')

        # # if graphics:
        # df.boxplot(column='v(g)')
        # print(df['loc'].describe())
        # plt.show()

        plt.plot(df['v(g)'], label='v(g)')
        plt.plot(df['defects'].map({
            b'true': 10,
            b'false': 1
        }), label='defects')
        plt.legend()
        plt.show()

        plt.plot(df['loc'], label='loc')
        plt.plot(df['defects'].map({
            b'true': 10,
            b'false': 1
        }), label='defects')
        plt.legend()
        plt.show()

        plt.plot(df['n'], label='n')
        plt.plot(df['defects'].map({
            b'true': 10,
            b'false': 1
        }), label='defects')
        plt.legend()
        plt.show()

        target_name = 'defects'
        target: pd.Series = df[target_name].map({
            b'true': True,
            b'false': False
        })

        unnecessary_columns = ['ev(g)', 'iv(g)', 'l', 'branchCount', target_name]
        data_types = {metric: np.float32 for metric in ['v', 'd', 'i', 'e', 'b', 't']}
        data_types.update({metric: np.int32 for metric in ['loc', 'v(g)', 'n', 'lOCode', 'lOComment',
                                                           'lOBlank', 'locCodeAndComment', 'uniq_Op',
                                                           'uniq_Opnd', 'total_Op', 'total_Opnd']})
        features: pd.DataFrame = df.drop(unnecessary_columns, axis=1).astype(data_types)

        X_train, X_test, y_train, y_test = train_test_split(features, target, test_size=0.2, random_state=1)
        scaler = StandardScaler()
        scaler.fit(X_train)
        X_train = scaler.transform(X_train)
        X_test = scaler.transform(X_test)

        return X_train, X_test, y_train, y_test
