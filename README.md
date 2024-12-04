# Проект синхронного парсинга документации из python.org с использованием библиотеки Beautiful Soup 4

#### Вывод справочной информации об аргументах:
```angular2html
python src/main.py -h
```

### Получить информацию о ссылках на возможности в новых версиях:

#### c выводом в файл:
```angular2html
python src/main.py whats-new --output file
```
#### вывод в консоль таблицей:
```angular2html
python src/main.py whats-new --output pretty
```
### Получить информацию о количестве PEP:
#### c выводом в файл:
```angular2html
python src/main.py pep --output file
```
#### вывод в консоль таблицей:
```angular2html
python src/main.py pep --output pretty
```
### Загрузка документации последней версии:
#### c выводом в файл:
```angular2html
python src/main.py download --output file
```
### Получить информацию обо всех доступных версиях python:
#### вывод в консоль таблицей:
```angular2html
python src/main.py latest-versions --output pretty
```
#### c выводом в файл:
```angular2html
python src/main.py latest_versions --output file
```
