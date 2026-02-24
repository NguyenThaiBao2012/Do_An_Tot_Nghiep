import customtkinter as ctk
from tkinter import messagebox


class Sidebar(ctk.CTkFrame):
    def __init__(self, master, username, on_change_page_command):
        # Tăng width lên 240 để chữ to không bị chật
        super().__init__(master, width=240, fg_color="#e8f0f8")
        self.username = username
        self.on_change_page_command = on_change_page_command
        self.buttons = {}

        # Ngăn frame tự co lại theo nội dung con
        self.pack_propagate(False)
        self.setup_ui()

    def setup_ui(self):
        # ================== 1. HEADER (LOGO & AVATAR) ==================
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", pady=(25, 15))

        # Welcome Text
        ctk.CTkLabel(header_frame, text="", font=("Arial", 20, "bold"), text_color="#1565C0").pack()

        # Avatar Frame (Tròn, nổi bật)
        avatar_container = ctk.CTkFrame(header_frame, fg_color="white", width=90, height=90, corner_radius=45,
                                        border_width=3, border_color="#BBDEFB")
        avatar_container.pack(pady=(10, 5))
        avatar_container.pack_propagate(False)

        # Avatar Icon (Căn giữa tuyệt đối trong khung tròn)
        avatar_label = ctk.CTkLabel(avatar_container, text="👤", font=("Arial", 45))
        avatar_label.place(relx=0.5, rely=0.5, anchor="center")

        # Username
        user_label = ctk.CTkLabel(header_frame, text=self.username.upper(), font=("Arial", 16, "bold"),
                                  text_color="#333")
        user_label.pack(pady=(5, 0))

        # Sự kiện click Avatar đổi trang
        def on_avatar_click(event):
            self.clear_active_button()
            self.after(10, lambda: self.on_change_page_command("TaiKhoan"))

        for w in [avatar_container, avatar_label, user_label]:
            w.bind("<Button-1>", on_avatar_click)
            w.configure(cursor="hand2")

        # ================== 3. FOOTER (ĐĂNG XUẤT) ==================
        # Đặt side="bottom" để luôn nằm dưới cùng
        logout_frame = ctk.CTkFrame(self, fg_color="transparent")
        logout_frame.pack(side="bottom", fill="x", padx=15, pady=25)

        ctk.CTkButton(
            logout_frame,
            text="⏻   ĐĂNG XUẤT",
            fg_color="#ffebee",  # Nền đỏ rất nhạt
            text_color="#d32f2f",  # Chữ đỏ đậm
            hover_color="#ffcdd2",  # Hover đỏ nhạt hơn
            border_width=1,
            border_color="#ef5350",
            height=45,  # Nút cao
            corner_radius=8,
            font=("Arial", 14, "bold"),
            anchor="center",  # Căn giữa chữ
            command=self.handle_logout
        ).pack(fill="x")

        # ================== 2. MENU LIST (SCROLLABLE) ==================
        # Frame cuộn chứa các nút menu
        self.menu_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.menu_frame.pack(fill="both", expand=True, padx=10, pady=5)

        # Danh sách module
        # Lưu ý: Các icon/emoji nên có khoảng cách đồng đều với chữ
        menu_items = [
            ("🏠 Trang chủ", "menu"),
            ("👥 Khách hàng", "Khach_Hang"),
            ("📦 Kho hàng", "QL_Kho"),
            ("🏷️ Sản phẩm", "QL_SP"),
            ("✅ Điểm danh", "QL_DD"),
            ("📜 Hóa đơn", "QL_HD"),
            ("🔑 Tài khoản", "QL_TK"),
            ("🏭 Nhà cung cấp", "QL_NCC"),
            ("🪪 Nhân viên", "QL_NV"),
            ("📊 Thống kê", "QL_ThongKe"),
            ("🏦 Ngân hàng", "Ngan_hang"),
            ("💰 Lương", "Luong"),
        ]

        for text, key in menu_items:
            self.create_menu_button(text, key)

    def create_menu_button(self, text, key):
        # Tạo nút menu
        btn = ctk.CTkButton(
            self.menu_frame,
            text=text,
            fg_color="white",  # Nền trắng sạch
            text_color="#37474F",  # Chữ xám đậm dễ đọc
            hover_color="#E3F2FD",  # Hover xanh nhạt
            height=45,  # Chiều cao nút lớn
            corner_radius=8,  # Bo góc nhẹ
            font=("Arial", 14, "normal"),

            # --- QUAN TRỌNG: CĂN GIỮA ---
            anchor="center",  # Căn giữa nội dung trong nút
            width=200,  # Độ rộng cố định (gần bằng sidebar trừ padding)

            command=lambda k=key: self.handle_click(k)
        )
        # Pack với fill="x" để nút dãn ra đẹp mắt
        btn.pack(pady=5, padx=5, fill="x")
        self.buttons[key] = btn

    def handle_click(self, key):
        # Reset màu tất cả
        for k, btn in self.buttons.items():
            if k == key:
                # Style Active: Nổi bật
                btn.configure(
                    fg_color="#2196F3",  # Xanh dương Brand
                    text_color="white",
                    font=("Arial", 14, "bold")
                )
            else:
                # Style Normal
                btn.configure(
                    fg_color="white",
                    text_color="#37474F",
                    font=("Arial", 14, "normal")
                )

        self.update_idletasks()
        # Chuyển trang
        self.after(10, lambda: self.on_change_page_command(key))

    def handle_logout(self):
        if messagebox.askyesno("Đăng xuất", "Bạn có chắc chắn muốn đăng xuất?"):
            self.master.winfo_toplevel().destroy()

    def clear_active_button(self):
        """Reset màu về mặc định khi click Avatar"""
        for k, btn in self.buttons.items():
            btn.configure(fg_color="white", text_color="#37474F", font=("Arial", 14, "normal"))
        self.update_idletasks()