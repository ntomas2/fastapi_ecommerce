FROM python:3.12.0

# Устанока переменные окружения
ENV HOME=/home/fast \
    APP_HOME=/home/fast/app \
    PYTHONPATH="$PYTHONPATH:/home/fast" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Создание домашней директории для пользователя(/home/fast) и директории проекта(/home/fast/app)
# Создание группы fast
# Создание отдельного пользователя fast
RUN mkdir -p $APP_HOME \
 && groupadd -r fast\
 && useradd -r -g fast fast

# Установка рабочей директории
WORKDIR $HOME

# Копирование проекта FastAPI в рабочую директорию
COPY app app
ADD .env .
ADD alembic.ini .

# Обновление pip
# Установка зависимостей из списка  requirements.txt
# Изменение владельца для всех директорий и файлов проекта на пользователя fast
RUN pip install --upgrade pip \
 && pip install -r app/requirements.txt \
 && chown -R fast:fast .

# Изменение рабочего пользователя на fast
USER fast