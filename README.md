### Привет! Это мой скрипт для автоматической публикации пакетов разработки ИС DirectumRX

### Важно
1. Перед тем как запускать скрипт нужно добавить пользователя под которым производится 
подключение к серверам добавить в группу `Docker`
```bash
sudo usermod -aG docker $USER
```
2. Выдать полные права на файлы домашней директории `DirectumRX`
```bash
chmod -R 777 <path to Directum Launcher>
```
3. Файл разработки должен всегда называться одинаково. Например `solution.dat`

Главный файл, в который вносятся изменения - `config.ini`

Рассмотрим его повнимательней:

В данной секции указываются логин и пароль пользователя на сервере Linux.
К нему мы будем удаленно подключаться по `ssh`
```ini
[props]
username = user
password = 1234
```

В данном блоке мы указываем пути к следующим фалам:
```ini
[paths]
path_for_do = /srv/drx/do.sh
path_for_package = /srv/dev/*.dat
config_yml_path = /srv/drx/etc/config.yml
ssl_cert = /srv/drx/etc/server.pem
```

`path_for_do` - полный путь к главному исполняемому скрипту do.sh

`path_for_package` - полный путь к файлу с разработкой. Обязательно должен заканчиваться на `*.dat`

`config_yml_path` - полный путь к основному файлу конфигурации `DirectumRX`

`ssl_cert` - полный путь к сертификату ssl в расширении `pem`

В данной секции указываем порт для подключения по `ssh`
```ini
[ssh]
port = 22
```

В данной секции указываются данные, которые будут подменяться в конфигурационном файле, 
для публикации по протоколу `http`
```ini
[changes_in_yml]
new_host_fqdn = 10.0.2.103
new_protocol = http
old_host_fqdn = ased.gov35.ru
old_protocol = https
```

`new_host_fqdn` - ip сервера, на котором будет выполняться публикация

`new_protocol` - протокол по которому будет выполняться публикация

`old_host_fqdn`- текущее доменное имя сервера

`old_protocol` - текущий протокол сервера DirectumRX

В данной секции мы перечисляем перечень нод, на который у нас установлена 
система `DirectumRX`
```ini
[servers]
app2 = 10.0.2.104
app3 = 10.0.2.105
app4 = 10.0.2.106
```
