import os
import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
from sqlalchemy.orm import Session
from sqlalchemy import func
from models import User, Word, engine
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
        # Проверяем, есть ли пользователь в базе, если нет — добавляем его
        user = session.query(User).filter_by(id=user_id).first()  # Используем 'id', а не 'user_id'
        if not user:
            user = User(id=user_id, name=user_name)  # Создаем пользователя правильно
            session.add(user)
            session.commit()

    # Ответ пользователю с описанием доступных команд и функционала
    menu_text = (
        f"Привет, {user_name}! Добро пожаловать в бота для изучения слов!\n\n"
        "Вот что ты можешь сделать:\n\n"
        "/quiz - Начать тест на перевод слов\n"
        "/add слово перевод - Добавить новое слово с переводом\n"
        "/delete слово - Удалить слово\n"
        "/help - Показать это меню снова"
    )

    await update.message.reply_text(menu_text)

# Команда для начала теста
async def quiz(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    with Session(engine) as session:
        # Получаем случайное слово
        word = session.query(Word).order_by(func.random()).first()
        if not word:
            await update.message.reply_text("Слов для изучения пока нет.")
            return

        # Сохраняем id слова в контексте пользователя
        context.user_data['current_word'] = word.id

        # Генерируем случайные переводы, исключая дублирование правильного ответа
        words = session.query(Word).order_by(func.random()).limit(3).all()  # Получаем 3 случайных слова
        words_texts = [w.translation for w in words]
        
        # Добавляем правильный перевод, но проверяем, что он не дублируется
        if word.translation not in words_texts:
            words_texts.append(word.translation)
        else:
            # Если вдруг все 3 случайных слова уже имеют тот же перевод, добавим еще одно случайное слово
            words_texts.append(session.query(Word).order_by(func.random()).first().translation)

        random.shuffle(words_texts)  # Перемешиваем варианты

        # Создаем кнопки с переводами
        keyboard = [
            [InlineKeyboardButton(answer, callback_data=f"{word.id}_{answer}") for answer in words_texts]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(f"Как переводится '{word.word}'?", reply_markup=reply_markup)

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
            word = Word(word=word_text, translation=translation, user_id=user_id)
            session.add(word)
            session.commit()
            
        await update.message.reply_text(f"Слово '{word_text}' добавлено с переводом '{translation}'.")
    else:
        await update.message.reply_text("Пожалуйста, используйте формат: /add слово перевод")

# Функция для удаления слова
async def delete_word(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.args:
        word_text = context.args[0]
        user_id = update.message.from_user.id
        
        with Session(engine) as session:
            word = session.query(Word).filter_by(word=word_text, user_id=user_id).first()
            if word:
                session.delete(word)
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
