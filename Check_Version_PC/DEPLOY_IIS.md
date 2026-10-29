# Hướng Dẫn Deploy Server Flask Lên IIS

## 📋 Yêu Cầu

- Windows Server hoặc Windows với IIS đã cài đặt
- Python 3.8+ đã cài đặt trên server
- IIS URL Rewrite Module
- Quyền admin

## 🔧 Bước 1: Cài Đặt IIS (nếu chưa có)

**Windows Server:**
```powershell
# Mở PowerShell as Admin
Add-WindowsFeature Web-Server, Web-App-Dev, Web-CGI
```

**Windows 10/11:**
- Mở Control Panel → Programs → Turn Windows features on or off
- Tìm và enable: **Internet Information Services (IIS)**
- Chọn các tính năng:
  - Web Management Tools
  - IIS Management Console
  - CGI

## 🔧 Bước 2: Cài Đặt IIS URL Rewrite Module

1. Download: https://www.iis.net/downloads/microsoft/url-rewrite
2. Cài đặt file .msi

## 🔧 Bước 3: Tạo Thư Mục Ứng Dụng

```powershell
# Tạo thư mục cho app trên server
mkdir "C:\inetpub\AssetCheckServer"

# Copy toàn bộ file từ server/ vào thư mục này
# server.py
# config.py
# requirements.txt
```

## 🔧 Bước 4: Cài Đặt Dependencies

```powershell
# Mở Command Prompt as Admin
cd C:\inetpub\AssetCheckServer

# Cài thư viện
pip install -r requirements.txt

# Cài WSGI server (cần cho IIS)
pip install wfastcgi
```

## 🔧 Bước 5: Cấu Hình FastCGI

```powershell
# Chạy PowerShell as Admin
wfastcgi-enable
```

## 🔧 Bước 6: Tạo File web.config

Tạo file `web.config` trong thư mục `C:\inetpub\AssetCheckServer`:

```xml
<?xml version="1.0" encoding="utf-8"?>
<configuration>
  <system.webServer>
    <security>
      <requestFiltering>
        <fileExtensions>
          <add fileExtension=".py" allowed="false" />
        </fileExtensions>
      </requestFiltering>
    </security>
    <staticContent>
      <mimeMap fileExtension=".py" mimeType="text/plain" />
    </staticContent>
    <handlers>
      <add name="Python FastCGI" path="*" verb="*" modules="FastCgiModule" scriptProcessor="C:\Python311\python.exe|C:\Python311\lib\site-packages\wfastcgi.py" resourceType="Unspecified" requireAccess="Script" />
    </handlers>
    <rewrite>
      <rules>
        <rule name="Static Files" stopProcessing="true">
          <match url="^/static/.*" />
          <action type="Rewrite" url="{PATH_INFO}" />
        </rule>
        <rule name="Flask" stopProcessing="true">
          <match url="^(?!static)" ignoreCase="false" />
          <conditions logicalGrouping="MatchAll" trackAllCaptures="false" />
          <action type="Rewrite" url="server.py" />
        </rule>
      </rules>
    </rewrite>
  </system.webServer>
  <appSettings>
    <add key="WSGI_HANDLER" value="server.app" />
    <add key="PYTHONPATH" value="C:\inetpub\AssetCheckServer" />
  </appSettings>
</configuration>
```

⚠️ **Thay đổi `C:\Python311` với đường dẫn Python của bạn!**

## 🔧 Bước 7: Tạo App Pool Mới Trong IIS

1. Mở **IIS Manager**
2. Chuột phải vào **Application Pools** → **Add Application Pool...**
3. Điền:
   - Name: `AssetCheckPool`
   - .NET CLR version: `No Managed Code`
   - Managed pipeline mode: `Classic`
4. Click **OK**

## 🔧 Bước 8: Tạo Website Mới Trong IIS

1. Mở **IIS Manager**
2. Chuột phải vào **Sites** → **Add Website...**
3. Điền:
   - Site name: `AssetCheckServer`
   - Application pool: `AssetCheckPool`
   - Physical path: `C:\inetpub\AssetCheckServer`
   - Binding:
     - Type: `http`
     - IP: `All Unassigned` (hoặc chọn IP cụ thể)
     - Port: `5000` (hoặc port khác)
     - Host name: (để trống hoặc điền domain)
4. Click **OK**

## 🔧 Bước 9: Cấp Quyền Thư Mục

```powershell
# Mở PowerShell as Admin
$path = "C:\inetpub\AssetCheckServer"

# Cấp quyền cho IIS_IUSRS
icacls $path /grant "IIS_IUSRS:(OI)(CI)F" /T
icacls $path /grant "IUSR:(OI)(CI)F" /T
```

## 🔧 Bước 10: Kiểm Tra & Khởi Động

1. Mở IIS Manager
2. Click vào site `AssetCheckServer`
3. Bên phải, click **Browse *.5000 (http)**
   - Nếu thấy trang Flask → ✅ Thành công!
   - Nếu lỗi → Xem **Logs**

**Hoặc test bằng cURL:**
```powershell
Invoke-WebRequest http://localhost:5000/submit
```

## 📊 Kiểm Tra Logs

Logs nằm ở:
```
C:\inetpub\logs\LogFiles\W3SVC1\
```

## 🔍 Khắc Phục Sự Cố

**Lỗi 500 Internal Server Error:**
- Kiểm tra `web.config`
- Kiểm tra quyền thư mục
- Xem logs IIS

**Lỗi: Python không tìm được:**
- Đảm bảo đúng đường dẫn Python trong `web.config`
- Chạy `python --version` để kiểm tra

**Lỗi: Không thể kết nối Database:**
- Kiểm tra kết nối SQL Server
- Đảm bảo SQL Server port mở (1433)
- Kiểm tra firewall

## ✅ Sau Khi Deploy

Client sẽ gửi dữ liệu đến:
```
http://10.15.27.77:5000/submit
```

Hoặc nếu dùng domain:
```
http://yourdomain.com:5000/submit
```

**Cập nhật file `client/config.py`:**
```python
SERVER_URL = "http://10.15.27.77:5000/submit"
```

## 🚀 Chạy Server Ngoài IIS (Tạm Thời)

Nếu chưa sẵn sàng deploy IIS, có thể chạy trực tiếp:
```powershell
cd C:\path\to\server
python server.py
```
