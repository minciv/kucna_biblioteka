# -*- coding: utf-8 -*-
# @Аутор    : minciv
# @Фајл     : Makefile
# @Верзија  : 0.2.0
# @Програм  : Windsurf
# @Опис     : Makefile за аутоматизацију задатака за Кућну Библиотеку

.PHONY: help install test lint format clean run dev-install

# Подразумевана команда
help:
	@echo "Доступне команде:"
	@echo "  install      - Инсталирај зависности"
	@echo "  dev-install  - Инсталирај развојне зависности"
	@echo "  test         - Покрени тестове"
	@echo "  lint         - Провери код (ruff, mypy)"
	@echo "  format       - Форматирај код (black)"
	@echo "  clean        - Обриши привремене фајлове"
	@echo "  run          - Покрени апликацију"
	@echo "  build        - Направи дистрибуцију"

# Инсталирање зависности
install:
	pip install -r requirements.txt

# Инсталирање развојних зависности
dev-install: install
	pip install -e .[dev]

# Покретање тестова
test:
	pytest tests/ -v --cov=. --cov-report=html

# Провера кода
lint:
	ruff check .
	mypy .

# Форматирање кода
format:
	black .
	ruff check --fix .

# Чишћење
clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf .pytest_cache/

# Покретање апликације
run:
	python kucna_biblioteka.py

# Покретање у debug режиму
debug:
	python kucna_biblioteka.py --debug

# Направи дистрибуцију
build: clean
	python -m build

# Инсталирај локално
install-local: build
	pip install dist/*.whl
