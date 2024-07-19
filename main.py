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
# Получаем порт для SSH
port = config.get("ssh", "port")
# Получаем реквизиты пользователя через файл конфигурации
username = config.get("props", "username")
password = config.get("props", "password")
# Получаем полный путь к пакету разработки и к скрипту do.sh
path_for_do = config.get("paths", "path_for_do")
file_path = config.get("paths", "path_for_package")
# Получаем данные для подмены в файле config.yml
config_yml_path = config.get("paths", "config_yml_path")
new_host_fqdn = config.get("changes_in_yml", "new_host_fqdn")
new_protocol = config.get("changes_in_yml", "new_protocol")
old_host_fqdn = config.get("changes_in_yml", "old_host_fqdn")
old_protocol = config.get("changes_in_yml", "old_protocol")
ssl_cert = config.get("paths", "ssl_cert")

if __name__ == "__main__":

    file_exists = f.check_file_exists(file_path=file_path)

    if file_exists:

        if f.update_yaml(file_path=config_yml_path,
                         host_fqdn=new_host_fqdn,
                         protocol=new_protocol,
                         ssl_cert=ssl_cert,
                         dns_name=old_host_fqdn,
                         extra_host=new_host_fqdn):
            print("Updated config file successfully")

            if f.command_os(script_path=path_for_do, parameter='haproxy'):
                print("Running haproxy command successfully")
                status_function_down = None
                for server_name in servers:
                    if f.execute_command_on_server(hostname=servers[server_name],
                                                   port=port,
                                                   username=username,
                                                   password=password,
                                                   command=c.all_down):
                        print(f"{server_name} is down")
                        status_function_down = True
                    else:
                        status_function_down = False
                        for server_name_ in servers:
                            f.execute_command_on_server(hostname=servers[server_name_],
                                                        port=port,
                                                        username=username,
                                                        password=password,
                                                        command=c.all_up)
                        print(f"{server_name} down exited with error")
                        break

                if status_function_down:
                    if f.command_os(script_path=path_for_do, parameter='deploy', path_dat=file_path):
                        print("Running deployment command successfully")

                        status_function_up = None
                        for server_name in servers:
                            if f.execute_command_on_server(hostname=servers[server_name],
                                                           port=port,
                                                           username=username,
                                                           password=password,
                                                           command=c.all_up):
                                print(f"{server_name} is up")
                                status_function_up = True
                            else:
                                status_function_up = False
                                for server_name_ in servers:
                                    f.execute_command_on_server(hostname=servers[server_name_],
                                                                port=port,
                                                                username=username,
                                                                password=password,
                                                                command=c.all_up)
                                print(f"{server_name} up exited with error")
                                break
                        if status_function_up:
                            print("Status function up is True")
                            f.delete_files_by_pattern(directory=file_path)
                        else:
                            print("Status function up is False")
                    else:
                        print("deploy exited with error")
                else:
                    print("Status function down is False")
            else:
                print("Haproxy Up Failed")
        else:
            print("Convert yaml finished with error")
    else:
        print("File not exist")
