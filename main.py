import sys
import markdown
import tempfile
import webbrowser
import os
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtWidgets import (QApplication, QMainWindow, QSplitter, 
                             QTextEdit, QWidget, QVBoxLayout, 
                             QLabel, QScrollArea, QToolBar, 
                             QFileDialog, QAction)
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtGui import QFont, QTextCursor, QIcon
from PyQt5.QtGui import QIcon

class MarkdownIDE(QMainWindow):
    def __init__(self):
        super().__init__()
        self.current_file = None
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle('MarkE')
        self.setWindowIcon(QIcon('bin/favicon.ico'))  # Fixed: changed 'window' to 'self'
        self.setGeometry(100, 100, 1200, 800)
        
        # Создаем панель инструментов
        self.create_toolbar()
        
        # Создаем сплиттер для разделения редактора и предпросмотра
        splitter = QSplitter(Qt.Horizontal)
        
        # Редактор Markdown с обработчиками вставки
        self.editor = QTextEdit()
        self.editor.setFont(QFont('Consolas', 11))
        self.editor.canInsertFromMimeData = self.can_insert_from_mime_data
        self.editor.insertFromMimeData = self.insert_from_mime_data
        self.editor.textChanged.connect(self.update_preview)
        
        # Область предпросмотра
        self.preview = QWebEngineView()
        self.preview.setHtml(self.get_preview_html(""))
        
        # Добавляем виджеты в сплиттер
        splitter.addWidget(self.editor)
        splitter.addWidget(self.preview)
        
        # Настройка пропорций
        splitter.setSizes([400, 800])
        
        # Центральный виджет
        central_widget = QWidget()
        central_widget.setLayout(QVBoxLayout())
        central_widget.layout().addWidget(splitter)
        self.setCentralWidget(central_widget)
        
        # Пример содержимого
        self.editor.setPlainText("# Welcome to MarkE!\n\n"
                               "It's a simple Markdown IDE.\n\n"
                               "## Features\n"
                               "- Markdown editor\n"
                               "- Instant preview\n"
                               "- Syntax highlight (may not work)\n\n"
                               "```python\n"
                               "def example():\n"
                               "    print('Hello, Markdown!')\n"
                               "```\n\n"
                               "**Fat text** and _Italic text_")
        
    def can_insert_from_mime_data(self, source):
        """Разрешаем вставку только текста"""
        return source.hasText()
    
    def insert_from_mime_data(self, source):
        """Вставка только чистого текста без форматирования"""
        if source.hasText():
            text = source.text()
            # Очищаем текст от форматирования и специальных символов
            clean_text = text.replace('\xa0', ' ').replace('\u2028', '\n')
            self.editor.insertPlainText(clean_text)
    
    def create_toolbar(self):
        """Создает панель инструментов с кнопками"""
        toolbar = QToolBar("ToolBar")
        self.addToolBar(toolbar)
        
        # Действие "Открыть"
        open_action = QAction(QIcon.fromTheme('document-open'), "Open", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.open_file)
        toolbar.addAction(open_action)
        
        # Действие "Сохранить"
        save_action = QAction(QIcon.fromTheme('document-save'), "Save", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self.save_file)
        toolbar.addAction(save_action)
        
        # Действие "Сохранить как"
        save_as_action = QAction(QIcon.fromTheme('document-save-as'), "Save as", self)
        save_as_action.setShortcut("Ctrl+Shift+S")
        save_as_action.triggered.connect(self.save_file_as)
        toolbar.addAction(save_as_action)
        
        toolbar.addSeparator()
        
        # Действие "Открыть в браузере"
        browser_action = QAction(QIcon.fromTheme('internet-web-browser'), "Open in browser", self)
        browser_action.setShortcut("Ctrl+B")
        browser_action.triggered.connect(self.open_in_browser)
        toolbar.addAction(browser_action)
        
        toolbar.addSeparator()
        
        # Действие "Очистить форматирование"
        clean_action = QAction(QIcon.fromTheme('edit-clear'), "Clear formatting", self)
        clean_action.setShortcut("Ctrl+Space")
        clean_action.triggered.connect(self.clear_formatting)
        toolbar.addAction(clean_action)
    
    def clear_formatting(self):
        """Очищает форматирование выделенного текста"""
        cursor = self.editor.textCursor()
        if cursor.hasSelection():
            # Создаем новое форматирование с очищенными стилями
            fmt = QTextCursor().charFormat()
            fmt.clearBackground()
            fmt.clearForeground()
            cursor.setCharFormat(fmt)
    
    def open_file(self):
        """Открывает файл Markdown"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open Markdown file.", "", 
            "Markdown Files (*.md *.markdown);;All Files (*)"
        )
        
        if file_path:
            self.current_file = file_path
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    self.editor.setPlainText(content)
                    self.statusBar().showMessage(f"Working file: {file_path}")
                    self.setWindowTitle(f"MarkE - {os.path.basename(file_path)}")
            except Exception as e:
                self.statusBar().showMessage(f"Error while opening file: {str(e)}")
    
    def save_file(self):
        """Сохраняет файл Markdown"""
        if self.current_file:
            try:
                with open(self.current_file, 'w', encoding='utf-8') as f:
                    f.write(self.editor.toPlainText())
                    self.statusBar().showMessage(f"File saved: {self.current_file}")
            except Exception as e:
                self.statusBar().showMessage(f"Error while saving file: {str(e)}")
        else:
            self.save_file_as()
    
    def save_file_as(self):
        """Сохраняет файл Markdown с указанием нового имени"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save MD file.", "", 
            "Markdown Files (*.md *.markdown);;All Files (*)"
        )
        
        if file_path:
            self.current_file = file_path
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(self.editor.toPlainText())
                    self.statusBar().showMessage(f"File saved: {file_path}")
                    self.setWindowTitle(f"MarkE - {os.path.basename(file_path)}")
            except Exception as e:
                self.statusBar().showMessage(f"Error while saving file: {str(e)}")
    
    def open_in_browser(self):
        """Открывает текущий Markdown в системном браузере"""
        markdown_text = self.editor.toPlainText()
        html = self.get_preview_html(markdown_text)
        
        # Создаем временный HTML файл
        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', 
                                        suffix='.html', delete=False) as f:
            f.write(html)
            temp_path = f.name
        
        # Открываем в браузере
        webbrowser.open('file://' + temp_path)
        self.statusBar().showMessage("in browser...")
    
    def update_preview(self):
        """Обновляет предпросмотр при изменении текста"""
        markdown_text = self.editor.toPlainText()
        html = self.get_preview_html(markdown_text)
        self.preview.setHtml(html)
        
    def get_preview_html(self, markdown_text):
        """Генерирует HTML для предпросмотра с GitHub-стилями"""
        # Преобразуем Markdown в HTML
        html_content = markdown.markdown(markdown_text, extensions=[
            'fenced_code',  # Поддержка блоков кода
            'codehilite',  # Подсветка синтаксиса
            'tables',      # Поддержка таблиц
            'footnotes',   # Сноски
            'toc'          # Оглавление
        ])
        
        # CSS в стиле GitHub
        github_css = """
        <style>
            body {
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
                font-size: 16px;
                line-height: 1.5;
                color: #24292e;
                background-color: #fff;
                padding: 20px;
            }
            h1, h2, h3, h4, h5, h6 {
                margin-top: 24px;
                margin-bottom: 16px;
                font-weight: 600;
                line-height: 1.25;
            }
            h1 { font-size: 2em; border-bottom: 1px solid #eaecef; padding-bottom: 0.3em; }
            h2 { font-size: 1.5em; border-bottom: 1px solid #eaecef; padding-bottom: 0.3em; }
            code, pre {
                font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, monospace;
                font-size: 12px;
            }
            pre {
                padding: 16px;
                overflow: auto;
                line-height: 1.45;
                background-color: #f6f8fa;
                border-radius: 6px;
            }
            blockquote {
                padding: 0 1em;
                color: #6a737d;
                border-left: 0.25em solid #dfe2e5;
                margin: 0 0 16px 0;
            }
            table {
                border-collapse: collapse;
                margin: 16px 0;
                display: block;
                width: 100%;
                overflow: auto;
            }
            table th, table td {
                padding: 6px 13px;
                border: 1px solid #dfe2e5;
            }
            table tr {
                background-color: #fff;
                border-top: 1px solid #c6cbd1;
            }
            table tr:nth-child(2n) {
                background-color: #f6f8fa;
            }
            img {
                max-width: 100%;
                box-sizing: content-box;
                background-color: #fff;
            }
        </style>
        """
        
        # Подключение highlight.js для подсветки синтаксиса
        highlight_js = """
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.3.1/styles/github.min.css">
        <script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.3.1/highlight.min.js"></script>
        <script>hljs.highlightAll();</script>
        """
        
        # Собираем итоговый HTML
        full_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Markdown Preview</title>
            {github_css}
            {highlight_js}
        </head>
        <body>
            {html_content}
        </body>
        </html>
        """
        
        return full_html

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ide = MarkdownIDE()
    ide.show()
    sys.exit(app.exec_())