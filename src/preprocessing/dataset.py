import os
import requests


def download_nasa(name: str, dataset_path: str) -> str:
    filename = f'{name}.arff'
    url = f'http://promise.site.uottawa.ca/SERepository/datasets/{filename}'

    response = requests.get(url)
    path = os.path.join(dataset_path, filename)

    with open(path, 'wb') as f:
        f.write(response.content)

    return path
