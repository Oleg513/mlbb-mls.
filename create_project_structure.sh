#!/bin/bash

# Створення основних директорій
mkdir -p project/{src,docs,tests,build,config,assets}

# Створення файлів у директоріях
touch project/src/{main.py,utils.py,config.py} \
      project/docs/{README.md,CONTRIBUTING.md,CHANGELOG.md} \
      project/tests/{test_main.py,test_utils.py} \
      project/build/{build_log.txt} \
      project/config/{settings.yaml,env.example} \
      project/assets/{logo.png,styles.css}

# Повідомлення про завершення
echo "Структура проекту створена успішно!"
