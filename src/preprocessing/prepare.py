import pandas as pd
from scipy.io import arff


def prepare_nasa_dataset(filename: str):
    dataset = arff.loadarff(filename)
    df = pd.DataFrame(dataset[0])

    return df
