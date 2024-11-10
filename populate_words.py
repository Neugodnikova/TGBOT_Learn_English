from sqlalchemy.orm import Session
from models import Base, Word, engine
from sqlalchemy import select

# Стартовый набор из 20 слов
default_words = [
    {"word": "red", "translation": "красный"},
    {"word": "blue", "translation": "синий"},
    {"word": "green", "translation": "зеленый"},
    {"word": "yellow", "translation": "желтый"},
    {"word": "black", "translation": "черный"},
    {"word": "white", "translation": "белый"},
    {"word": "orange", "translation": "оранжевый"},
    {"word": "purple", "translation": "фиолетовый"},
    {"word": "brown", "translation": "коричневый"},
    {"word": "pink", "translation": "розовый"},
    {"word": "dog", "translation": "собака"},
    {"word": "cat", "translation": "кошка"},
    {"word": "house", "translation": "дом"},
    {"word": "tree", "translation": "дерево"},
    {"word": "car", "translation": "машина"},
    {"word": "book", "translation": "книга"},
    {"word": "water", "translation": "вода"},
    {"word": "fire", "translation": "огонь"},
    {"word": "sun", "translation": "солнце"},
    {"word": "moon", "translation": "луна"},
]

# Создание таблиц
Base.metadata.create_all(bind=engine)

def populate_default_words(session: Session):
    """Заполняет таблицу words стартовым набором слов, если они еще не добавлены"""
    # Проверяем, есть ли уже слова в таблице
    if session.query(Word).count() == 0:
        # Добавляем слова, не привязывая к конкретному пользователю (user_id = None)
        for word in default_words:
            new_word = Word(word=word["word"], translation=word["translation"])
            session.add(new_word)
        session.commit()

# Запуск скрипта
with Session(engine) as session:
    populate_default_words(session)