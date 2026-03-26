# test_connection.py
from config import DatabaseHelper
import sys


def main():
    print("=" * 40)
    print("🛠  KIỂM TRA KẾT NỐI DATABASE (clothingstore)")
    print("=" * 40)

    # Khởi tạo helper
    db = DatabaseHelper()

    # BƯỚC 1: THỬ KẾT NỐI
    print("\n[Bước 1] Đang kết nối đến MySQL...")
    conn = db.connect()

    if conn and conn.is_connected():
        print(f"   ✅ KẾT NỐI THÀNH CÔNG!")
        print(f"   -> MySQL Version: {conn.server_info}")
        print(f"   -> Database đang chọn: {conn.database}")
    else:
        print("   ❌ KẾT NỐI THẤT BẠI!")
        print("   -> Gợi ý: Kiểm tra lại file 'db_config.py' (user, password, port).")
        # Dừng chương trình nếu không kết nối được
        sys.exit()

    # BƯỚC 2: THỬ TRUY VẤN DỮ LIỆU (SELECT)
    print("\n[Bước 2] Kiểm tra đọc dữ liệu (Bảng NhanVien)...")
    try:
        # Lấy thử tên các nhân viên
        sql = "SELECT idNhanVien, hoTen, phanQuyen FROM nhanVien"
        data = db.fetch_all(sql)

        if data:
            print(f"   ✅ TRUY VẤN THÀNH CÔNG! Tìm thấy {len(data)} nhân viên:")
            for nv in data:
                print(f"      - ID: {nv['idNhanVien']} | Tên: {nv['hoTen']} ({nv['phanQuyen']})")
        else:
            print("   ⚠️ Truy vấn chạy được nhưng không có dữ liệu (Bảng rỗng).")

    except Exception as e:
        print(f"   ❌ LỖI TRUY VẤN: {e}")

    # BƯỚC 3: ĐÓNG KẾT NỐI
    print("\n[Bước 3] Đóng kết nối...")
    db.disconnect()
    print("   ✅ Đã ngắt kết nối an toàn.")

    print("\n" + "=" * 40)
    print("KẾT LUẬN: HỆ THỐNG SẴN SÀNG!")
    print("=" * 40)


if __name__ == "__main__":
    main()