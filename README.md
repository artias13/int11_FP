# int11_FP - PT Start 2024.2

Заполните .env

## Чтобы протестировать работу:

### Запуск только с minio

```bash
docker run -p 9000:9000 -e "MINIO_ACCESS_KEY=minio_access_key" -e "MINIO_SECRET_KEY=minio_secret_key" minio/minio server /data
```
или
```bash
docker compose up minio
```
```bash
sudo pip install poetry
```

```bash
sudo poetry install && sudo poetry shell
```

```bash
sudo python main.py --year 2024 --month 11 --day 01
```

### Запуск minio и Airflow DAG

```bash
mkdir logs plugins && echo -e "AIRFLOW_UID=$(id -u)\nAIRFLOW_GID=0" >> .env
```

```bash
docker compose up airflow-init
```

```bash
docker compose up
```

## Результат выполнения main.py:

1. Архив будет загружен в / и разархивирован в папку /tmp
2. Все файлы /tmp будут протестированы против YARA правил в папке /rules
3. Результат тестирования будет сохранен в папку /tmp/yara_results.json
4. Содержимое папки /tmp будет загружено в S3 бакет в формате YYYY-MM-DD-vx-underground
5. Файл архива и папка /tmp будут удалены

## Некоторые 'особенности':

1. Пытался написать статус бар для разархивирования 7z используя tqdm, не особо работает, если кажется что зависло - нужно подождать.
2. Сюда очевидно напрашивается FastAPI и докеркомпоуз, чтобы можно было поднять одной командой два контейнера и отправлять команды к API, пока реализовал через argparse

---

Тестирование произведено на Ubuntu 20.04

## Для установки Docker:

1. Обновление пакетов

```bash
sudo apt-get update
```

2. Установка зависимостей

```bash
sudo apt-get install ca-certificates curl
```

3. Ключ GPG Docker

```bash
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc
```

4. Репозиторий в источники Apt

```bash
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update
```

5. Установка пакетов

```bash
sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```

---
