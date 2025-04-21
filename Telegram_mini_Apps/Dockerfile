FROM python:3.12.7

# Задать переменные среды
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV LC_ALL=ru_RU.UTF-8
ENV LANG=ru_RU.UTF-8
ENV LANGUAGE=ru



# Задать рабочий каталог
WORKDIR /code

RUN apt-get update && \
    apt-get install -y locales-all sqlite3 && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip
COPY requirements.txt /code/
RUN pip install --no-cache-dir -r requirements.txt

COPY . /code/

CMD ["gunicorn", "--bind", "your_domen:8000", "app.wsgi:application"]

