# -*- coding: utf-8 -*-
import paramiko
import logging

logging.basicConfig(filename='logfile.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')


def execute_command_on_server(hostname,
                              port,
                              username,
                              password,
                              command):
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

        return output, error
    except paramiko.ssh_exception.AuthenticationException as e:
        logging.error(f"Authentication failed: {str(e)}")
        return None, str(e)
    except paramiko.ssh_exception.SSHException as e:
        logging.error(f"SSH connection failed: {str(e)}")
        return None, str(e)
    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")
        return None, str(e)


def check_file_exists(hostname, port, username, password, file_path):
    """
    Данная функция принимает в себя параметры для подключения к серверам по SSH и путь к файлу разработки .dat.
    Она запускает проверку на существование файла на определенном сервере.
    """

    command = f"test -f {file_path} && echo 'File exists' || echo 'File does not exist'"
    output, error = execute_command_on_server(hostname, port, username, password, command)

    if output:
        logging.info(f"File check output: {output}")
        if 'File exists' in output:
            return True
        else:
            return False
    if error:
        logging.error(f"File check error: {error}")
        return False
