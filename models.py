from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

# Загрузка переменных окружения из .env
load_dotenv()

# Получение URL базы данных из .env
DATABASE_URL = os.getenv("DATABASE_URL")

# Настройка базы данных
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Создание базового класса для моделей
Base = declarative_base()

# Модель пользователя
class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)  # Идентификатор пользователя
    username = Column(String, unique=True, nullable=False)  # Имя пользователя (username)

    # Связь с таблицей слов
    words = relationship("Word", back_populates="user")

    def __repr__(self):
        return f"<User(id={self.id}, username={self.username})>"

# Модель слова
class Word(Base):
    __tablename__ = 'words'

    id = Column(Integer, primary_key=True, index=True)
    word = Column(String, nullable=False)  # Слово
    translation = Column(String, nullable=False)  # Перевод слова

    # Внешний ключ для пользователя, которому принадлежит слово
    user_id = Column(Integer, ForeignKey('users.id', ondelete="CASCADE"), nullable=True)

    # Связь с таблицей User
    user = relationship("User", back_populates="words")

    def __repr__(self):
        return f"<Word(id={self.id}, word={self.word}, translation={self.translation})>"

# Создание всех таблиц в базе данных (если они ещё не созданы)
def init_db():
    Base.metadata.create_all(bind=engine)

