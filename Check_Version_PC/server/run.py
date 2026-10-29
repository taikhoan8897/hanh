import os
from waitress import serve
from server import app  # Nhập ứng dụng Flask từ file server.py

if __name__ == '__main__':
    # IIS sẽ tự cấp cổng qua biến môi trường 'PORT' nhờ cấu hình trong web.config
    port = int(os.environ.get('PORT', 8000)) 
    
    print(f"Starting Waitress server on port {port}...")
    serve(app, host='10.15.17.32', port=port)
