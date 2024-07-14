# -*- coding: utf-8 -*-

from configparser import ConfigParser

# Читаем файл конфигурации, для того чтобы забрать оттуда путь к скрипту
config = ConfigParser()
config.read('config.ini')

# Получаем пути через файл конфигурации
path_for_do = config.get("paths", "path_for_do")
path_for_package = config.get("paths", "path_for_package")

# Основные команды для работы с контейнерами DirectumRX
deploy = f"{path_for_do} dt deploy --package='{path_for_package}'"
all_down = f"{path_for_do} all down"
all_up = f"{path_for_do} all up"
haproxy_up = f"{path_for_do} haproxy up"

