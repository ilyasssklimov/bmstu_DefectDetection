from preprocessing.dataset import download_nasa


def main():
	download_nasa('jm1', './data/nasa')


if __name__ == '__main__':
	main()
