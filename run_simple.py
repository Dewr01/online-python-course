#!/usr/bin/env python3
"""
Простой запуск FastAPI приложения без установки зависимостей
Использует встроенные модули Python
"""
import json
import os
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import threading
import webbrowser
import time


class CourseHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Обработка GET запросов"""
        parsed_path = urlparse(self.path)
        path = parsed_path.path

        if path == '/':
            self.serve_index()
        elif path == '/static/style.css':
            self.serve_css()
        elif path.startswith('/api/'):
            self.serve_api(path)
        else:
            self.send_error(404)

    def do_POST(self):
        """Обработка POST запросов"""
        parsed_path = urlparse(self.path)
        path = parsed_path.path

        if path == '/api/check-answer':
            self.handle_check_answer()
        else:
            self.send_error(404)

    def serve_index(self):
        """Отдает главную страницу"""
        try:
            # Загружаем данные курса
            course_data = self.load_course_data()

            # Читаем HTML шаблон
            with open('templates/index.html', 'r', encoding='utf-8') as f:
                html_content = f.read()

            # Заменяем переменные в шаблоне
            modules_html = self.generate_modules_html(course_data['modules'])
            lessons_js = self.generate_lessons_js(course_data['lessons'])

            html_content = html_content.replace('{% for module in modules %}', '')
            html_content = html_content.replace('{% endfor %}', '')
            html_content = html_content.replace('{{ loop.index0 }}', '0')
            html_content = html_content.replace('{{ module.title }}', 'Модуль')
            html_content = html_content.replace('{{ topic.title }}', 'Тема')
            html_content = html_content.replace('{{ topic.id }}', 'topic-id')

            # Добавляем данные в HTML
            html_content = html_content.replace('</body>', f'''
    <script>
        const COURSE_DATA = {json.dumps(course_data, ensure_ascii=False)};
        {lessons_js}
    </script>
</body>''')

            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(html_content.encode('utf-8'))

        except Exception as e:
            self.send_error(500, f"Ошибка загрузки страницы: {str(e)}")

    def serve_css(self):
        """Отдает CSS файл"""
        try:
            with open('static/style.css', 'r', encoding='utf-8') as f:
                css_content = f.read()

            self.send_response(200)
            self.send_header('Content-type', 'text/css')
            self.end_headers()
            self.wfile.write(css_content.encode('utf-8'))

        except Exception as e:
            self.send_error(404)

    def serve_api(self, path):
        """Обрабатывает API запросы"""
        try:
            course_data = self.load_course_data()

            if path == '/api/modules':
                response = {'modules': course_data['modules']}
            elif path == '/api/lessons':
                response = {'lessons': course_data['lessons']}
            elif path == '/api/health':
                response = {
                    'status': 'ok',
                    'modules_count': len(course_data['modules']),
                    'lessons_count': len(course_data['lessons'])
                }
            else:
                self.send_error(404)
                return

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))

        except Exception as e:
            self.send_error(500, f"Ошибка API: {str(e)}")

    def handle_check_answer(self):
        """Обрабатывает проверку ответов"""
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))

            # Простая проверка ответа
            task_id = data.get('task_id', '')
            answer = data.get('answer', '').strip().lower()

            # Находим задание в данных курса
            correct_answer = None
            hint = ""

            for lesson in self.load_course_data()['lessons']:
                for task in lesson.get('tasks', []):
                    if task['id'] == task_id:
                        correct_answer = task['answer'].strip().lower()
                        hint = task['hint']
                        break
                if correct_answer:
                    break

            if correct_answer is None:
                self.send_error(404, "Задание не найдено")
                return

            is_correct = answer == correct_answer

            response = {
                'correct': is_correct,
                'expected': correct_answer,
                'hint': hint,
                'attempts': 1
            }

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))

        except Exception as e:
            self.send_error(500, f"Ошибка проверки: {str(e)}")

    def load_course_data(self):
        """Загружает данные курса"""
        course_data = {'modules': [], 'lessons': []}

        # Загружаем манифест
        manifest_path = Path('data/modules/manifest.json')
        if manifest_path.exists():
            with open(manifest_path, 'r', encoding='utf-8') as f:
                manifest = json.load(f)
                course_data['modules'] = manifest.get('modules', [])

        # Загружаем уроки
        for module in course_data['modules']:
            for topic in module.get('topics', []):
                lesson_path = Path(topic['path'])
                if lesson_path.exists():
                    with open(lesson_path, 'r', encoding='utf-8') as f:
                        lesson_data = json.load(f)
                        lesson = {
                            'id': topic['id'],
                            'title': f"{module['title']} - {topic['title']}",
                            'module_id': module['id'],
                            'topic_id': topic['id'],
                            'theory': lesson_data.get('theory', ''),
                            'tasks': lesson_data.get('tasks', [])
                        }
                        course_data['lessons'].append(lesson)

        return course_data

    def generate_modules_html(self, modules):
        """Генерирует HTML для модулей"""
        html = ""
        for i, module in enumerate(modules):
            html += f'''
            <div class="module-item">
                <div class="module-header" data-module-index="{i}">
                    <span class="module-title">{module['title']}</span>
                    <span class="module-arrow">▶</span>
                </div>
                <div class="module-topics" style="display: none;">
            '''
            for j, topic in enumerate(module.get('topics', [])):
                html += f'''
                    <div class="topic-item">
                        <span class="topic-title" 
                              data-module-index="{i}" 
                              data-topic-index="{j}"
                              data-lesson-id="{topic['id']}">
                            {topic['title']}
                        </span>
                    </div>
                '''
            html += '''
                </div>
            </div>
            '''
        return html

    def generate_lessons_js(self, lessons):
        """Генерирует JavaScript для уроков"""
        return f"""
        // Данные уроков
        const LESSONS = {json.dumps(lessons, ensure_ascii=False)};
        
        // Простая функция загрузки урока
        function loadLesson(lessonId) {{
            const lesson = LESSONS.find(l => l.id === lessonId);
            if (lesson) {{
                document.getElementById('current-lesson-title').textContent = lesson.title;
                loadTasks(lesson.tasks);
            }}
        }}
        
        // Функция загрузки заданий
        function loadTasks(tasks) {{
            const container = document.getElementById('tasks-container');
            container.innerHTML = '';
            
            if (!tasks || tasks.length === 0) {{
                container.innerHTML = '<em>Нет заданий для этого урока.</em>';
                return;
            }}
            
            tasks.forEach(task => {{
                const row = document.createElement('div');
                row.className = 'task-row';
                row.innerHTML = `
                    <label class="task-label">${{task.question}}</label>
                    <div class="task-input-group">
                        <input class="task-input" type="text" data-task-id="${{task.id}}" placeholder="Ваш ответ" />
                        <button class="btn btn-sm btn-submit" data-task-id="${{task.id}}">Отправить</button>
                    </div>
                `;
                container.appendChild(row);
            }});
            
            // Добавляем обработчики
            document.querySelectorAll('.btn-submit').forEach(btn => {{
                btn.addEventListener('click', function() {{
                    const taskId = this.dataset.taskId;
                    const input = this.previousElementSibling;
                    const answer = input.value.trim();
                    
                    if (!answer) {{
                        alert('Пожалуйста, введите ответ');
                        return;
                    }}
                    
                    checkAnswer(taskId, answer, input, this);
                }});
            }});
        }}
        
        // Функция проверки ответа
        async function checkAnswer(taskId, answer, input, button) {{
            try {{
                const response = await fetch('/api/check-answer', {{
                    method: 'POST',
                    headers: {{'Content-Type': 'application/json'}},
                    body: JSON.stringify({{task_id: taskId, answer: answer}})
                }});
                
                const result = await response.json();
                
                if (result.correct) {{
                    input.style.borderColor = '#10b981';
                    input.style.backgroundColor = '#d1fae5';
                    button.textContent = '✓';
                    button.disabled = true;
                    input.disabled = true;
                }} else {{
                    input.style.borderColor = '#ef4444';
                    input.style.backgroundColor = '#fee2e2';
                    button.textContent = 'Неверно';
                }}
            }} catch (error) {{
                console.error('Ошибка проверки:', error);
                alert('Ошибка проверки ответа');
            }}
        }}
        """


def open_browser():
    """Открывает браузер через 2 секунды"""
    time.sleep(2)
    webbrowser.open('http://localhost:8000')


def main():
    """Главная функция"""
    print("🚀 Запуск простого сервера курса Python 3.12")
    print("=" * 50)

    # Проверяем структуру
    if not Path('templates/index.html').exists():
        print("❌ Файл templates/index.html не найден")
        return

    if not Path('static/style.css').exists():
        print("❌ Файл static/style.css не найден")
        return

    if not Path('data/modules/manifest.json').exists():
        print("❌ Файл data/modules/manifest.json не найден")
        return

    print("✅ Структура проекта корректна")

    # Запускаем сервер
    server = HTTPServer(('localhost', 8000), CourseHandler)
    print("🌐 Сервер запущен на http://localhost:8000")
    print("📚 Откройте браузер для просмотра курса")
    print("⏹️  Нажмите Ctrl+C для остановки")

    # Открываем браузер в отдельном потоке
    browser_thread = threading.Thread(target=open_browser)
    browser_thread.daemon = True
    browser_thread.start()

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Сервер остановлен")
        server.shutdown()


if __name__ == "__main__":
    main()
