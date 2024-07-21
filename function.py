# -*- coding: utf-8 -*-
import glob
import os
import subprocess
import ruamel.yaml
from ruamel.yaml import YAML
import paramiko
import logging

logging.basicConfig(filename='logfile.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')


def execute_command_on_server(hostname, port, username, password, command):
    """
    Выполняет команду на удаленном сервере по SSH.
    Логирует все этапы и ошибки.
    """
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        logging.info(f"Connecting to {hostname} as {username}...")
        client.connect(hostname, port, username, password)
        logging.info(f"Connected to {hostname}")
        logging.info(f"Executing command: {command}")
        stdin, stdout, stderr = client.exec_command(command)
        output = stdout.read().decode()
        error = stderr.read().decode()
        if output:
            logging.info(f"Command output:\n{output}")
        if error:
            logging.error(f"Command error:\n{error}")
        client.close()
        logging.info("Connection closed")
        return not bool(error)
    except paramiko.ssh_exception.AuthenticationException as e:
        logging.error(f"Authentication failed: {str(e)}")
    except paramiko.ssh_exception.SSHException as e:
        logging.error(f"SSH connection failed: {str(e)}")
    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")
    return False


def command_os(script_path, parameter, path_dat=None):
    """
    Запускает выполнение скрипта на сервере Linux.
    Логирует все этапы и ошибки.
    """
    if parameter == 'haproxy':
        command = f"bash {script_path} haproxy up"
        logging.info(f"Command HAPROXY UP {script_path}")
    elif parameter == 'deploy':
        command = f"bash {script_path} dt deploy --init --package='{path_dat}'"
        logging.info(f"Command DEPLOY UP {script_path}")
    else:
        logging.error(f"Invalid parameter provided {parameter}")
        return False

    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    output, error = process.communicate()
    exit_code = process.returncode
    if output:
        logging.info(f"Command output:\n{output}")
    if error:
        logging.error(f"Command error:\n{error}")

    if exit_code != 0:
        logging.error(f"Command failed: {command}\n{error}")
        return False
    else:
        logging.info(f"Command executed successfully: {command}\n{output}")
        return True


def check_file_exists(file_path):
    """
    Проверяет существование файла.
    Логирует результат.
    """
    exists = glob.glob(file_path)
    if exists:
        logging.info(f"File {file_path} exists")
    else:
        logging.info(f"File {file_path} does not exist")
    return bool(exists)


def update_yaml(file_path, host_fqdn, protocol, ssl_cert):
    """
    Обновляет параметры в YAML файле.
    Логирует все этапы и ошибки.
    """
    yaml = YAML()
    yaml.preserve_quotes = True

    try:
        with open(file_path, 'r') as file:
            data = yaml.load(file)

        if 'variables' in data:
            data['variables']['host_fqdn'] = host_fqdn
            data['variables']['protocol'] = protocol
            logging.info(f"Updated variables: host_fqdn={host_fqdn}, protocol={protocol}")

        if 'services_config' in data and 'SungeroHaproxy' in data['services_config']:
            haproxy_config = data['services_config']['SungeroHaproxy']

            if 'ssl_cert' in haproxy_config:
                haproxy_config.pop('ssl_cert')
                logging.info(f"Updated ssl_cert: {haproxy_config}. Variable ssl_cert was deleted")
            else:
                haproxy_config['ssl_cert'] = ssl_cert
                haproxy_config['https_port'] = '{{ https_port }}'
                logging.info(f"Updated SungeroHaproxy: ssl_cert={ssl_cert}, https_port='{{ https_port }}'")

        with open(file_path, 'w') as file:
            yaml.dump(data, file)
        logging.info(f"YAML file {file_path} updated successfully")
        return True
    except Exception as e:
        logging.error(f"Error updating YAML file {file_path}: {e}")
        return False


def delete_files_by_pattern(directory):
    """
    Удаляет файлы в указанной директории по шаблону.
    Логирует все этапы и ошибки.
    """
    try:
        files = glob.glob(directory)
        for file_path in files:
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.remove(file_path)
                    logging.info(f"File {file_path} was deleted")
                else:
                    logging.warning(f"{file_path} is a directory and cannot be deleted")
            except Exception as e:
                logging.error(f"Error deleting file {file_path}: {e}")
    except Exception as e:
        logging.error(f"Error accessing directory {directory}: {e}")
