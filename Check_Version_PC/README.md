# AssetCheck - Hướng Dẫn Sử Dụng

## 📋 Mô Tả
Ứng dụng kiểm tra thông tin máy tính (phiên bản, RAM, CPU, ổ cứng, v.v.) và gửi dữ liệu lên server.

## 🔧 Cài Đặt

### 1. Cài Đặt Thư Viện
```bash
pip install -r requirements.txt
```

### 2. Cập Nhật Database
- Mở SQL Server Management Studio
- Chạy script: `UpdateDatabase.sql`
- Hoặc chạy các lệnh ALTER TABLE để thêm cột mới

### 3. Cấu Hình

**Client (client/config.py):**
```python
SERVER_URL = "http://10.15.27.77:5000/submit"  # Thay đổi IP server nếu cần
```

**Server (server/config.py):**
```python
SQL_CONFIG = {
    "driver": "ODBC Driver 17 for SQL Server",
    "server": "10.15.27.77",
    "database": "AssetManagement",
    "username": "sa",
    "password": "abcd1234"
}
```

## 🚀 Chạy Ứng Dụng

### Chạy Client (GUI)
```bash
python client/client.py
```

### Chạy Server (Backend)
```bash
python server/server.py
```

## 📦 Đóng Gói Client Thành .exe
```bash
cd client
pyinstaller --onefile client.py
```
File .exe sẽ nằm trong thư mục `dist/`

## 📊 Dữ Liệu Được Thu Thập

| Thông Tin | Mô Tả |
|-----------|-------|
| Họ tên | Tên nhân viên |
| Mã số | Mã số nhân viên |
| Bộ phận | Phòng ban công tác |
| Loại tài sản | Tài sản cá nhân/công ty |
| Tên máy | Model máy tính |
| Serial Number | Số seri máy |
| Windows Key | Product Key Windows |
| Phiên bản Windows | OS version |
| Kiến trúc | 32-bit/64-bit |
| Hostname | Tên máy trên mạng |
| User Windows | Người dùng đăng nhập |
| IP Address | Địa chỉ IP |
| Office License | Trạng thái license Office |
| **RAM** | **Dung lượng RAM (GB)** |
| **CPU** | **Loại CPU và số cores** |
| **Ổ cứng** | **Dung lượng ổ cứng (GB)** |

## 🔍 Các Cột Mới Trong Database

```sql
RamInfo NVARCHAR(50)      -- Ví dụ: "16.00 GB"
CpuInfo NVARCHAR(255)     -- Ví dụ: "Intel Core i7-10700K (8 cores)"
DiskInfo NVARCHAR(255)    -- Ví dụ: "Tổng: 2102.45 GB (C: 238.17GB | E: ...)"
```

## ⚠️ Lưu Ý

1. Đảm bảo server SQL Server đang chạy
2. Kiểm tra kết nối mạng giữa client và server
3. Cần quyền admin để chạy client (lấy thông tin hardware)
4. Firewall cần allow port 5000 (mặc định)

## 🛠️ Khắc Phục Sự Cố

**Lỗi: "Không lấy được thông tin"**
- Chạy client với quyền admin
- Kiểm tra WMIC/PowerShell có sẵn không

**Lỗi: "Lỗi kết nối server"**
- Kiểm tra SERVER_URL trong config.py
- Đảm bảo server đang chạy

**Lỗi: "Dữ liệu đã tồn tại"**
- Mã nhân viên hoặc Serial Number đã được ghi nhận
- Kiểm tra database hoặc thay đổi mã nhân viên
