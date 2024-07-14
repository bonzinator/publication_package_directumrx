# -*- coding: utf-8 -*-

import function as f
import commands as c
from configparser import ConfigParser

# Читаем файл конфигурации, для того чтобы забрать оттуда реквизиты пользователя
# и путь к скрипту
config = ConfigParser()
config.read('config.ini')
# Получаем секцию с серверами
servers = config['servers']
main_server = config['main_server']
# Получаем порт для SSH
port = config.get("ssh", "port")
# Получаем реквизиты пользователя через файл конфигурации
username = config.get("props", "username")
password = config.get("props", "password")
# Получаем полный путь к пакету разработки
file_path = config.get("paths", "path_for_package")

if __name__ == "__main__":

    file_exists = f.check_file_exists(hostname=main_server["app1"],
                                      port=port,
                                      username=username,
                                      password=password,
                                      file_path=file_path)

    if file_exists:
        for server_name in servers:
            output, error = f.execute_command_on_server(hostname=servers[server_name],
                                                        port=port,
                                                        username=username,
                                                        password=password,
                                                        command=c.all_down)
            if output:
                print("Output:\n", output)
            if error:
                print("Error:\n", error)
    else:
        print("File not exist")
