from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import json
import re
import os
from pathlib import Path

app = FastAPI(title="Онлайн курс Python 3.12", version="1.0.0")

# Монтируем статические файлы
app.mount("/static", StaticFiles(directory="static"), name="static")

# Настройка шаблонов
templates = Jinja2Templates(directory="templates")


# Модели данных
class Task(BaseModel):
    id: str
    question: str
    answer: str
    hint: str


class Lesson(BaseModel):
    title: str
    theory: str
    tasks: List[Task]


class Module(BaseModel):
    id: str
    title: str
    topics: List[Dict[str, str]]


class LessonResponse(BaseModel):
    id: str
    title: str
    theory: str
    tasks: List[Task]


class CheckAnswerRequest(BaseModel):
    task_id: str
    answer: str


class CheckAnswerResponse(BaseModel):
    correct: bool
    expected: str
    hint: str
    attempts: int


# Функция для преобразования Markdown в HTML
def markdown_to_html(text: str) -> str:
    """Преобразует Markdown-подобное форматирование в HTML"""
    if not text:
        return ""

    # Обрабатываем код-блоки
    def code_block_replacer(match):
        language = match.group(1) or ''
        code = match.group(2)
        # Экранируем HTML-символы в коде
        code = code.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        return f'<div class="code-block"><span class="language">{language}</span><pre><code>{code}</code></pre></div>'

    # Регулярные выражения для преобразования
    patterns = [
        (r'```(\w*)\n(.*?)```', code_block_replacer),  # код-блоки
        (r'\*\*(.*?)\*\*', r'<strong>\1</strong>'),  # жирный текст
        (r'\*(.*?)\*', r'<em>\1</em>'),  # курсив
        (r'`(.*?)`', r'<code>\1</code>'),  # inline код
        (r'\n', '<br>')  # переносы строк
    ]

    for pattern, replacement in patterns:
        if callable(replacement):
            text = re.sub(pattern, replacement, text, flags=re.DOTALL)
        else:
            text = re.sub(pattern, replacement, text)

    return text


# Обновить функцию загрузки данных
def load_course_data():
    """Загружает данные курса из JSON файлов"""
    course_data = {
        "modules": [],
        "lessons": []
    }

    # Загружаем манифест модулей
    manifest_path = Path("data/modules/manifest.json")
    if manifest_path.exists():
        with open(manifest_path, 'r', encoding='utf-8') as f:
            manifest = json.load(f)
            course_data["modules"] = manifest.get("modules", [])

    # Загружаем уроки из модулей
    for module in course_data["modules"]:
        for topic in module.get("topics", []):
            lesson_path = Path(topic["path"])
            if lesson_path.exists():
                with open(lesson_path, 'r', encoding='utf-8') as f:
                    lesson_data = json.load(f)
                    # Преобразуем теорию в HTML
                    theory_html = markdown_to_html(lesson_data.get("theory", ""))
                    lesson = {
                        "id": topic["id"],
                        "title": f"{module['title']} - {topic['title']}",
                        "module_id": module["id"],
                        "topic_id": topic["id"],
                        "theory": theory_html,  # Сохраняем как HTML
                        "tasks": lesson_data.get("tasks", [])
                    }
                    course_data["lessons"].append(lesson)

    return course_data


# Глобальное хранилище данных курса
COURSE_DATA = load_course_data()

# Хранилище попыток пользователей
user_attempts: Dict[str, int] = {}


@app.get("/", response_class=HTMLResponse)
async def read_root():
    """Главная страница курса"""
    return templates.TemplateResponse("index.html", {
        "request": {},
        "modules": COURSE_DATA["modules"],
        "lessons": COURSE_DATA["lessons"]
    })


@app.get("/api/modules")
async def get_modules():
    """Получить список модулей"""
    return {"modules": COURSE_DATA["modules"]}


@app.get("/api/lessons")
async def get_lessons():
    """Получить список всех уроков"""
    return {"lessons": COURSE_DATA["lessons"]}


@app.get("/api/lessons/{lesson_id}")
async def get_lesson(lesson_id: str):
    """Получить конкретный урок"""
    for lesson in COURSE_DATA["lessons"]:
        if lesson["id"] == lesson_id:
            return lesson

    raise HTTPException(status_code=404, detail="Урок не найден")


@app.get("/api/lessons/by-index/{lesson_index}")
async def get_lesson_by_index(lesson_index: int):
    """Получить урок по индексу"""
    if lesson_index < 0 or lesson_index >= len(COURSE_DATA["lessons"]):
        raise HTTPException(status_code=404, detail="Некорректный индекс урока")

    return COURSE_DATA["lessons"][lesson_index]


@app.post("/api/check-answer")
async def check_answer(request: CheckAnswerRequest):
    """Проверить ответ на задание"""
    # Находим задание
    task = None
    lesson = None

    for l in COURSE_DATA["lessons"]:
        for t in l["tasks"]:
            if t["id"] == request.task_id:
                task = t
                lesson = l
                break
        if task:
            break

    if not task:
        raise HTTPException(status_code=404, detail="Задание не найдено")

    # Увеличиваем счетчик попыток
    user_attempts[request.task_id] = user_attempts.get(request.task_id, 0) + 1

    # Проверяем ответ
    correct = request.answer.strip().lower() == task["answer"].strip().lower()

    return CheckAnswerResponse(
        correct=correct,
        expected=task["answer"],
        hint=task["hint"],
        attempts=user_attempts[request.task_id]
    )


@app.get("/api/lesson/{lesson_id}/tasks")
async def get_lesson_tasks(lesson_id: str):
    """Получить задания урока"""
    for lesson in COURSE_DATA["lessons"]:
        if lesson["id"] == lesson_id:
            return {"tasks": lesson["tasks"]}

    raise HTTPException(status_code=404, detail="Урок не найден")


@app.get("/api/lesson/{lesson_id}/theory")
async def get_lesson_theory(lesson_id: str):
    """Получить теорию урока"""
    for lesson in COURSE_DATA["lessons"]:
        if lesson["id"] == lesson_id:
            return {"theory": lesson["theory"]}

    raise HTTPException(status_code=404, detail="Урок не найден")


@app.get("/api/health")
async def health_check():
    """Проверка здоровья API"""
    return {
        "status": "ok",
        "modules_count": len(COURSE_DATA["modules"]),
        "lessons_count": len(COURSE_DATA["lessons"])
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
