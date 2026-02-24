import customtkinter as ctk
from tkinter import messagebox, ttk, filedialog
from src.Controller.HoaDonController import HoaDonController
from datetime import datetime


class HoaDonPage(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="white")

        self.controller = HoaDonController()
        self.current_list = []
        self.selected_id = None

        # Setup giao diện
        self.setup_ui_layout()
        self.style_treeview()

        # Load dữ liệu ban đầu
        self.load_table_data()

    def setup_ui_layout(self):
        # Container chính
        container = ctk.CTkFrame(self, fg_color="white")
        container.pack(fill="both", expand=True, padx=20, pady=20)

        # Tiêu đề
        ctk.CTkLabel(container, text="Quản Lý Hoá Đơn",
                     font=("Arial", 18, "bold"), text_color="#333").pack(anchor="w", pady=(0, 20))

        # === THANH CÔNG CỤ (TOOLBAR) ===
        toolbar_frame = ctk.CTkFrame(container, fg_color="#F9F9F9", corner_radius=8)
        toolbar_frame.pack(fill="x", pady=(0, 15), ipady=5)

        # Dòng 1: Các nút chức năng
        btn_row = ctk.CTkFrame(toolbar_frame, fg_color="transparent")
        btn_row.pack(fill="x", padx=10, pady=10)

        self.create_btn(btn_row, "📄 Xem Chi Tiết", "#2196F3", self.xem_chi_tiet)
        self.create_btn(btn_row, "🖨 Xuất PDF", "#009688", self.xuat_pdf)
        self.create_btn(btn_row, "❌ Hủy Hóa Đơn", "#F44336", self.huy_hoa_don)
        self.create_btn(btn_row, "🔄 Tải lại", "#607D8B", self.reload_data)

        # Dòng 2: Bộ lọc
        filter_row = ctk.CTkFrame(toolbar_frame, fg_color="transparent")
        filter_row.pack(fill="x", padx=10, pady=(0, 10))

        # -- Filter Date --
        ctk.CTkLabel(filter_row, text="Thời gian:", font=("Arial", 12, "bold")).pack(side="left", padx=(0, 5))

        days = ["Tất cả"] + [str(i) for i in range(1, 32)]
        self.cb_day = ctk.CTkComboBox(filter_row, values=days, width=70, state="readonly")
        self.cb_day.set("Tất cả")
        self.cb_day.pack(side="left", padx=2)

        months = ["Tất cả"] + [str(i) for i in range(1, 13)]
        self.cb_month = ctk.CTkComboBox(filter_row, values=months, width=70, state="readonly")
        self.cb_month.set(str(datetime.now().month))  # Mặc định tháng hiện tại
        self.cb_month.pack(side="left", padx=2)

        self.entry_year = ctk.CTkEntry(filter_row, width=60, placeholder_text="Năm")
        self.entry_year.insert(0, str(datetime.now().year))
        self.entry_year.pack(side="left", padx=2)

        # -- Search --
        ctk.CTkLabel(filter_row, text="|  Tìm kiếm:", font=("Arial", 12, "bold")).pack(side="left", padx=(15, 5))
        self.search_entry = ctk.CTkEntry(filter_row, width=250,
                                         placeholder_text="Nhập Mã HĐ, Tên KH hoặc Nội dung CK...")
        self.search_entry.pack(side="left", padx=5)

        ctk.CTkButton(filter_row, text="🔍 Tìm Kiếm", width=100, fg_color="#3F51B5",
                      command=self.thuc_hien_loc).pack(side="left", padx=10)

        # === BẢNG DỮ LIỆU (TREEVIEW) ===
        table_frame = ctk.CTkFrame(container, fg_color="white")
        table_frame.pack(fill="both", expand=True)

        # Scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical")
        scrollbar.pack(side="right", fill="y")

        # Cấu hình cột
        cols = ("id", "kh", "nv", "ngay", "tien", "pay", "tt")
        self.tree = ttk.Treeview(table_frame, columns=cols, show="headings",
                                 height=15, yscrollcommand=scrollbar.set)

        scrollbar.config(command=self.tree.yview)

        # Tiêu đề cột
        # [QUAN TRỌNG] Cột id bây giờ hiển thị Mã hoặc Nội dung CK -> Cần rộng hơn
        self.tree.heading("id", text="Mã HĐ / Nội dung CK")
        self.tree.heading("kh", text="Khách Hàng")
        self.tree.heading("nv", text="Nhân Viên")
        self.tree.heading("ngay", text="Ngày Tạo")
        self.tree.heading("tien", text="Tổng Tiền")
        self.tree.heading("pay", text="Hình thức TT")
        self.tree.heading("tt", text="Trạng Thái")

        # Kích thước cột
        self.tree.column("id", width=180, anchor="w")  # Canh trái để đọc nội dung CK dễ hơn
        self.tree.column("kh", width=150)
        self.tree.column("nv", width=120)
        self.tree.column("ngay", width=120, anchor="center")
        self.tree.column("tien", width=100, anchor="e")
        self.tree.column("pay", width=150, anchor="center")
        self.tree.column("tt", width=100, anchor="center")

        # Màu sắc trạng thái
        self.tree.tag_configure('success', foreground='green')  # Đã thanh toán
        self.tree.tag_configure('cancel', foreground='red')  # Đã hủy
        self.tree.tag_configure('wait', foreground='#F57C00')  # Chờ thanh toán

        self.tree.pack(fill="both", expand=True)
        self.tree.bind("<<TreeviewSelect>>", self.on_select)

    def style_treeview(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview.Heading", font=("Arial", 11, "bold"), background="#E0E0E0", padding=5)
        style.configure("Treeview", font=("Arial", 10), rowheight=28)

    def create_btn(self, parent, text, color, cmd):
        ctk.CTkButton(parent, text=text, fg_color=color, hover_color=color,
                      width=110, height=35, command=cmd).pack(side="left", padx=5)

    # === LOGIC DỮ LIỆU ===
    def load_table_data(self, data=None):
        # Xóa dữ liệu cũ
        for i in self.tree.get_children():
            self.tree.delete(i)

        self.selected_id = None  # Reset selection

        if data is None:
            self.current_list = self.controller.get_list_invoices()
        else:
            self.current_list = data

        for item in self.current_list:
            # Xác định màu sắc
            tag = 'wait'
            if item['trangThai'] == 2:
                tag = 'success'
            elif item['trangThai'] == 0:
                tag = 'cancel'

            # [QUAN TRỌNG NHẤT]
            # 1. 'iid' (Internal ID): Gán bằng ID thật của Database (item['idHoaDon'])
            #    để khi click vào dòng, ta lấy được ID này để xử lý.
            # 2. values[0]: Hiển thị 'maHienThi' (đã xử lý ở Controller: là Nội dung CK hoặc #ID)

            self.tree.insert("", "end", iid=item['idHoaDon'], values=(
                item['maHienThi'],  # Cột 1: Hiển thị nội dung
                item['tenKhachHang'],
                item['tenNhanVien'],
                item['ngayTaoFmt'],
                item['tongTienFmt'],
                item['paymentMethod'],
                item['statusText']
            ), tags=(tag,))

    def on_select(self, event):
        sel = self.tree.selection()
        if sel:
            # Lấy ID thật từ iid (không phải từ values[0])
            self.selected_id = sel[0]
            # print(f"Selected Real ID: {self.selected_id}")

    def thuc_hien_loc(self):
        d = self.cb_day.get()
        m = self.cb_month.get()
        y = self.entry_year.get()
        kw = self.search_entry.get().strip()

        data = self.controller.filter_invoices(d, m, y, kw)
        self.load_table_data(data)

    def reload_data(self):
        self.search_entry.delete(0, "end")
        self.cb_day.set("Tất cả")
        # Giữ lại tháng hiện tại hoặc reset tùy ý
        self.load_table_data(None)

    # === CÁC CHỨC NĂNG ===
    def huy_hoa_don(self):
        if not self.selected_id:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn hóa đơn cần hủy!")
            return

        # Kiểm tra trạng thái hiện tại (Optional: Không cho hủy nếu đã thanh toán?)
        # Ở đây cho phép hủy nhưng hỏi kỹ
        if messagebox.askyesno("Xác nhận", f"Bạn chắc chắn muốn hủy hóa đơn #{self.selected_id}?"):
            if self.controller.delete_invoice(self.selected_id):
                messagebox.showinfo("Thành công", "Đã hủy hóa đơn!")
                self.thuc_hien_loc()  # Load lại nhưng giữ bộ lọc
            else:
                messagebox.showerror("Lỗi", "Không thể hủy hóa đơn này!")

    def xuat_pdf(self):
        if not self.selected_id:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn hóa đơn để xuất!")
            return

        file_name = f"HoaDon_{self.selected_id}_{datetime.now().strftime('%Y%m%d')}.pdf"
        path = filedialog.asksaveasfilename(defaultextension=".pdf",
                                            initialfile=file_name,
                                            filetypes=[("PDF Files", "*.pdf")])
        if path:
            ok, msg = self.controller.export_invoice_pdf(self.selected_id, path)
            if ok:
                messagebox.showinfo("Thành công", msg)
            else:
                messagebox.showerror("Thất bại", msg)

    def xem_chi_tiet(self):
        if not self.selected_id:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn hóa đơn để xem!")
            return

        details = self.controller.get_details(self.selected_id)

        # Tạo cửa sổ Popup (Toplevel)
        top = ctk.CTkToplevel(self)
        top.geometry("700x400")
        top.title(f"Chi tiết Hóa Đơn #{self.selected_id}")
        top.attributes("-topmost", True)  # Luôn nổi lên trên

        # Tiêu đề popup
        ctk.CTkLabel(top, text="DANH SÁCH MÓN", font=("Arial", 16, "bold")).pack(pady=10)

        # Bảng chi tiết
        cols = ("mon", "sl", "gia", "vat", "tong")
        tree_detail = ttk.Treeview(top, columns=cols, show="headings", height=10)

        tree_detail.heading("mon", text="Tên Món")
        tree_detail.heading("sl", text="Số Lượng")
        tree_detail.heading("gia", text="Đơn Giá")
        tree_detail.heading("vat", text="VAT (%)")
        tree_detail.heading("tong", text="Thành Tiền")

        tree_detail.column("mon", width=250)
        tree_detail.column("sl", width=80, anchor="center")
        tree_detail.column("gia", width=100, anchor="e")
        tree_detail.column("vat", width=80, anchor="center")
        tree_detail.column("tong", width=120, anchor="e")

        tree_detail.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        # Đổ dữ liệu
        for item in details:
            tree_detail.insert("", "end", values=(
                item['tenSanPham'],
                item['soLuong'],
                item['donGiaFmt'],
                item['thueVAT'],
                item['thanhTienFmt']
            ))

        ctk.CTkButton(top, text="Đóng", fg_color="#F44336", width=100,
                      command=top.destroy).pack(pady=10)