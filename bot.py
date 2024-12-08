import os
import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
from sqlalchemy.orm import Session
from models import User, Word, UserWord, engine
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

# Создаем бота
application = Application.builder().token(TELEGRAM_TOKEN).build()

# Команда /start для приветствия пользователя
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    user_name = update.message.from_user.first_name

    # Открываем сессию с базой данных
    with Session(engine) as session:
        # Проверяем существование пользователя по ID
        user = session.query(User).filter_by(id=user_id).first()
        if not user:
            user = User(id=user_id, name=user_name)
            session.add(user)
            session.commit()

            # Добавляем стартовые слова в таблицу userwords для нового пользователя
            add_default_words_for_user(session, user.id)

    # Приветственное сообщение
    menu_text = (
        f"Привет, {user_name}! Добро пожаловать в бота для изучения слов!\n\n"
        "Вот что ты можешь сделать:\n\n"
        "/quiz - Начать тест на перевод слов\n"
        "/add слово перевод - Добавить новое слово с переводом\n"
        "/delete слово - Удалить слово\n"
        "/help - Показать это меню снова"
    )
    await update.message.reply_text(menu_text)

# Функция для добавления стартовых слов в таблицу userwords для нового пользователя
def add_default_words_for_user(session: Session, user_id: int):
    """Добавляет слова из default_words в таблицу userwords для нового пользователя"""
    # Получаем все слова из таблицы Word
    default_words = session.query(Word).all()

    for word in default_words:
        # Добавляем каждое слово для пользователя в таблицу userwords
        user_word = UserWord(word=word.word, translation=word.translation, user_id=user_id)
        session.add(user_word)
    session.commit()

# Команда для начала теста
async def quiz(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    with Session(engine) as session:
        # Получаем случайное слово из общей таблицы или пользовательских слов
        userwords = session.query(UserWord).filter_by(user_id=user_id).all()
        all_words = session.query(Word).all()
        combined_words = userwords + all_words

        if not combined_words:
            await update.message.reply_text("Слов для изучения пока нет.")
            return

        random_word = random.choice(combined_words)
        context.user_data['current_word'] = random_word.id

        # Генерируем варианты ответов
        options = [w.translation for w in combined_words if w.translation != random_word.translation][:3]
        options.append(random_word.translation)
        random.shuffle(options)

        keyboard = [
            [InlineKeyboardButton(option, callback_data=f"{random_word.id}_{option}") for option in options]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(f"Как переводится '{random_word.word}'?", reply_markup=reply_markup)

# Обработчик ответов
async def answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    # Разбираем данные ответа
    selected_word_id, selected_answer = query.data.split("_")
    selected_word_id = int(selected_word_id)

    with Session(engine) as session:
        word = session.get(Word, selected_word_id)
        if word and word.translation == selected_answer:
            await query.edit_message_text("Верно! Для нового теста используйте команду /quiz.")
        else:
            await query.edit_message_text("Неправильно, попробуйте снова! Для нового теста используйте команду /quiz.")

# Функция для добавления нового слова
async def add_word(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.args and len(context.args) == 2:
        word_text, translation = context.args
        user_id = update.message.from_user.id
        
        with Session(engine) as session:
            # Проверяем, существует ли уже это слово у пользователя
            existing_word = session.query(UserWord).filter_by(word=word_text, user_id=user_id).first()
            if existing_word:
                await update.message.reply_text(f"Слово '{word_text}' уже добавлено.")
                return

            # Добавляем персональное слово в таблицу userwords
            userword = UserWord(word=word_text, translation=translation, user_id=user_id)
            session.add(userword)
            session.commit()

        await update.message.reply_text(f"Слово '{word_text}' добавлено с переводом '{translation}'.")
    else:
        await update.message.reply_text(     "Пожалуйста, используйте формат: /add слово перевод")


# Функция для удаления слова
async def delete_word(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.args:
        word_text = context.args[0]
        user_id = update.message.from_user.id

        with Session(engine) as session:
            # Ищем слово только в пользовательских словах
            userword = session.query(UserWord).filter_by(word=word_text, user_id=user_id).first()
            if userword:
                session.delete(userword)
                session.commit()
                await update.message.reply_text(f"Слово '{word_text}' удалено.")
            else:
                await update.message.reply_text("Такое слово не найдено.")
    else:
        await update.message.reply_text("Пожалуйста, укажите слово для удаления. Формат: /delete слово")


# Команда /help для вывода меню
async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.message.from_user.first_name
    menu_text = (
        f"Привет, {user_name}! Вот что ты можешь сделать:\n\n"
        "/quiz - Начать тест на перевод слов\n"
        "/add слово перевод - Добавить новое слово с переводом\n"
        "/delete слово - Удалить слово\n"
        "/help - Показать это меню снова"
    )
    await update.message.reply_text(menu_text)

# Регистрируем обработчики команд и сообщений
application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("quiz", quiz))
application.add_handler(CallbackQueryHandler(answer))
application.add_handler(CommandHandler("add", add_word))
application.add_handler(CommandHandler("delete", delete_word))
application.add_handler(CommandHandler("help", help))

# Запуск бота
if __name__ == "__main__":
    application.run_polling()
