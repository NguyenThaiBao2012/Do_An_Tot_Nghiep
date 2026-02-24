import customtkinter as ctk
from tkinter import ttk, messagebox, filedialog
import tkinter as tk
from datetime import datetime
from PIL import Image, ImageTk
from src.Controller.DiemDanhController import DiemDanhController


class DiemDanhPage(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="white")

        self.controller = DiemDanhController()

        self.selected_id = None
        self.selected_name = None

        self.current_cam_image = None
        self.cam_window = None

        # Biến lưu index camera hiện tại (mặc định 0)
        self.current_cam_index = 0

        self.tao_main_content()
        self.load_table_data()
        self.load_log_data()

    def tao_main_content(self):
        # Chia lưới: 7 phần trái (Danh sách), 3 phần phải (Log)
        self.grid_columnconfigure(0, weight=7)
        self.grid_columnconfigure(1, weight=3)
        self.grid_rowconfigure(0, weight=1)

        # =================================================================
        # KHUNG TRÁI: DANH SÁCH NHÂN VIÊN & CHỨC NĂNG
        # =================================================================
        left_frame = ctk.CTkFrame(self, fg_color="white")
        left_frame.grid(row=0, column=0, sticky="nsew", padx=(10, 5), pady=10)

        ctk.CTkLabel(left_frame, text="Quản Lý Điểm Danh", font=("Arial", 18, "bold"), text_color="#333").pack(
            anchor="w", pady=(0, 10))

        # --- Hàng Nút Chức Năng ---
        btn_box = ctk.CTkFrame(left_frame, fg_color="transparent")
        btn_box.pack(fill="x", pady=(0, 10))

        ctk.CTkButton(btn_box, text="📸 Đăng ký Face", fg_color="#FF9800", hover_color="#F57C00",
                      width=110, height=35, command=self.open_capture_window).pack(side="left", padx=5)

        # [MỚI] Nút Xóa Face
        ctk.CTkButton(btn_box, text="🗑️ Xóa Face", fg_color="#F44336", hover_color="#D32F2F",
                      width=100, height=35, command=self.xoa_face).pack(side="left", padx=5)

        ctk.CTkButton(btn_box, text="✅ Điểm danh", fg_color="#2196F3", hover_color="#1976D2",
                      width=120, height=35, command=self.open_attendance_window).pack(side="left", padx=5)

        ctk.CTkButton(btn_box, text="🔃 Tải lại", fg_color="#9E9E9E", hover_color="#757575",
                      width=80, height=35, command=self.reload_all).pack(side="left", padx=5)

        ctk.CTkButton(btn_box, text="📊 Excel", fg_color="#009688", hover_color="#00796B",
                      width=80, height=35, command=self.export_excel).pack(side="right", padx=5)

        # --- Bảng Danh Sách ---
        table_frame = ctk.CTkFrame(left_frame, fg_color="white")
        table_frame.pack(fill="both", expand=True)

        cols = ("id", "ten", "chucvu", "face_status", "gio_vao", "gio_ra", "trangthai_chamcong")
        self.tree = ttk.Treeview(table_frame, columns=cols, show="headings", height=15)

        self.tree.heading("id", text="ID");
        self.tree.heading("ten", text="Họ Tên")
        self.tree.heading("chucvu", text="Chức Vụ");
        self.tree.heading("face_status", text="Dữ liệu Face")
        self.tree.heading("gio_vao", text="Giờ Vào");
        self.tree.heading("gio_ra", text="Giờ Ra")
        self.tree.heading("trangthai_chamcong", text="Trạng Thái")

        self.tree.column("id", width=40, anchor="center");
        self.tree.column("ten", width=180)
        self.tree.column("chucvu", width=100);
        self.tree.column("face_status", width=100, anchor="center")
        self.tree.column("gio_vao", width=80, anchor="center");
        self.tree.column("gio_ra", width=80, anchor="center")
        self.tree.column("trangthai_chamcong", width=120, anchor="center")

        # Cấu hình màu sắc
        self.tree.tag_configure('chua_vao', background='#FFEBEE')  # Đỏ nhạt
        self.tree.tag_configure('dang_lam', background='#FFFDE7')  # Vàng nhạt
        self.tree.tag_configure('da_ve', background='#E8F5E9')  # Xanh nhạt

        self.tree.pack(fill="both", expand=True)
        self.tree.bind("<<TreeviewSelect>>", self.on_select_row)

        # =================================================================
        # KHUNG PHẢI: NHẬT KÝ & BỘ LỌC
        # =================================================================
        right_frame = ctk.CTkFrame(self, fg_color="#f5f5f5", border_width=1, border_color="#ccc")
        right_frame.grid(row=0, column=1, sticky="nsew", padx=(5, 10), pady=10)

        ctk.CTkLabel(right_frame, text="NHẬT KÝ HOẠT ĐỘNG", font=("Arial", 14, "bold"), text_color="#555").pack(
            pady=(10, 5))

        # --- Bộ Lọc ---
        filter_box = ctk.CTkFrame(right_frame, fg_color="transparent")
        filter_box.pack(fill="x", padx=5, pady=5)

        days = ["Tất cả"] + [str(i) for i in range(1, 32)]
        self.cb_day = ctk.CTkComboBox(filter_box, values=days, width=65, state="readonly")
        self.cb_day.pack(side="left", padx=2)

        months = ["Tất cả"] + [str(i) for i in range(1, 13)]
        self.cb_month = ctk.CTkComboBox(filter_box, values=months, width=65, state="readonly")
        self.cb_month.pack(side="left", padx=2)

        self.entry_year = ctk.CTkEntry(filter_box, width=50, placeholder_text="Năm")
        self.entry_year.pack(side="left", padx=2)

        now = datetime.now()
        self.cb_day.set(str(now.day))
        self.cb_month.set(str(now.month))
        self.entry_year.insert(0, str(now.year))

        ctk.CTkButton(filter_box, text="Lọc", width=50, height=28, command=self.filter_logs).pack(side="left", padx=2)

        # --- Bảng Log ---
        self.log_tree = ttk.Treeview(right_frame, columns=("time", "content"), show="headings", height=20)
        self.log_tree.heading("time", text="Thời gian")
        self.log_tree.heading("content", text="Nội dung")
        self.log_tree.column("time", width=100, anchor="center")
        self.log_tree.column("content", width=180)
        self.log_tree.pack(fill="both", expand=True, padx=5, pady=5)

    # ================= LOGIC LOAD DỮ LIỆU =================

    def reload_all(self):
        self.load_table_data()
        self.filter_logs()
        messagebox.showinfo("Thông báo", "Đã tải lại dữ liệu mới nhất!")

    def load_table_data(self):
        # Xóa dữ liệu cũ
        for i in self.tree.get_children(): self.tree.delete(i)

        employees = self.controller.get_list_nv_sorted()
        for emp in employees:
            status_code = emp['trangThai']
            tag = 'chua_vao'
            status_text = "Chưa vào"

            if status_code == 1:
                tag = 'dang_lam'; status_text = "Đang làm"
            elif status_code == 2:
                tag = 'da_ve'; status_text = "Đã về"

            # Check dữ liệu Face
            has_face = self.controller.check_face_data_exists(emp['idNhanVien'])
            face_text = "Đã có" if has_face else "Chưa có"

            # Format giờ hiển thị
            gv = emp['gioVao'].strftime("%H:%M") if emp['gioVao'] else ""
            gr = emp['gioRa'].strftime("%H:%M") if emp['gioRa'] else ""

            self.tree.insert("", "end", values=(
                emp['idNhanVien'], emp['hoTen'], emp['tenChucVu'],
                face_text, gv, gr, status_text
            ), tags=(tag,))

    def filter_logs(self):
        d = self.cb_day.get()
        m = self.cb_month.get()
        y = self.entry_year.get()

        for i in self.log_tree.get_children(): self.log_tree.delete(i)

        logs = self.controller.filter_logs_by_date(d, m, y)
        if not logs and d != "Tất cả":
            self.log_tree.insert("", "end", values=("---", "Không có dữ liệu"))
            return

        for log in logs:
            time_str = log['gioVao'].strftime("%d/%m %H:%M")
            action = f"{log['hoTen']} (Vào)"
            self.log_tree.insert("", "end", values=(time_str, action))

            if log['gioRa']:
                time_out = log['gioRa'].strftime("%d/%m %H:%M")
                action_out = f"{log['hoTen']} (Ra)"
                self.log_tree.insert("", "end", values=(time_out, action_out))

    def load_log_data(self):
        self.filter_logs()

    def on_select_row(self, event):
        sel = self.tree.selection()
        if sel:
            item = self.tree.item(sel[0])
            self.selected_id = item['values'][0]
            self.selected_name = item['values'][1]

    def add_log_ui(self, message):
        time_str = datetime.now().strftime("%d/%m %H:%M")
        self.log_tree.insert("", 0, values=(time_str, message))

    def export_excel(self):
        if not self.selected_id:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn nhân viên cần xuất bảng công!")
            return

        now = datetime.now()
        default_name = f"BangCong_{self.selected_name.replace(' ', '_')}_{now.month}_{now.year}.xlsx"

        file_path = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel Files", "*.xlsx"), ("All Files", "*.*")],
            initialfile=default_name,
            title="Lưu Bảng Chấm Công"
        )

        if not file_path: return

        month_year = now.strftime("%m/%Y")
        ok, msg = self.controller.export_excel_individual(self.selected_id, month_year, file_path)

        if ok:
            messagebox.showinfo("Thành công", msg)
        else:
            messagebox.showerror("Lỗi", msg)

    # [MỚI] Hàm xử lý Xóa Khuôn Mặt
    def xoa_face(self):
        if not self.selected_id:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn nhân viên cần xóa dữ liệu Face!")
            return

        if messagebox.askyesno("Xác nhận",
                               f"Bạn có chắc muốn xóa dữ liệu khuôn mặt của:\n{self.selected_name}?\n\nHành động này không thể hoàn tác."):
            ok, msg = self.controller.delete_face_data(self.selected_id)
            if ok:
                messagebox.showinfo("Thành công", msg)
                self.add_log_ui(f"Xóa Face: {self.selected_name}")
                self.load_table_data()  # Load lại bảng để cập nhật trạng thái "Chưa có"
            else:
                messagebox.showerror("Lỗi", msg)

    # ================= LOGIC CAMERA AN TOÀN (ANTI-FLICKER) =================

    # Hàm cập nhật hình ảnh an toàn trên Main Thread
    def _safe_update_image(self, pil_img, status_text):
        if not self.cam_window or not self.cam_window.winfo_exists(): return
        try:
            if pil_img:
                self.current_cam_image = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=(580, 400))
                if self.cam_label.winfo_exists():
                    self.cam_label.configure(image=self.current_cam_image, text="")

            if status_text and self.status_label.winfo_exists():
                self.status_label.configure(text=status_text)
        except Exception:
            pass

    # 1. CỬA SỔ THU THẬP MẪU
    def open_capture_window(self):
        if not self.selected_id:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn nhân viên từ danh sách bên trái!")
            return

        self.cam_window = ctk.CTkToplevel(self)
        self.cam_window.title(f"Thu thập: {self.selected_name}")
        self.cam_window.geometry("600x650")
        self.cam_window.attributes("-topmost", True)

        # Chọn Camera
        cam_frame = ctk.CTkFrame(self.cam_window, fg_color="transparent")
        cam_frame.pack(pady=(10, 0))
        ctk.CTkLabel(cam_frame, text="Chọn Camera:", font=("Arial", 12)).pack(side="left", padx=5)

        available_cams = self.controller.get_available_cameras()
        cam_values = [f"Camera {i}" for i in available_cams]

        self.cb_camera = ctk.CTkComboBox(cam_frame, values=cam_values, state="readonly", width=150,
                                         command=self.on_change_camera_capture)
        self.cb_camera.set(cam_values[0])
        self.cb_camera.pack(side="left", padx=5)
        self.current_cam_index = available_cams[0]

        self.cam_label = ctk.CTkLabel(self.cam_window, text="Khởi động Camera...", width=580, height=400,
                                      fg_color="black")
        self.cam_label.pack(pady=10)
        self.status_label = ctk.CTkLabel(self.cam_window, text="Giữ khuôn mặt trước camera...",
                                         font=("Arial", 16, "bold"))
        self.status_label.pack(pady=5)

        self.btn_frame_cam = ctk.CTkFrame(self.cam_window, fg_color="transparent")
        self.btn_frame_cam.pack(pady=10)
        self.btn_close_cam = ctk.CTkButton(self.btn_frame_cam, text="Đóng", fg_color="red",
                                           command=self.close_cam_window)

        self.start_capture_process(self.current_cam_index)

    def on_change_camera_capture(self, choice):
        new_index = int(choice.split(" ")[1])
        if new_index != self.current_cam_index:
            self.current_cam_index = new_index
            self.controller.stop_camera()
            self.cam_window.after(500, lambda: self.start_capture_process(new_index))

    def start_capture_process(self, cam_idx):
        # Callback trung gian để chuyển luồng về Main Thread bằng self.after
        def ui_callback(pil_img, text, loop=None):
            self.after(0, lambda: self._safe_update_image(pil_img, text))

        def on_finish(msg):
            # Cập nhật GUI kết thúc cũng cần an toàn
            self.after(0, lambda: self._safe_finish_capture(msg))

        self.controller.start_capture(self.selected_id, ui_callback, on_finish, cam_index=cam_idx)

    def _safe_finish_capture(self, msg):
        if not self.cam_window or not self.cam_window.winfo_exists(): return
        try:
            self.current_cam_image = None
            self.cam_label.configure(image=None, text="HOÀN TẤT", fg_color="#333")
            self.status_label.configure(text="✅ " + msg, text_color="green")
            self.btn_close_cam.pack()
            self.add_log_ui(f"Cập nhật Face: {self.selected_name}")
            self.reload_all()
        except:
            pass

    # 2. CỬA SỔ ĐIỂM DANH
    def open_attendance_window(self):
        self.cam_window = ctk.CTkToplevel(self)
        self.cam_window.title("Quét Điểm Danh")
        self.cam_window.geometry("600x650")
        self.cam_window.attributes("-topmost", True)

        # Chọn Camera
        cam_frame = ctk.CTkFrame(self.cam_window, fg_color="transparent")
        cam_frame.pack(pady=(10, 0))
        ctk.CTkLabel(cam_frame, text="Nguồn Camera:", font=("Arial", 12)).pack(side="left", padx=5)

        available_cams = self.controller.get_available_cameras()
        cam_values = [f"Camera {i}" for i in available_cams]

        self.cb_camera = ctk.CTkComboBox(cam_frame, values=cam_values, state="readonly", width=150,
                                         command=self.on_change_camera_attendance)
        self.cb_camera.set(cam_values[0])
        self.cb_camera.pack(side="left", padx=5)
        self.current_cam_index = available_cams[0]

        self.cam_label = ctk.CTkLabel(self.cam_window, text="Đang khởi động...", width=580, height=400,
                                      fg_color="black")
        self.cam_label.pack(pady=10)
        self.status_label = ctk.CTkLabel(self.cam_window, text="Đang quét...", font=("Arial", 16, "bold"))
        self.status_label.pack(pady=5)

        ctk.CTkButton(self.cam_window, text="Dừng & Thoát", fg_color="#F44336", hover_color="#D32F2F",
                      command=self.close_cam_window).pack(pady=10)

        self.start_attendance_process(self.current_cam_index)

    def on_change_camera_attendance(self, choice):
        new_index = int(choice.split(" ")[1])
        if new_index != self.current_cam_index:
            self.current_cam_index = new_index
            self.controller.stop_camera()
            self.cam_window.after(500, lambda: self.start_attendance_process(new_index))

    def start_attendance_process(self, cam_idx):
        def ui_callback(pil_img, text, loop=None):
            self.after(0, lambda: self._safe_update_image(pil_img, text))

        def on_success(name, type_cc, hours):
            self.after(0, lambda: self._safe_success_attendance(name, type_cc, hours))

        ok, msg = self.controller.start_recognition(ui_callback, on_success, cam_index=cam_idx)
        if not ok:
            messagebox.showerror("Lỗi", msg)
            self.cam_window.destroy()

    def _safe_success_attendance(self, name, type_cc, hours):
        if not self.cam_window or not self.cam_window.winfo_exists(): return
        try:
            msg = f"{name}: {type_cc}"
            if hours > 0: msg += f" ({hours}h)"
            self.status_label.configure(text=f"✅ {msg}", text_color="green")
            self.add_log_ui(msg)

            # Reset label sau 2s
            self.after(2000, lambda: self.reset_status_label())
            self.load_table_data()
        except:
            pass

    def reset_status_label(self):
        try:
            if self.cam_window and self.cam_window.winfo_exists():
                self.status_label.configure(text="Đang quét người tiếp theo...", text_color="#333")
        except:
            pass

    def close_cam_window(self):
        self.controller.stop_camera()
        self.current_cam_image = None
        if self.cam_window: self.cam_window.destroy()