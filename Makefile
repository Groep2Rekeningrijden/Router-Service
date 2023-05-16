lint:
	-poetry run black --check .
	-poetry run flake8
	-poetry run pylint --disable all --enable spelling --recursive=y ./

lint-fix:
	-poetry run black .
	-poetry run flake8
	-poetry run pylint --disable all --enable spelling --recursive=y ./