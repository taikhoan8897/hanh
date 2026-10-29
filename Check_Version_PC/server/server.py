from flask import Flask, request, jsonify
import pypyodbc as pyodbc

from config import SQL_CONFIG, API_CONFIG

app = Flask(__name__)

# Connection string
conn_str = (
    f"DRIVER={{{SQL_CONFIG['driver']}}};"
    f"SERVER={SQL_CONFIG['server']};"
    f"DATABASE={SQL_CONFIG['database']};"
    f"UID={SQL_CONFIG['username']};"
    f"PWD={SQL_CONFIG['password']};"
    "TrustServerCertificate=yes;"
)

@app.route('/submit', methods=['POST'])
def submit():
    data = request.json
    # print("DATA RECEIVED:", data)
    try:
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        # =========================
        # CHECK DUPLICATE
        # =========================
        cursor.execute("""
            SELECT COUNT(*)
            FROM ComputerAssets
            WHERE EmployeeCode = ?
               OR SerialNumber = ?
        """,
        (
            data['employee_code'],
            data['serial_number']
        ))
        count = cursor.fetchone()[0]
        print("COUNT =", count)
        # Nếu trùng
        if count > 0:
            cursor.close()
            conn.close()
            return jsonify({
                "success": False,
                "message": "Dữ liệu đã tồn tại"
            })
        # =========================
        # INSERT
        # =========================
        print("START INSERT")

        cursor.execute("""
            INSERT INTO ComputerAssets
            (
                FullName,
                EmployeeCode,
                Department,
                AssetType,
                MachineName,
                SerialNumber,
                WindowsKey,
               
                Architecture,
                OfficeLicense,
                RamInfo,
                CpuInfo,
                DiskInfo
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            data['full_name'],
            data['employee_code'],
            data['department'],
            data['asset_type'],
            data['machine_name'],
            data['serial_number'],
            data['windows_key'],
           
            data['architecture'],
            data['office_license'],
            data['ram_info'],
            data['cpu_info'],
            data['disk_info']
        ))
        conn.commit()
        print("INSERT SUCCESS")
        cursor.close()
        conn.close()
        return jsonify({
            "success": True
        })
    except Exception as e:
        # print("SQL ERROR:", str(e))
        return jsonify({
            "success": False,
            "message": str(e)
        })
if __name__ == '__main__':
    from waitress import serve
    print("Server Waitress dang chay truc tiep tren mang LAN cong 2804...")
    # Thay đổi sang 0.0.0.0 để chấp nhận mọi kết nối trong mạng LAN
    serve(app, host='0.0.0.0', port=2804)