import customtkinter as ctk
from tkinter import messagebox, ttk, filedialog
from datetime import datetime
import pandas as pd
from src.Controller.LuongController import LuongController


class LuongPage(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="white")

        self.controller = LuongController()

        self.current_list = []
        self.selected_id = None
        self.selected_name = None

        self.tao_main_content()
        self.load_data()

    def tao_main_content(self):
        container = ctk.CTkFrame(self, fg_color="white")
        container.pack(fill="both", expand=True, padx=15, pady=15)

        # === HEADER ===
        header = ctk.CTkFrame(container, fg_color="white")
        header.pack(fill="x", pady=(0, 15))

        ctk.CTkLabel(header, text="Quản Lý Lương Nhân Viên",
                     font=("Arial", 18, "bold"), text_color="#333").pack(side="left")

        # Combobox Chọn Tháng
        now = datetime.now()
        months = [f"Tháng {m}/{y}" for y in [now.year, now.year - 1] for m in range(12, 0, -1)]

        self.cb_month = ctk.CTkComboBox(
            header, values=months, width=160, state="readonly",
            command=self.on_month_change
        )
        self.cb_month.set(f"Tháng {now.month}/{now.year}")
        self.cb_month.pack(side="right")

        # === THANH CÔNG CỤ (TÌM KIẾM + BUTTONS) ===
        toolbar = ctk.CTkFrame(container, fg_color="#f5f5f5", border_width=1, border_color="#ccc")
        toolbar.pack(fill="x", pady=(0, 15))

        inner_tool = ctk.CTkFrame(toolbar, fg_color="transparent")
        inner_tool.pack(padx=10, pady=10, fill="x")

        # 1. Tìm kiếm
        ctk.CTkLabel(inner_tool, text="Tìm kiếm:", font=("Arial", 12, "bold"), text_color="#555").pack(side="left",
                                                                                                       padx=(0, 5))
        self.entry_search = ctk.CTkEntry(inner_tool, width=200, placeholder_text="Nhập tên hoặc mã NV...")
        self.entry_search.pack(side="left", padx=(0, 5))

        ctk.CTkButton(inner_tool, text="🔍 Tìm", width=60, height=30, fg_color="#2196F3", hover_color="#1976D2",
                      command=self.search_data).pack(side="left", padx=(0, 20))

        # 2. Các nút chức năng
        # Nút Thanh Toán (Nổi bật)
        ctk.CTkButton(inner_tool, text="💰 Xác nhận Thanh Toán", width=160, height=35,
                      fg_color="#4CAF50", hover_color="#388E3C", font=("Arial", 12, "bold"),
                      command=self.thanh_toan).pack(side="left", padx=5)

        # Nút Xuất Excel
        ctk.CTkButton(inner_tool, text="📊 Xuất Excel", width=120, height=35,
                      fg_color="#009688", hover_color="#00796B",
                      command=self.xuat_excel).pack(side="left", padx=5)

        # Nút Tải lại
        ctk.CTkButton(inner_tool, text="🔃 Tải lại", width=80, height=35,
                      fg_color="#9E9E9E", hover_color="#757575",
                      command=self.reload_data).pack(side="right", padx=5)

        # === BẢNG DỮ LIỆU ===
        table_frame = ctk.CTkFrame(container, fg_color="white")
        table_frame.pack(fill="both", expand=True)

        columns = ("stt", "manv", "hoten", "chucvu", "luongcb", "tonggio", "thuclanh", "trangthai")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)

        self.tree.heading("stt", text="STT")
        self.tree.heading("manv", text="Mã NV")
        self.tree.heading("hoten", text="Họ tên")
        self.tree.heading("chucvu", text="Chức vụ")
        self.tree.heading("luongcb", text="Lương CB/h")
        self.tree.heading("tonggio", text="Tổng giờ")
        self.tree.heading("thuclanh", text="Thực lãnh (VNĐ)")
        self.tree.heading("trangthai", text="Trạng thái")

        # Căn chỉnh cột
        self.tree.column("stt", width=50, anchor="center")
        self.tree.column("manv", width=80, anchor="center")
        self.tree.column("hoten", width=200)
        self.tree.column("chucvu", width=120)
        self.tree.column("luongcb", width=120, anchor="e")
        self.tree.column("tonggio", width=100, anchor="center")
        self.tree.column("thuclanh", width=150, anchor="e")
        self.tree.column("trangthai", width=150, anchor="center")

        # Tag màu sắc cho trạng thái
        self.tree.tag_configure('chua_tt', background='#FFEBEE', foreground='red')  # Đỏ nhạt
        self.tree.tag_configure('da_tt', background='#E8F5E9', foreground='green')  # Xanh nhạt

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.tree.pack(fill="both", expand=True)

        self.tree.bind("<<TreeviewSelect>>", self.on_select_row)

    # ================= LOGIC =================
    def load_data(self, data_input=None):
        # Xóa bảng cũ
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Nếu không có data đầu vào (từ tìm kiếm), thì load từ Controller
        if data_input is None:
            month_str = self.cb_month.get()
            self.current_list = self.controller.get_list_salary(month_str)
        else:
            self.current_list = data_input

        if not self.current_list:
            return

        for idx, row in enumerate(self.current_list):
            is_paid = (row['trangThai'] == 'DaThanhToan')
            status_text = "Đã thanh toán" if is_paid else "Chưa thanh toán"
            tag = "da_tt" if is_paid else "chua_tt"

            luong_cb = "{:,.0f}".format(float(row['luongCoBan']))
            thuc_lanh = "{:,.0f}".format(float(row['thucLanh']))

            self.tree.insert("", "end", values=(
                idx + 1,
                row['idNhanVien'],
                row['hoTen'],
                row['tenChucVu'],
                luong_cb,
                row['tongGioLamThang'],
                thuc_lanh,
                status_text
            ), tags=(tag,))

    def on_select_row(self, event):
        selected = self.tree.selection()
        if selected:
            idx = self.tree.index(selected[0])
            if idx < len(self.current_list):
                data = self.current_list[idx]
                self.selected_id = data['idNhanVien']
                self.selected_name = data['hoTen']
                self.selected_status = data['trangThai']  # Lưu trạng thái để check khi bấm nút

    def on_month_change(self, value):
        self.reload_data()

    def reload_data(self):
        self.entry_search.delete(0, "end")  # Xóa ô tìm kiếm
        self.selected_id = None
        self.load_data()

    # --- CHỨC NĂNG TÌM KIẾM ---
    def search_data(self):
        keyword = self.entry_search.get().lower()
        if not keyword:
            self.reload_data()
            return

        # Lấy dữ liệu gốc của tháng hiện tại
        month_str = self.cb_month.get()
        full_data = self.controller.get_list_salary(month_str)

        # Lọc dữ liệu trong Python (Client-side filtering)
        filtered_list = []
        for item in full_data:
            # Tìm theo Tên hoặc Mã NV
            if keyword in item['hoTen'].lower() or keyword in str(item['idNhanVien']):
                filtered_list.append(item)

        self.load_data(filtered_list)

    # --- CHỨC NĂNG THANH TOÁN ---
    def thanh_toan(self):
        if not self.selected_id:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn nhân viên trong danh sách!")
            return

        if self.selected_status == 'DaThanhToan':
            messagebox.showinfo("Thông báo", f"Lương của {self.selected_name} đã được thanh toán rồi!")
            return

        if messagebox.askyesno("Xác nhận", f"Xác nhận thanh toán lương tháng này cho:\n{self.selected_name}?"):
            ok, msg = self.controller.thanh_toan_luong(self.selected_id, self.cb_month.get())
            if ok:
                messagebox.showinfo("Thành công", msg)
                self.reload_data()  # Load lại bảng để cập nhật màu sắc
            else:
                messagebox.showerror("Lỗi", msg)

    # --- CHỨC NĂNG XUẤT EXCEL ---
    def xuat_excel(self):
        if not self.current_list:
            messagebox.showwarning("Cảnh báo", "Không có dữ liệu để xuất!")
            return

        month_str = self.cb_month.get().replace('/', '_').replace(' ', '')
        default_name = f"Bang_Luong_{month_str}.xlsx"

        file_path = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel Files", "*.xlsx")],
            initialfile=default_name,
            title="Lưu Bảng Lương"
        )

        if file_path:
            ok, msg = self.controller.export_excel(self.cb_month.get(), file_path)
            if ok:
                messagebox.showinfo("Thành công", msg)
            else:
                messagebox.showerror("Lỗi", msg)