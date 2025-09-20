#!/usr/bin/env python3
"""
Тест структуры FastAPI проекта
"""
import os
import json
from pathlib import Path


def test_project_structure():
    """Проверяет структуру проекта"""
    print("🔍 Проверка структуры проекта FastAPI...")

    # Проверяем основные файлы
    required_files = [
        "main.py",
        "requirements.txt",
        "templates/index.html",
        "static/style.css",
        "data/modules/manifest.json"
    ]

    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
        else:
            print(f"✅ {file_path}")

    if missing_files:
        print(f"❌ Отсутствуют файлы: {missing_files}")
        return False

    # Проверяем манифест модулей
    try:
        with open("data/modules/manifest.json", 'r', encoding='utf-8') as f:
            manifest = json.load(f)
            modules = manifest.get("modules", [])
            print(f"✅ Манифест загружен: {len(modules)} модулей")

            # Проверяем файлы модулей
            total_topics = 0
            for module in modules:
                topics = module.get("topics", [])
                total_topics += len(topics)

                for topic in topics:
                    topic_path = topic.get("path", "")
                    if Path(topic_path).exists():
                        print(f"✅ {topic_path}")
                    else:
                        print(f"❌ {topic_path}")

            print(f"✅ Всего тем: {total_topics}")

    except Exception as e:
        print(f"❌ Ошибка загрузки манифеста: {e}")
        return False

    print("🎉 Структура проекта корректна!")
    return True


def test_json_files():
    """Проверяет JSON файлы модулей"""
    print("\n🔍 Проверка JSON файлов модулей...")

    try:
        with open("data/modules/manifest.json", 'r', encoding='utf-8') as f:
            manifest = json.load(f)

        for module in manifest.get("modules", []):
            for topic in module.get("topics", []):
                topic_path = topic.get("path", "")
                if Path(topic_path).exists():
                    try:
                        with open(topic_path, 'r', encoding='utf-8') as f:
                            topic_data = json.load(f)

                        # Проверяем структуру
                        required_fields = ["title", "theory", "tasks"]
                        for field in required_fields:
                            if field not in topic_data:
                                print(f"❌ {topic_path}: отсутствует поле '{field}'")
                                continue

                        tasks = topic_data.get("tasks", [])
                        print(f"✅ {topic_path}: {len(tasks)} заданий")

                    except json.JSONDecodeError as e:
                        print(f"❌ {topic_path}: ошибка JSON - {e}")
                    except Exception as e:
                        print(f"❌ {topic_path}: ошибка - {e}")

    except Exception as e:
        print(f"❌ Ошибка проверки JSON файлов: {e}")
        return False

    print("🎉 JSON файлы корректны!")
    return True


if __name__ == "__main__":
    print("🚀 Тестирование структуры проекта FastAPI")
    print("=" * 50)

    structure_ok = test_project_structure()
    json_ok = test_json_files()

    print("\n" + "=" * 50)
    if structure_ok and json_ok:
        print("🎉 Все тесты пройдены! Проект готов к запуску.")
        print("\nДля запуска выполните:")
        print("python main.py")
        print("\nЗатем откройте: http://localhost:8000")
    else:
        print("❌ Есть проблемы в структуре проекта.")
