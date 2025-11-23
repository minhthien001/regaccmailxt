# ================================================================
# key_manager.py
# Quản lý key kích hoạt từ Google Sheet + Apps Script
# ---------------------------------------------------------------
# Cấu trúc Sheet:
#   A: KEY | B: THIẾT BỊ | C: NGÀY HẾT HẠN | D: GIỜ HẾT HẠN
#   E: TRẠNG THÁI | F: TRẠNG THÁI KEY | G: ACTIVATED_AT
# ================================================================

import uuid
import requests
import datetime
import threading
import time
import csv
import io

# ---------------------------------------------------------------
# ⚙️ Cấu hình (bạn KHÔNG cần sửa thêm)
# ---------------------------------------------------------------

# ✅ Link Google Sheet (xuất dạng CSV)
SHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/1Jp01lMq5Jajom6Eo3Zm6XUbVTd5ht_TAE-TJoev3wXM/export?format=csv"

# ✅ Link Apps Script Web App (bản bạn đã deploy)
APPS_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbwpEkGvCFnBPDqZBWq2Ralw28T0mxKP1ikFnzP0LKd2ZUVjJH76-ODLn3kKZ67r2FC4/exec"

# ---------------------------------------------------------------
# 🔑 Mã định danh máy (UUID dựa trên MAC address)
# ---------------------------------------------------------------
MACHINE_CODE = str(uuid.UUID(int=uuid.getnode())).lower()


# ---------------------------------------------------------------
# 🛰️ Gửi mã máy lên Apps Script để ghi vào Sheet
# ---------------------------------------------------------------
def update_device_to_sheet(key):
    """Gửi mã máy lên Apps Script để ghi vào cột 'THIẾT BỊ'"""
    try:
        data = {"key": key, "machine_code": MACHINE_CODE}
        res = requests.post(APPS_SCRIPT_URL, json=data, timeout=10)
        print("📡 Gửi cập nhật thiết bị:", res.text)
    except Exception as e:
        print("❌ Lỗi ghi thiết bị lên sheet:", e)


# ---------------------------------------------------------------
# 📥 Đọc key từ Google Sheet (file CSV)
# ---------------------------------------------------------------
def fetch_key_from_sheet(user_key=None):
    """
    Đọc Google Sheet, tìm key người dùng nhập.
    Nếu hợp lệ → ghi mã máy.
    Trả về (key, expiry_datetime, status)
    """
    try:
        resp = requests.get(SHEET_CSV_URL, timeout=10)
        resp.raise_for_status()

        csv_data = io.StringIO(resp.text)
        reader = csv.reader(csv_data)
        next(reader)  # Bỏ hàng tiêu đề

        for row in reader:
            while len(row) < 7:
                row.append("")

            key_val = row[0].strip()
            device = row[1].strip()
            expiry_date = row[2].strip()
            expiry_time = row[3].strip()
            status_text = row[4].strip()
            key_status = row[5].strip()

            # Tìm đúng key
            if key_val.lower() == (user_key or "").strip().lower():
                expiry = None
                if expiry_date and expiry_time:
                    try:
                        expiry = datetime.datetime.strptime(
                            expiry_date + " " + expiry_time, "%d/%m/%Y %H:%M"
                        )
                    except:
                        pass

                # 1️⃣ Key đã dùng cho máy khác
                if device and device not in ("", "(auto điền)", MACHINE_CODE):
                    return key_val, expiry, "key_used_by_other"

                # 2️⃣ Key chưa gán máy → ghi mới
                if not device or device in ("", "(auto điền)"):
                    threading.Thread(
                        target=update_device_to_sheet, args=(key_val,), daemon=True
                    ).start()
                    if expiry and datetime.datetime.now() > expiry:
                        return key_val, expiry, "expired"
                    return key_val, expiry, "activated_new"

                # 3️⃣ Key trùng máy → hợp lệ
                if device == MACHINE_CODE:
                    if expiry and datetime.datetime.now() > expiry:
                        return key_val, expiry, "expired"
                    return key_val, expiry, "already_activated"

        # 4️⃣ Không tìm thấy key
        return None, None, "not_found"

    except Exception as e:
        print("❌ Lỗi đọc sheet:", e)
        return None, None, "no_connection"


# ---------------------------------------------------------------
# 🔁 Theo dõi trạng thái key định kỳ
# ---------------------------------------------------------------
def start_polling(callback, user_key, interval=5):
    """Gọi callback(state) mỗi {interval} giây"""
    def loop():
        while True:
            key, expiry, status = fetch_key_from_sheet(user_key)
            state = {"key": key, "expiry": expiry, "status": status}
            try:
                callback(state)
            except Exception as e:
                print("❌ Lỗi callback:", e)
            time.sleep(interval)

    t = threading.Thread(target=loop, daemon=True)
    t.start()


# ---------------------------------------------------------------
# 🧪 Kiểm tra nhanh (chạy riêng file này)
# ---------------------------------------------------------------
if __name__ == "__main__":
    print("Mã máy:", MACHINE_CODE)
    user_key = input("Nhập key: ").strip()
    key, expiry, status = fetch_key_from_sheet(user_key)
    print("\nKết quả kiểm tra:")
    print("  Key:", key)
    print("  Mã máy:", MACHINE_CODE)
    print("  Hết hạn:", expiry)
    print("  Trạng thái:", status)
