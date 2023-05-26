import sys
sys.path.append('../..')

import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import pandas as pd
import pickle
from sklearn.metrics import f1_score, accuracy_score, precision_score, recall_score
from src.model.config import SEED
from sklearn.model_selection import GridSearchCV, StratifiedKFold
from src.processing.promise import PromiseDataset
from xgboost import XGBClassifier


# Gradient Boosting Defect Detection Model
class GBDDModel:
    def __init__(self, learning_rate: float = 0.01, n_estimators: int = 1000, max_depth: int = 7,
                 model_file: str = r'..\app\model.pkl'):
        self.__model: XGBClassifier = XGBClassifier(
            learning_rate=learning_rate,
            n_estimators=n_estimators,
            max_depth=max_depth,
            objective='binary:logistic',
            eval_metric='logloss',
        )

        self.__model_file = model_file

    def grid_search(self, X_train: pd.DataFrame, y_train: pd.DataFrame):
        skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=SEED)
        params = {
            'learning_rate': [0.01, 0.02, 0.03, 0.04, 0.05],
            'max_depth': [3, 4, 5, 6, 7],
            'n_estimators': [800, 900, 1000]
        }
        search = GridSearchCV(self.__model, param_grid=params, scoring='roc_auc', n_jobs=4,
                              cv=skf.split(X_train, y_train), verbose=3)
        search.fit(X_train, y_train)
        print(search.best_score_)
        print(search.best_estimator_)
        print(search.best_params_)

    def debug_fit(self, X_train: pd.DataFrame, y_train: pd.DataFrame, X_test: pd.DataFrame, y_test: pd.DataFrame):
        defect_classes = y_train.value_counts()
        self.__model.scale_pos_weight = defect_classes[0] / defect_classes[1]
        self.__model.fit(X_train, y_train, eval_set=[(X_train, y_train), (X_test, y_test)])
        self.__model.predict(X_test)

        y_prob = self.__model.predict_proba(X_test)
        for i in [0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5, 0.55, 0.6]:
            y_pred = np.where(y_prob[:, 1] > i, 1, 0)
            print(i, get_statistics(y_test, y_pred))

        results = self.__model.evals_result()

        matplotlib.use('Qt5Agg')
        plt.plot(results['validation_0']['logloss'], label='train')
        plt.plot(results['validation_1']['logloss'], label='test')
        plt.legend()
        # plt.show()

    def fit(self, X_train: pd.DataFrame, y_train: pd.DataFrame):
        self.__model.fit(X_train, y_train)
        with open(self.__model_file, 'wb') as f:
            pickle.dump(self.__model, f)

    def __read_model(self):
        try:
            with open(self.__model_file, 'rb') as f:
                return pickle.load(f)
        except FileNotFoundError:
            print('Do fit before predict, there is no model file')

    def predict(self, X_test: pd.DataFrame) -> list[float]:
        model = self.__read_model()
        # pd.DataFrame(model.predict_proba(X_test)).to_csv('test2.txt')
        return model.predict(X_test)

    def predict_proba(self, X_test: pd.DataFrame) -> list[list[float]]:
        model = self.__read_model()
        return model.predict_proba(X_test)


def get_statistics(y_test: pd.DataFrame, y_pred: np.array):
    return {
        'accuracy': round(accuracy_score(y_test, y_pred), 3),
        'precision': round(precision_score(y_test, y_pred), 3),
        'recall': round(recall_score(y_test, y_pred), 3),
        'F-measure': round(f1_score(y_test, y_pred), 3)
    }


def main():
    dataset = PromiseDataset(r'..\..\data\promise')
    X_train, X_test, y_train, y_test = dataset.prepare()

    model = GBDDModel()
    # model.grid_search(X_train, y_train)
    model.debug_fit(X_train, y_train, X_test, y_test)
    model.fit(X_train, y_train)
    # print(get_statistics(y_test, model.predict(X_test)))


if __name__ == '__main__':
    main()
