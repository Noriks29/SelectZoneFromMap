from http.server import BaseHTTPRequestHandler, HTTPServer
import os
from pathlib import Path

class CombinedHandler(BaseHTTPRequestHandler):
    def __init__(self, *args, vue_dist_path='dist', **kwargs):
        self.vue_dist_path = Path(vue_dist_path)
        super().__init__(*args, **kwargs)
    
    def do_GET(self):
        # Обработка запросов к изображениям (начинаются с /map/)
        if self.path.startswith('/map/'):
            self.handle_image_request()
        else:
            self.handle_vue_request()
    
    def handle_image_request(self):
        """Обработка запросов к изображениям"""
        try:
            # Безопасное формирование пути к файлу
            path = self.path.lstrip('/')
            full_path = path
            
            # Проверка существования файла и что он в разрешенной директории
            if not os.path.exists(full_path) or not os.path.isfile(full_path):
                raise FileNotFoundError
            
            # Определение Content-Type по расширению файла
            ext = os.path.splitext(full_path)[1].lower()
            content_type = {
                '.jpg': 'image/jpeg',
                '.jpeg': 'image/jpeg',
                '.png': 'image/png',
                '.gif': 'image/gif'
            }.get(ext, 'application/octet-stream')
            
            # Чтение и отправка файла
            with open(full_path, 'rb') as f:
                self.send_response(200)
                self.send_header('Content-type', content_type)
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(f.read())
                
        except FileNotFoundError:
            self.send_error(404, "File Not Found")
        except Exception as e:
            self.send_error(500, f"Server Error: {str(e)}")
    
    def handle_vue_request(self):
        """Обработка запросов к Vue приложению"""
        try:
            # Определяем путь к файлу в папке dist
            if self.path == '/':
                file_path = self.vue_dist_path / 'index.html'
            else:
                file_path = self.vue_dist_path / self.path.lstrip('/')
            
            # Если файл не существует, возвращаем index.html (для Vue Router)
            if not file_path.exists() or not file_path.is_file():
                file_path = self.vue_dist_path / 'index.html'
            
            # Определяем Content-Type
            ext = file_path.suffix.lower()
            content_types = {
                '.html': 'text/html',
                '.css': 'text/css',
                '.js': 'application/javascript',
                '.json': 'application/json',
                '.png': 'image/png',
                '.jpg': 'image/jpeg',
                '.jpeg': 'image/jpeg',
                '.gif': 'image/gif',
                '.svg': 'image/svg+xml',
                '.ico': 'image/x-icon'
            }
            content_type = content_types.get(ext, 'application/octet-stream')
            
            # Читаем и отправляем файл
            with open(file_path, 'rb') as f:
                self.send_response(200)
                self.send_header('Content-type', content_type)
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(f.read())
                
        except FileNotFoundError:
            self.send_error(404, "File Not Found")
        except Exception as e:
            self.send_error(500, f"Server Error: {str(e)}")
    
    def log_message(self, format, *args):
        """Кастомное логирование"""
        print(f"{self.client_address[0]} - - [{self.log_date_time_string()}] {format % args}")

class CustomHTTPServer(HTTPServer):
    def __init__(self, server_address, handler_class, vue_dist_path):
        self.vue_dist_path = vue_dist_path
        super().__init__(server_address, handler_class)
    
    def finish_request(self, request, client_address):
        """Переопределяем для передачи дополнительных параметров в handler"""
        self.RequestHandlerClass(request, client_address, self, vue_dist_path=self.vue_dist_path)

class VueLiveServer:
    def __init__(self, port=8080, host='localhost', vue_dist_path='dist'):
        self.port = port
        self.host = host
        self.vue_dist_path = Path(vue_dist_path)
        
    def start_server(self):
        """Запуск объединенного HTTP сервера"""
        # Проверяем существование папки dist
        if not self.vue_dist_path.exists():
            print(f"❌ Папка {self.vue_dist_path} не найдена!")
            print("Сначала выполните: npm run build")
            return
        
        print(f"📁 Обслуживается из: {self.vue_dist_path.absolute()}")
        print(f"🌐 Сервер запущен на http://{self.host}:{self.port}")
        print("🗺️  API изображений доступно по пути: /map/")
        
        # Создаем кастомный сервер с передачей параметров
        server = CustomHTTPServer(
            (self.host, self.port), 
            CombinedHandler, 
            vue_dist_path=str(self.vue_dist_path)
        )
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print("\n🛑 Сервер остановлен")
        finally:
            server.server_close()
# Использование
if __name__ == "__main__":
    print("🎯 Cервер (Vue + изображения)")
    server = VueLiveServer(port=8080, vue_dist_path='dist')
    server.start_server()