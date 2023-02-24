from preprocessing.dataset import download_nasa
from preprocessing.prepare import prepare_nasa_dataset


def main():
	# download_nasa('jm1', '../data/nasa')
	df = prepare_nasa_dataset('../data/nasa/jm1.arff')
	print(df.head().to_string())


if __name__ == '__main__':
	main()
