# models.py
from sqlalchemy import Column, Integer, String, ForeignKey, UniqueConstraint
from sqlalchemy import BigInteger
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import declarative_base
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

    id = Column(BigInteger, primary_key=True)  # Изменяем Integer на BigInteger
    name = Column(String, nullable=False)

    # Связь с таблицей userwords
    userwords = relationship("UserWord", back_populates="user")

    def __repr__(self):
        return f"<User(id={self.id}, name={self.name})>"

# Модель общего слова
class Word(Base):
    __tablename__ = 'words'

    id = Column(Integer, primary_key=True, index=True)
    word = Column(String, nullable=False)  # Слово
    translation = Column(String, nullable=False)  # Перевод слова

    def __repr__(self):
        return f"<Word(id={self.id}, word={self.word}, translation={self.translation})>"

# Модель персональных слов пользователей
class UserWord(Base):
    __tablename__ = 'userwords'

    id = Column(Integer, primary_key=True)
    word = Column(String, nullable=False)
    translation = Column(String, nullable=False)
    user_id = Column(BigInteger, ForeignKey('users.id', ondelete="CASCADE"), nullable=False)

    # Связь с таблицей пользователей
    user = relationship("User", back_populates="userwords")

    __table_args__ = (UniqueConstraint('word', 'user_id', name='unique_user_word'),)

    def __repr__(self):
        return f"<UserWord(id={self.id}, word={self.word}, translation={self.translation}, user_id={self.user_id})>"

# Создание всех таблиц в базе данных (если они ещё не созданы)
def init_db():
    Base.metadata.create_all(bind=engine)


