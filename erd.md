# Entity-Relationship Diagram (ERD)
Диаграмма взаимосвязей сущностей (ERD) для базы данных Telegram-бота.

![ERD Diagram](ERD.PNG)

```plantuml
@startuml
entity "users" {
    * id : Integer <<PK>>
    --
    name : String
}

entity "words" {
    * id : Integer <<PK>>
    --
    word : String
    translation : String
}

entity "userwords" {
    * id : Integer <<PK>>
    --
    word : String
    translation : String
    user_id : Integer <<FK>>
}

users ||--o{ userwords : "has"
@enduml

Объяснение:
users: Таблица для хранения данных пользователей.

id — уникальный идентификатор пользователя.
name — имя пользователя.
words: Таблица для общих слов.

id — уникальный идентификатор слова.
word — слово на английском языке.
translation — перевод слова.
userwords: Таблица для хранения персональных слов пользователей.

id — уникальный идентификатор записи.
word — слово на английском языке.
translation — перевод слова.
user_id — внешний ключ, связывающий слово с конкретным пользователем.
Связи:

users связана с userwords (один пользователь имеет множество слов).
words автономна и содержит общий словарь для всех пользователей.