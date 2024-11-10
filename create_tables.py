import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from models import Base, engine

# Загрузить переменные окружения из .env
load_dotenv()

# Получить URL базы данных из .env
DATABASE_URL = os.getenv("DATABASE_URL")

# Подключение к базе данных
engine = create_engine(DATABASE_URL)

# Создание таблиц
if __name__ == "__main__":
    Base.metadata.create_all(engine)
    print("Таблицы успешно созданы")
