import customtkinter as ctk
from tkinter import messagebox, ttk
from src.Controller.TaiKhoanController import TaiKhoanController


class QuanLyTKPage(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="white")

        # Khởi tạo Controller
        self.controller = TaiKhoanController()

        # Biến lưu trạng thái
        self.selected_id = None
        self.selected_has_account = False
        self.current_list = []

        # Xây dựng giao diện
        self.tao_main_content()
        self.load_table_data()

    def tao_main_content(self):
        """Tạo bố cục giao diện"""
        container = ctk.CTkFrame(self, fg_color="white")
        container.pack(fill="both", expand=True, padx=15, pady=15)

        # === 1. TIÊU ĐỀ ===
        ctk.CTkLabel(
            container,
            text="QUẢN LÝ TÀI KHOẢN NHÂN VIÊN",
            font=("Arial", 20, "bold"),
            text_color="#1565C0"
        ).pack(pady=(0, 20))

        # === 2. FORM NHẬP LIỆU ===
        input_group = ctk.CTkFrame(container, fg_color="#F5F5F5", border_width=1, border_color="#DDD")
        input_group.pack(fill="x", padx=10, pady=(0, 20))

        # --- Toolbar (Nút bấm) ---
        toolbar = ctk.CTkFrame(input_group, fg_color="transparent")
        toolbar.pack(fill="x", padx=10, pady=(15, 5))

        btn_center = ctk.CTkFrame(toolbar, fg_color="transparent")
        btn_center.pack(anchor="center")

        self.create_btn(btn_center, "Lưu / Cấp TK", "#4CAF50", "#45a049", self.luu_thong_tin, width=120)
        self.create_btn(btn_center, "Xóa TK", "#F44336", "#D32F2F", self.xoa_tk)
        self.create_btn(btn_center, "Làm mới", "#607D8B", "#455A64", self.lam_moi)

        # Thêm nút Khóa/Mở khóa (Nếu controller hỗ trợ sau này)
        # self.create_btn(btn_center, "Khóa / Mở", "#FF9800", "#F57C00", self.khoa_mo_tk)

        ctk.CTkFrame(input_group, height=1, fg_color="#DDD").pack(fill="x", padx=20, pady=10)

        # --- Các trường nhập liệu ---
        form_container = ctk.CTkFrame(input_group, fg_color="transparent")
        form_container.pack(fill="x", padx=20, pady=(0, 20))

        # Hàng 1: Tên & Email (Readonly - Lấy từ thông tin nhân viên)
        row1 = ctk.CTkFrame(form_container, fg_color="transparent")
        row1.pack(fill="x", pady=5)

        self.entry_name = self.create_input(row1, "Họ và tên:", 250)
        self.entry_name.configure(state="readonly", fg_color="#E0E0E0")  # Xám nhẹ để biết không sửa được

        self.entry_email = self.create_input(row1, "Email:", 250)
        self.entry_email.configure(state="readonly", fg_color="#E0E0E0")

        # Hàng 2: Username & Password
        row2 = ctk.CTkFrame(form_container, fg_color="transparent")
        row2.pack(fill="x", pady=5)

        self.entry_user = self.create_input(row2, "Tên đăng nhập:", 250)

        # Frame chứa Mật khẩu + Nút ẩn hiện
        f_pass = ctk.CTkFrame(row2, fg_color="transparent")
        f_pass.pack(side="left", padx=10)
        ctk.CTkLabel(f_pass, text="Mật khẩu:", font=("Arial", 12, "bold"), text_color="#555").pack(anchor="w")

        f_pass_inner = ctk.CTkFrame(f_pass, fg_color="transparent")
        f_pass_inner.pack()

        self.entry_pass = ctk.CTkEntry(f_pass_inner, width=210, height=32, show="*", border_color="#ccc")
        self.entry_pass.pack(side="left")

        self.btn_eye = ctk.CTkButton(f_pass_inner, text="👁", width=35, height=32,
                                     fg_color="#DDD", text_color="#333", hover_color="#CCC",
                                     command=self.toggle_pass)
        self.btn_eye.pack(side="left", padx=(5, 0))

        # Hàng 3: Vai trò (Combobox)
        row3 = ctk.CTkFrame(form_container, fg_color="transparent")
        row3.pack(fill="x", pady=5)

        f_role = ctk.CTkFrame(row3, fg_color="transparent")
        f_role.pack(side="left", padx=10)
        ctk.CTkLabel(f_role, text="Chức vụ / Vai trò:", font=("Arial", 12, "bold"), text_color="#555").pack(anchor="w")

        # Danh sách chức vụ (Cần khớp với DB)
        roles = ["Quản Lý Cửa Hàng", "Pha Chế Trưởng", "Pha Chế Viên", "Phục Vụ", "Thu Ngân", "Bảo Vệ"]
        self.combo_role = ctk.CTkComboBox(f_role, values=roles, width=250, height=32, state="readonly")
        self.combo_role.set("Chọn chức vụ")
        self.combo_role.pack()

        # === 3. DANH SÁCH (TREEVIEW) ===
        ctk.CTkLabel(container, text="DANH SÁCH NHÂN SỰ", font=("Arial", 14, "bold"), text_color="#333").pack(
            anchor="w", padx=10, pady=(10, 5))

        list_frame = ctk.CTkFrame(container, fg_color="white", border_width=1, border_color="#999")
        list_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        # Cấu hình bảng
        columns = ("stt", "name", "user", "email", "role", "status")
        self.tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=10)

        # Định nghĩa tiêu đề
        self.tree.heading("stt", text="STT")
        self.tree.heading("name", text="Họ và Tên")
        self.tree.heading("user", text="Tên Đăng Nhập")
        self.tree.heading("email", text="Email")
        self.tree.heading("role", text="Chức Vụ")
        self.tree.heading("status", text="Trạng Thái")

        # Định nghĩa cột
        self.tree.column("stt", width=50, anchor="center")
        self.tree.column("name", width=200)
        self.tree.column("user", width=150)
        self.tree.column("email", width=200)
        self.tree.column("role", width=150)
        self.tree.column("status", width=120, anchor="center")

        # Cấu hình màu sắc cho các dòng (Tags)
        self.tree.tag_configure('active', foreground='green')  # Hoạt động
        self.tree.tag_configure('locked', foreground='red')  # Bị khóa
        self.tree.tag_configure('none', foreground='gray')  # Chưa có TK

        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.tree.pack(fill="both", expand=True)

        # Sự kiện click
        self.tree.bind("<<TreeviewSelect>>", self.on_select_row)

    # ================= CÁC HÀM HỖ TRỢ (HELPERS) =================
    def create_btn(self, parent, text, color, hover, cmd, width=100):
        ctk.CTkButton(parent, text=text, fg_color=color, hover_color=hover,
                      width=width, height=35, font=("Arial", 12, "bold"),
                      command=cmd).pack(side="left", padx=5)

    def create_input(self, parent, label, width):
        f = ctk.CTkFrame(parent, fg_color="transparent")
        f.pack(side="left", padx=10)
        ctk.CTkLabel(f, text=label, font=("Arial", 12, "bold"), text_color="#555").pack(anchor="w")
        e = ctk.CTkEntry(f, width=width, height=32, border_color="#ccc")
        e.pack()
        return e

    def toggle_pass(self):
        if self.entry_pass.cget('show') == '*':
            self.entry_pass.configure(show='')
            self.btn_eye.configure(text="🔒")
        else:
            self.entry_pass.configure(show='*')
            self.btn_eye.configure(text="👁")

    # ================= LOGIC XỬ LÝ DỮ LIỆU =================
    def load_table_data(self):
        """Tải dữ liệu từ Controller và hiển thị lên bảng"""
        # Xóa dữ liệu cũ
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Lấy danh sách mới
        self.current_list = self.controller.get_list()

        for idx, item in enumerate(self.current_list):
            has_acc = item['tenDangNhap'] is not None

            # [LOGIC MỚI] Xử lý hiển thị trạng thái dựa trên cột 'trangThai'
            if not has_acc:
                status_text = "Chưa có TK"
                tag = 'none'
            else:
                # Kiểm tra cột trangThai từ DB (1: Active, 0: Locked)
                # Sử dụng .get() để tránh lỗi nếu key không tồn tại
                trang_thai = item.get('trangThai')

                if trang_thai == 1:
                    status_text = "Hoạt động"
                    tag = 'active'
                elif trang_thai == 0:
                    status_text = "Đã Khóa"
                    tag = 'locked'
                else:
                    # Trường hợp dữ liệu cũ hoặc null, mặc định coi là Hoạt động
                    status_text = "Hoạt động"
                    tag = 'active'

            user_display = item['tenDangNhap'] if has_acc else ""

            self.tree.insert("", "end", values=(
                idx + 1,
                item['hoTen'],
                user_display,
                item['email'],
                item['tenChucVu'],
                status_text
            ), tags=(tag,))

    def on_select_row(self, event):
        """Xử lý khi click chọn 1 dòng"""
        selected = self.tree.selection()
        if selected:
            index = self.tree.index(selected[0])
            # Đảm bảo index nằm trong phạm vi danh sách
            if index < len(self.current_list):
                data = self.current_list[index]
                self.selected_id = data['idNhanVien']
                self.selected_has_account = (data['tenDangNhap'] is not None)

                # Đổ dữ liệu Readonly
                self.entry_name.configure(state="normal")
                self.entry_name.delete(0, "end")
                self.entry_name.insert(0, data['hoTen'])
                self.entry_name.configure(state="readonly")

                self.entry_email.configure(state="normal")
                self.entry_email.delete(0, "end")
                self.entry_email.insert(0, data['email'])
                self.entry_email.configure(state="readonly")

                self.combo_role.set(data['tenChucVu'])

                # Đổ dữ liệu Username/Pass
                self.entry_user.delete(0, "end")
                self.entry_pass.delete(0, "end")

                if self.selected_has_account:
                    self.entry_user.insert(0, data['tenDangNhap'])
                    # Không hiển thị mật khẩu thật (Hash), chỉ hiện placeholder
                    self.entry_pass.configure(placeholder_text="(Đã có mật khẩu - Nhập mới để đổi)")
                else:
                    self.entry_pass.configure(placeholder_text="Nhập mật khẩu để cấp TK")

    def luu_thong_tin(self):
        """Lưu hoặc Cấp tài khoản mới"""
        if not self.selected_id:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn nhân viên từ danh sách!")
            return

        name = self.entry_name.get()
        user = self.entry_user.get()
        pwd = self.entry_pass.get()
        email = self.entry_email.get()
        role = self.combo_role.get()

        # Gọi Controller xử lý
        success, msg = self.controller.save_account(
            self.selected_id, self.selected_has_account,
            name, user, pwd, email, role
        )

        if success:
            messagebox.showinfo("Thành công", msg)
            self.lam_moi()  # Reset form và load lại bảng
        else:
            messagebox.showerror("Lỗi", msg)

    def xoa_tk(self):
        """Xóa tài khoản đăng nhập"""
        if not self.selected_id:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn dòng cần xóa!")
            return

        if not self.selected_has_account:
            messagebox.showinfo("Thông báo", "Nhân viên này chưa có tài khoản để xóa!")
            return

        if messagebox.askyesno("Xác nhận",
                               "Bạn có chắc muốn xóa tài khoản đăng nhập của nhân viên này?\n(Thông tin nhân viên vẫn được giữ lại)"):
            success, msg = self.controller.delete_account_only(self.selected_id)
            if success:
                messagebox.showinfo("Thành công", msg)
                self.lam_moi()
            else:
                messagebox.showerror("Lỗi", msg)

    def lam_moi(self):
        """Reset form và tải lại dữ liệu"""
        self.selected_id = None
        self.selected_has_account = False

        # Xóa các ô nhập liệu
        self.entry_name.configure(state="normal")
        self.entry_name.delete(0, "end")
        self.entry_name.configure(state="readonly")  # Reset về readonly rỗng hoặc để normal tùy ý

        self.entry_email.configure(state="normal")
        self.entry_email.delete(0, "end")
        self.entry_email.configure(state="readonly")

        self.entry_user.delete(0, "end")
        self.entry_pass.delete(0, "end")
        self.combo_role.set("Chọn chức vụ")
        self.entry_pass.configure(placeholder_text="")

        # Tải lại bảng
        self.load_table_data()