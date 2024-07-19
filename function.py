# -*- coding: utf-8 -*-
import glob
import os
import ruamel.yaml
from ruamel.yaml import YAML
import paramiko
import logging

logging.basicConfig(filename='logfile.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')


def execute_command_on_server(hostname, port, username, password, command):
    """
    Данная функция принимает в себя параметры для подключения к серверам по SSH и выполняет
    определенную команду, которую укажет пользователь. Вся информация, пишется в лог файл logfile.log
    """

    try:
        # Создание SSH клиента
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        # Логирование этапа подключения
        logging.info(f"Connecting to {hostname} as {username}...")

        # Подключение к серверу
        client.connect(hostname, port, username, password)

        # Логирование успешного подключения
        logging.info(f"Connected to {hostname}")

        # Выполнение команды
        logging.info(f"Executing command: {command}")
        stdin, stdout, stderr = client.exec_command(command)

        # Чтение вывода команды
        output = stdout.read().decode()
        error = stderr.read().decode()

        # Логирование вывода команды
        if output:
            logging.info(f"Command output:\n{output}")
        if error:
            logging.error(f"Command error:\n{error}")

        # Закрытие соединения
        client.close()
        logging.info("Connection closed")

        if output:
            return True
        else:
            return False

    except paramiko.ssh_exception.AuthenticationException as e:
        logging.error(f"Authentication failed: {str(e)}")
        return None, str(e)
    except paramiko.ssh_exception.SSHException as e:
        logging.error(f"SSH connection failed: {str(e)}")
        return None, str(e)
    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")
        return None, str(e)


def command_os(script_path, parameter, path_dat=None):
    """
    Запускает выполнение скрипта на сервере Linux с помощью os.system.
    :param path_dat:
    :param parameter:
    :param script_path: Путь к скрипту, который нужно выполнить.
    """
    if parameter == 'haproxy':
        logging.info(f"Command HAPROXY UP {script_path}")
        command = f"bash {script_path} haproxy up"
        exit_code = os.system(command)
        if exit_code != 0:
            logging.error(f"Command failed: {command}")
            return False
        else:
            logging.info(f"Command executed successfully: {command}")
            return True
    elif parameter == 'deploy':
        logging.info(f"Command DEPLOY START {script_path}")
        command = f"bash {script_path} dt deploy --init --package='{path_dat}'"
        exit_code = os.system(command)
        if exit_code != 0:
            logging.error(f"Command failed: {command}")
            return False
        else:
            logging.info(f"Command executed successfully: {command}")
            return True
    else:
        return False


def check_file_exists(file_path):
    """
    Данная функция принимает в себя путь к файлу разработки .dat.
    Она запускает проверку на существование файла на определенном сервере.
    """
    if glob.glob(file_path):
        logging.info(f"File {file_path} exists")
    else:
        logging.info(f"File {file_path} does not exist")
    return glob.glob(file_path)


def update_yaml(file_path, host_fqdn, protocol, ssl_cert, dns_name, extra_host):
    """
    Функция изменяет параметры файла конфигурации для корректного проведения публикации.
    Она подменяет параметры host_fqdn и protocol в секции variables для работы haproxy по http.
    Также она удаляет и добавляет параметры в extra_hosts и ssl_cert соответственно.
    """
    yaml = YAML()
    yaml.preserve_quotes = True

    with open(file_path, 'r') as file:
        data = yaml.load(file)

    # Обновление данных в параметрах host_fqdn и protocol
    if 'variables' in data:
        data['variables']['host_fqdn'] = host_fqdn
        logging.info(f"Updating {file_path}, new host fqdn: {host_fqdn}")
        data['variables']['protocol'] = protocol
        logging.info(f"Updating {file_path}, new protocol: {protocol}")

    # Добавление и удаление строчки ssl_cert в блоке HAProxy
    if 'services_config' in data and 'SungeroHaproxy' in data['services_config']:
        haproxy_config = data['services_config']['SungeroHaproxy']
        if 'ssl_cert' in haproxy_config:
            haproxy_config.pop('ssl_cert')
            logging.info(f"Updating {file_path}, variable ssl_cert was deleted")
        else:
            haproxy_config['ssl_cert'] = ssl_cert
            logging.info(f"Updating {file_path}, ssl_cert = {ssl_cert}")
        if 'https_port' not in haproxy_config:
            haproxy_config['https_port'] = '{{ https_port }}'
            logging.info(f"Updating {file_path}, https_port = https_port ")

    # Добавление и удаление параметра в блоке extra_hosts
    if 'extra_hosts' in data and dns_name in data['extra_hosts']:
        data['extra_hosts'].pop(dns_name)
        logging.info(f"Updating {file_path}, extra_hosts was deleted")
    else:
        data['extra_hosts'][dns_name] = extra_host
        logging.info(f"Updating {file_path}, extra_hosts was added to {dns_name}")

    with open(file_path, 'w') as file:
        yaml.dump(data, file)


def delete_files_by_pattern(directory):
    """
    Удаляет все файлы в указанной директории, соответствующие шаблону.

    :param directory: Путь к директории, в которой нужно удалить файлы.
    """
    try:
        # Поиск всех файлов, соответствующих шаблону
        files = glob.glob(directory)

        for file_path in files:
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.remove(file_path)
                    logging.info(f"File {file_path} was deleted")
                else:
                    logging.warning(f"{file_path} is a directory. We can't delete it")
            except Exception as e:
                logging.error(f"File deletion error {file_path}: {e}")
    except Exception as e:
        logging.error(f"Error accessing directory {directory}: {e}")