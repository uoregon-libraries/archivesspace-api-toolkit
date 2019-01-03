
compile:
	rm -rf ./build/*
	python setup.py build

setup:
	pip install -r requirements.txt

freeze:
	pip freeze > requirements.txt
