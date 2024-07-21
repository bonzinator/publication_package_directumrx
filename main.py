# -*- coding: utf-8 -*-

import sys
import function as f
import commands as c
from configparser import ConfigParser


def load_config(file_path):
    config = ConfigParser()
    config.read(file_path)
    return config


def main():
    config = load_config('config.ini')

    servers = config['servers']
    port = config.get("ssh", "port")
    username = config.get("props", "username")
    password = config.get("props", "password")
    path_for_do = config.get("paths", "path_for_do")
    file_path = config.get("paths", "path_for_package")
    config_yml_path = config.get("paths", "config_yml_path")
    new_host_fqdn = config.get("changes_in_yml", "new_host_fqdn")
    new_protocol = config.get("changes_in_yml", "new_protocol")
    old_host_fqdn = config.get("changes_in_yml", "old_host_fqdn")
    old_protocol = config.get("changes_in_yml", "old_protocol")
    ssl_cert = config.get("paths", "ssl_cert")

    if not f.check_file_exists(file_path=file_path):
        print("File not exist")
        sys.exit(1)

    if not f.update_yaml(file_path=config_yml_path,
                         host_fqdn=new_host_fqdn,
                         protocol=new_protocol,
                         ssl_cert=ssl_cert,
                         dns_name=old_host_fqdn,
                         extra_host=new_host_fqdn):
        print("Convert yaml finished with error")
        sys.exit(1)

    print("Updated config file successfully")

    if not f.command_os(script_path=path_for_do, parameter='haproxy'):
        print("Haproxy Up Failed")
        sys.exit(1)

    print("Running haproxy command successfully")

    if not execute_commands_on_servers(servers, port, username, password, c.all_down, "down"):
        sys.exit(1)

    if not f.command_os(script_path=path_for_do, parameter='deploy', path_dat=file_path):
        print("Deploy exited with error")
        sys.exit(1)

    print("Running deployment command successfully")

    if not f.update_yaml(file_path=config_yml_path,
                         host_fqdn=old_host_fqdn,
                         protocol=old_protocol,
                         ssl_cert=ssl_cert,
                         dns_name=old_host_fqdn,
                         extra_host=new_host_fqdn):
        print("Convert yaml finished with error")
        sys.exit(1)

    if not f.command_os(script_path=path_for_do, parameter='haproxy'):
        print("Haproxy Up Failed")
        sys.exit(1)

    if not execute_commands_on_servers(servers, port, username, password, c.all_up, "up"):
        sys.exit(1)

    print("Status function up is True")
    f.delete_files_by_pattern(directory=file_path)


def execute_commands_on_servers(servers, port, username, password, command, action):
    for server_name in servers:
        if f.execute_command_on_server(hostname=servers[server_name],
                                       port=port,
                                       username=username,
                                       password=password,
                                       command=command):
            print(f"{server_name} is {action}")
        else:
            for server_name_ in servers:
                f.execute_command_on_server(hostname=servers[server_name_],
                                            port=port,
                                            username=username,
                                            password=password,
                                            command=c.all_up)
            print(f"{server_name} {action} exited with error")
            return False
    return True


if __name__ == "__main__":
    main()
