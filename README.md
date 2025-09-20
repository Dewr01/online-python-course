# Онлайн курс Python 3.12 (FastAPI)

Веб-приложение с краткой теорией и демо-тестами по Python, построенное на FastAPI.
С самого начала вместо FastAPI был задействован Pyodide, поэтому в тексте иногда есть отсылки к нему. 
Ввиду не сильной дружбы Pyodide с json, дабы не использовать костыли, было принято решение перевести проект на FastAPI


## 🚀 Быстрый старт

### 1. Установка зависимостей
```bash
pip install -r requirements.txt
```

### 2. Запуск сервера
```bash
python main.py
```

### 3. Открыть в браузере
```bash
http://localhost:8000
```

## 📚 Структура проекта

```
online-python-course-fastapi/
├── main.py                 # Основной файл FastAPI приложения
├── requirements.txt        # Зависимости Python
├── templates/
│   └── index.html         # HTML шаблон главной страницы
├── static/
│   └── style.css          # CSS стили
├── data/
│   └── modules/           # JSON файлы модулей курса
│       ├── manifest.json
│       ├── module-01/
│       ├── module-02/
│       └── ...
└── README.md
```

## 🎯 Функциональность

### API Endpoints
- `GET /` - Главная страница курса
- `GET /api/modules` - Список модулей
- `GET /api/lessons` - Список всех уроков
- `GET /api/lessons/{lesson_id}` - Конкретный урок
- `GET /api/lessons/by-index/{lesson_index}` - Урок по индексу
- `GET /api/lesson/{lesson_id}/theory` - Теория урока
- `GET /api/lesson/{lesson_id}/tasks` - Задания урока
- `POST /api/check-answer` - Проверка ответа
- `GET /api/health` - Проверка здоровья API

### Фронтенд
- **Навигация по модулям** - раскрывающиеся списки
- **Интерактивные задания** - кнопка "Отправить" для каждого
- **Система попыток** - 3 попытки на задание
- **Визуальная обратная связь** - цветовая индикация
- **Адаптивный дизайн** - работает на всех устройствах

## 🛠 Технологии

### Backend
- **FastAPI** - веб-фреймворк
- **Pydantic** - валидация данных
- **Uvicorn** - ASGI сервер
- **Jinja2** - шаблонизатор

### Frontend
- **Vanilla JavaScript** - без внешних зависимостей
- **CSS Grid/Flexbox** - современная верстка
- **Gradient дизайн** - красивый интерфейс
- **Responsive** - адаптивная верстка

## 📱 Особенности

### Дизайн
- **Плавные анимации и переходы**
- **Интуитивная навигация**
- **Цветовая индикация результатов**

### Функциональность
- **Мгновенная загрузка** - все данные в памяти
- **Надежная работа** - нет проблем с загрузкой файлов
- **Простое развертывание** - один файл для запуска
- **Автоматическая документация** - Swagger UI на `/docs`

## 🔧 Разработка

### Добавление новых модулей
1. Создайте папку `data/modules/module-XX/`
2. Добавьте JSON файлы тем
3. Обновите `data/modules/manifest.json`
4. Перезапустите сервер

### Структура темы (JSON)
```json
{
  "title": "Название темы",
  "theory": "Теоретический материал",
  "tasks": [
    {
      "id": "уникальный_id",
      "question": "Вопрос",
      "answer": "Правильный ответ",
      "hint": "Подсказка"
    }
  ]
}
```

## 📊 API Документация

После запуска сервера доступна автоматическая документация:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🚀 Развертывание

### Локальная разработка
```bash
python main.py
```

### Продакшн (с Gunicorn)
```bash
pip install gunicorn
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker
```

### Docker
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["python", "main.py"]
```

## 🎨 Кастомизация

### Добавление новых API
Добавьте новые endpoints в `main.py`.

### Изменение логики курса
Модифицируйте функции в `main.py` для изменения поведения.

## 📄 Лицензия

MIT
