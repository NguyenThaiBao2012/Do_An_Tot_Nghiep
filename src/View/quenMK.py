import customtkinter as ctk
from tkinter import messagebox
from PIL import Image, ImageTk
import os
import sys

# Ép giao diện luôn ở chế độ Sáng để tránh bị chói/đen entry
ctk.set_appearance_mode("Light")
ctk.set_default_color_theme("blue")

try:
    from src.Controller.QuenMKController import QuenMKController
except ImportError:
    # Để code không crash nếu chưa có Controller thật khi test
    class QuenMKController:
        pass


class ForgotPasswordPage(ctk.CTkFrame):
    def __init__(self, parent, on_back_command):
        super().__init__(parent)
        self.on_back_command = on_back_command
        self.controller = QuenMKController()

        # --- 1. THÊM ẢNH NỀN ---
        # Thay "src/images/background.jpg" bằng file của bạn
        path_bg = os.path.join("src/images/anh_nen.jpg")
        try:
            original_image = Image.open(path_bg)
            self.bg_image = ctk.CTkImage(light_image=original_image,
                                         dark_image=original_image,
                                         size=(1000, 600))
            self.bg_label = ctk.CTkLabel(self, image=self.bg_image, text="")
            self.bg_label.place(relx=0, rely=0, relwidth=1, relheight=1)
        except:
            self.configure(fg_color="white")
            print("Cảnh báo: Không tìm thấy ảnh nền tại:", path_bg)

        # --- 2. KHUNG CHÍNH (CENTER FRAME) ---
        self.center_frame = ctk.CTkFrame(self, width=400, height=450, fg_color="#f5f5f5",
                                         corner_radius=15, border_width=1, border_color="#ddd")
        self.center_frame.place(relx=0.5, rely=0.5, anchor="center")
        self.center_frame.pack_propagate(False)  # Giữ nguyên kích thước khung

        # Bắt đầu ở bước 1
        self.step_1_input_info()

    # ================= BƯỚC 1: NHẬP THÔNG TIN =================
    def step_1_input_info(self):
        self.clear_frame()
        ctk.CTkLabel(self.center_frame, text="QUÊN MẬT KHẨU", font=("Arial", 20, "bold"), text_color="#1a237e").pack(
            pady=(40, 10))
        ctk.CTkLabel(self.center_frame, text="Nhập tài khoản và email để nhận mã OTP", font=("Arial", 12),
                     text_color="gray").pack(pady=(0, 25))

        self.entry_user = self.create_entry("🧑", "Tài khoản")
        self.entry_email = self.create_entry("📧", "Email")

        self.create_nav_buttons(self.xu_ly_gui_otp, "Gửi Mã OTP")

    def xu_ly_gui_otp(self):
        user = self.entry_user.get()
        email = self.entry_email.get()
        if not user or not email:
            messagebox.showwarning("Thiếu thông tin", "Vui lòng nhập đầy đủ!")
            return

        self.configure(cursor="watch")
        self.update()

        # Kiểm tra nếu controller có hàm này (phòng trường hợp dùng Mock)
        if hasattr(self.controller, 'gui_ma_xac_nhan'):
            success, msg = self.controller.gui_ma_xac_nhan(user, email)
        else:
            success, msg = False, "Controller chưa được cài đặt"

        self.configure(cursor="")
        if success:
            messagebox.showinfo("Đã gửi", msg)
            self.step_2_verify_otp(email)
        else:
            messagebox.showerror("Lỗi", msg)

    # ================= BƯỚC 2: NHẬP MÃ OTP =================
    def step_2_verify_otp(self, email):
        self.clear_frame()
        ctk.CTkLabel(self.center_frame, text="XÁC THỰC OTP", font=("Arial", 20, "bold"), text_color="#1a237e").pack(
            pady=(40, 10))
        ctk.CTkLabel(self.center_frame, text=f"Mã đã gửi đến: {email}", font=("Arial", 12), text_color="gray").pack(
            pady=(0, 25))

        self.entry_otp = self.create_entry("🔑", "Nhập mã 6 số")

        btn_frame = ctk.CTkFrame(self.center_frame, fg_color="transparent")
        btn_frame.pack(pady=25)
        ctk.CTkButton(btn_frame, text="Xác nhận", width=120, height=35, command=self.xu_ly_xac_thuc).pack(side="left",
                                                                                                          padx=5)
        ctk.CTkButton(btn_frame, text="Gửi lại", width=80, height=35, fg_color="#FF9800", hover_color="#e68a00",
                      command=self.step_1_input_info).pack(side="left", padx=5)

    def xu_ly_xac_thuc(self):
        otp = self.entry_otp.get()
        success, msg = self.controller.xac_thuc_otp(otp)
        if success:
            self.step_3_reset_pass()
        else:
            messagebox.showerror("Sai mã", msg)

    # ================= BƯỚC 3: ĐỔI MẬT KHẨU MỚI =================
    def step_3_reset_pass(self):
        self.clear_frame()
        ctk.CTkLabel(self.center_frame, text="ĐẶT MẬT KHẨU MỚI", font=("Arial", 20, "bold"), text_color="#4CAF50").pack(
            pady=(40, 25))

        self.entry_new = self.create_entry("🔒", "Mật khẩu mới", is_pass=True)
        self.entry_confirm = self.create_entry("🔒", "Nhập lại mật khẩu", is_pass=True)

        ctk.CTkButton(self.center_frame, text="Đổi Mật Khẩu", width=220, height=40, fg_color="#4CAF50",
                      hover_color="#45a049",
                      command=self.xu_ly_doi_mk).pack(pady=30)

    def xu_ly_doi_mk(self):
        new_p = self.entry_new.get()
        conf_p = self.entry_confirm.get()
        success, msg = self.controller.luu_mat_khau_moi(new_p, conf_p)
        if success:
            messagebox.showinfo("Thành công", msg)
            self.on_back_command()
        else:
            messagebox.showerror("Lỗi", msg)

    # ================= HELPERS =================
    def clear_frame(self):
        for widget in self.center_frame.winfo_children():
            widget.destroy()

    def create_entry(self, icon, placeholder, is_pass=False):
        f = ctk.CTkFrame(self.center_frame, fg_color="white", border_width=1, border_color="#ccc")
        f.pack(pady=10, padx=40, fill="x")

        ctk.CTkLabel(f, text=icon, width=40, font=("Arial", 16)).pack(side="left", padx=5)

        e = ctk.CTkEntry(f, placeholder_text=placeholder, border_width=0,
                         fg_color="transparent", height=38, text_color="black")
        e.pack(side="left", fill="x", expand=True)

        if is_pass: e.configure(show="*")
        return e

    def create_nav_buttons(self, next_cmd, next_text):
        f = ctk.CTkFrame(self.center_frame, fg_color="transparent")
        f.pack(pady=30)
        ctk.CTkButton(f, text=next_text, width=140, height=35, command=next_cmd).pack(side="left", padx=8)
        ctk.CTkButton(f, text="Hủy", width=80, height=35, fg_color="#757575", hover_color="#616161",
                      command=self.on_back_command).pack(side="left", padx=8)


# --- [ĐOẠN CODE TEST GIAO DIỆN] ---
if __name__ == "__main__":
    current_path = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(current_path))
    os.chdir(project_root)
    sys.path.append(project_root)

    root = ctk.CTk()
    root.geometry("1000x600")
    root.title("Test Giao Diện Quên Mật Khẩu")


    def test_back():
        print("Quay lại màn hình đăng nhập thành công")


    class MockController:
        def gui_ma_xac_nhan(self, user, email): return True, "Mã OTP đã gửi đến email của bạn!"

        def xac_thuc_otp(self, otp): return True, "Xác thực thành công!"

        def luu_mat_khau_moi(self, p1, p2): return True, "Mật khẩu đã được thay đổi!"


    app_test = ForgotPasswordPage(parent=root, on_back_command=test_back)
    app_test.controller = MockController()
    app_test.pack(fill="both", expand=True)

    root.mainloop()