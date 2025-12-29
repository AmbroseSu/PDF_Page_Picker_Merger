# import os
# import re
# import tkinter as tk
# from tkinter import ttk, filedialog, messagebox
# from pypdf import PdfReader, PdfWriter
#
#
# def parse_page_spec(spec: str, max_pages: int):
#     """
#     Parse input like:
#       "2" -> [1]
#       "2-5" -> [1,2,3,4]
#       "2,4,7-9" -> [1,3,6,7,8]
#     Returns 0-based unique pages in given order.
#     Raises ValueError if invalid or out of range.
#     """
#     spec = spec.strip().replace(" ", "")
#     if not spec:
#         raise ValueError("Bạn chưa nhập trang.")
#
#     parts = spec.split(",")
#     pages = []
#     seen = set()
#
#     range_pat = re.compile(r"^(\d+)-(\d+)$")
#     num_pat = re.compile(r"^\d+$")
#
#     for part in parts:
#         if not part:
#             raise ValueError("Chuỗi trang không hợp lệ (dấu phẩy thừa).")
#
#         m = range_pat.match(part)
#         if m:
#             a = int(m.group(1))
#             b = int(m.group(2))
#             if a < 1 or b < 1:
#                 raise ValueError("Trang phải >= 1.")
#             if a > b:
#                 raise ValueError(f"Dải trang '{part}' không hợp lệ (đầu > cuối).")
#             if b > max_pages:
#                 raise ValueError(f"Dải '{part}' vượt quá số trang PDF (tối đa {max_pages}).")
#
#             for p in range(a, b + 1):
#                 idx = p - 1
#                 if idx not in seen:
#                     pages.append(idx)
#                     seen.add(idx)
#             continue
#
#         if num_pat.match(part):
#             p = int(part)
#             if p < 1:
#                 raise ValueError("Trang phải >= 1.")
#             if p > max_pages:
#                 raise ValueError(f"Trang '{p}' vượt quá số trang PDF (tối đa {max_pages}).")
#             idx = p - 1
#             if idx not in seen:
#                 pages.append(idx)
#                 seen.add(idx)
#             continue
#
#         raise ValueError(f"Không hiểu phần '{part}'. Ví dụ hợp lệ: 2-5 hoặc 2,4,7-9")
#
#     return pages
#
#
# class PdfMergePickerApp(tk.Tk):
#     def __init__(self):
#         super().__init__()
#         self.title("PDF Page Picker & Merger")
#         self.geometry("900x520")
#         self.minsize(900, 520)
#
#         # State
#         self.current_pdf_path = None
#         self.current_pdf_pages = 0
#         self.current_reader = None  # only for page count; export will re-read for safety
#         self.selections = []  # list of dict: {path, pages(list 0-based), label}
#
#         self._build_ui()
#
#     def _build_ui(self):
#         # Top frame: select pdf
#         top = ttk.Frame(self, padding=10)
#         top.pack(fill="x")
#
#         self.btn_choose = ttk.Button(top, text="Choose PDF...", command=self.choose_pdf)
#         self.btn_choose.pack(side="left")
#
#         self.lbl_pdf = ttk.Label(top, text="No PDF selected")
#         self.lbl_pdf.pack(side="left", padx=10)
#
#         # Middle frame: page spec input + add
#         mid = ttk.LabelFrame(self, text="Pick pages from selected PDF", padding=10)
#         mid.pack(fill="x", padx=10, pady=(0, 10))
#
#         ttk.Label(mid, text="Pages (examples: 2 | 2-5 | 2,4,7-9):").grid(row=0, column=0, sticky="w")
#
#         self.page_spec_var = tk.StringVar()
#         self.entry_pages = ttk.Entry(mid, textvariable=self.page_spec_var, width=40)
#         self.entry_pages.grid(row=0, column=1, padx=10, sticky="w")
#
#         self.btn_add = ttk.Button(mid, text="Add selection →", command=self.add_selection)
#         self.btn_add.grid(row=0, column=2, padx=10)
#
#         self.lbl_info = ttk.Label(mid, text="Tip: Select a PDF first.")
#         self.lbl_info.grid(row=1, column=0, columnspan=3, sticky="w", pady=(8, 0))
#
#         mid.columnconfigure(1, weight=1)
#
#         # Bottom frame: list + actions
#         bottom = ttk.Frame(self, padding=(10, 0, 10, 10))
#         bottom.pack(fill="both", expand=True)
#
#         left = ttk.Frame(bottom)
#         left.pack(side="left", fill="both", expand=True)
#
#         ttk.Label(left, text="Merge order (top → bottom):").pack(anchor="w")
#
#         # Treeview
#         columns = ("pdf", "pages")
#         self.tree = ttk.Treeview(left, columns=columns, show="headings", height=14)
#         self.tree.heading("pdf", text="PDF file")
#         self.tree.heading("pages", text="Pages")
#         self.tree.column("pdf", width=520, anchor="w")
#         self.tree.column("pages", width=260, anchor="w")
#         self.tree.pack(fill="both", expand=True, pady=(6, 0))
#
#         # Right actions
#         right = ttk.Frame(bottom, width=220)
#         right.pack(side="right", fill="y", padx=(10, 0))
#
#         ttk.Button(right, text="Move Up", command=self.move_up).pack(fill="x", pady=4)
#         ttk.Button(right, text="Move Down", command=self.move_down).pack(fill="x", pady=4)
#         ttk.Button(right, text="Remove Selected", command=self.remove_selected).pack(fill="x", pady=4)
#         ttk.Button(right, text="Clear All", command=self.clear_all).pack(fill="x", pady=4)
#
#         ttk.Separator(right).pack(fill="x", pady=10)
#
#         ttk.Button(right, text="Export PDF...", command=self.export_pdf).pack(fill="x", pady=6)
#
#         self.status_var = tk.StringVar(value="Ready.")
#         ttk.Label(self, textvariable=self.status_var, relief="sunken", anchor="w").pack(fill="x", side="bottom")
#
#     def choose_pdf(self):
#         path = filedialog.askopenfilename(
#             title="Choose a PDF",
#             filetypes=[("PDF files", "*.pdf")],
#         )
#         if not path:
#             return
#
#         try:
#             reader = PdfReader(path)
#             n = len(reader.pages)
#         except Exception as e:
#             messagebox.showerror("Error", f"Không đọc được PDF:\n{e}")
#             return
#
#         self.current_pdf_path = path
#         self.current_reader = reader
#         self.current_pdf_pages = n
#
#         name = os.path.basename(path)
#         self.lbl_pdf.config(text=f"{name}  ({n} pages)")
#         self.lbl_info.config(text=f"Selected: {name}. Nhập trang 1..{n} rồi bấm 'Add selection'.")
#         self.status_var.set(f"Loaded: {name} ({n} pages).")
#         self.entry_pages.focus_set()
#
#     def add_selection(self):
#         if not self.current_pdf_path:
#             messagebox.showwarning("Missing PDF", "Bạn hãy chọn 1 file PDF trước.")
#             return
#
#         spec = self.page_spec_var.get().strip()
#         try:
#             pages = parse_page_spec(spec, self.current_pdf_pages)
#         except ValueError as e:
#             messagebox.showerror("Invalid pages", str(e))
#             return
#
#         # Save selection
#         pdf_name = os.path.basename(self.current_pdf_path)
#         pages_display = self._format_pages_for_display(pages)
#         label = f"{pdf_name} | {pages_display}"
#
#         self.selections.append({
#             "path": self.current_pdf_path,
#             "pages": pages,
#             "label": label,
#         })
#
#         self.tree.insert("", "end", values=(pdf_name, pages_display))
#         self.status_var.set(f"Added: {label}")
#
#         # Clear input for next add
#         self.page_spec_var.set("")
#         self.entry_pages.focus_set()
#
#     def _format_pages_for_display(self, pages_0_based):
#         # Convert 0-based list to 1-based display, compress consecutive ranges
#         pages = [p + 1 for p in pages_0_based]
#         if not pages:
#             return ""
#
#         ranges = []
#         start = prev = pages[0]
#         for p in pages[1:]:
#             if p == prev + 1:
#                 prev = p
#             else:
#                 ranges.append((start, prev))
#                 start = prev = p
#         ranges.append((start, prev))
#
#         out = []
#         for a, b in ranges:
#             out.append(str(a) if a == b else f"{a}-{b}")
#         return ",".join(out)
#
#     def _get_selected_index(self):
#         sel = self.tree.selection()
#         if not sel:
#             return None
#         item_id = sel[0]
#         index = self.tree.index(item_id)
#         return index
#
#     def move_up(self):
#         idx = self._get_selected_index()
#         if idx is None:
#             return
#         if idx <= 0:
#             return
#
#         # Swap in selections
#         self.selections[idx - 1], self.selections[idx] = self.selections[idx], self.selections[idx - 1]
#         # Rebuild tree
#         self._rebuild_tree(select_index=idx - 1)
#         self.status_var.set("Moved up.")
#
#     def move_down(self):
#         idx = self._get_selected_index()
#         if idx is None:
#             return
#         if idx >= len(self.selections) - 1:
#             return
#
#         self.selections[idx + 1], self.selections[idx] = self.selections[idx], self.selections[idx + 1]
#         self._rebuild_tree(select_index=idx + 1)
#         self.status_var.set("Moved down.")
#
#     def remove_selected(self):
#         idx = self._get_selected_index()
#         if idx is None:
#             return
#         del self.selections[idx]
#         self._rebuild_tree(select_index=min(idx, len(self.selections) - 1) if self.selections else None)
#         self.status_var.set("Removed selection.")
#
#     def clear_all(self):
#         self.selections.clear()
#         for item in self.tree.get_children():
#             self.tree.delete(item)
#         self.status_var.set("Cleared all selections.")
#
#     def _rebuild_tree(self, select_index=None):
#         for item in self.tree.get_children():
#             self.tree.delete(item)
#         for s in self.selections:
#             pdf_name = os.path.basename(s["path"])
#             pages_display = self._format_pages_for_display(s["pages"])
#             self.tree.insert("", "end", values=(pdf_name, pages_display))
#         if select_index is not None and 0 <= select_index < len(self.tree.get_children()):
#             item_id = self.tree.get_children()[select_index]
#             self.tree.selection_set(item_id)
#             self.tree.see(item_id)
#
#     def export_pdf(self):
#         if not self.selections:
#             messagebox.showwarning("Nothing to export", "Danh sách gộp đang trống. Hãy Add selection trước.")
#             return
#
#         out_path = filedialog.asksaveasfilename(
#             title="Save merged PDF as",
#             defaultextension=".pdf",
#             filetypes=[("PDF files", "*.pdf")],
#             initialfile="merged.pdf"
#         )
#         if not out_path:
#             return
#
#         writer = PdfWriter()
#
#         try:
#             for s in self.selections:
#                 reader = PdfReader(s["path"])
#                 max_pages = len(reader.pages)
#
#                 # Safety check in case file changed
#                 for p in s["pages"]:
#                     if p < 0 or p >= max_pages:
#                         raise ValueError(
#                             f"File '{os.path.basename(s['path'])}' không còn đủ trang. "
#                             f"Trang yêu cầu: {p+1}, tối đa hiện tại: {max_pages}"
#                         )
#                     writer.add_page(reader.pages[p])
#
#             with open(out_path, "wb") as f:
#                 writer.write(f)
#
#         except Exception as e:
#             messagebox.showerror("Export failed", f"Không xuất được PDF:\n{e}")
#             self.status_var.set("Export failed.")
#             return
#
#         messagebox.showinfo("Done", f"Đã xuất file:\n{out_path}")
#         self.status_var.set(f"Exported: {out_path}")
#
#
# if __name__ == "__main__":
#     app = PdfMergePickerApp()
#     app.mainloop()



import os
import re
import sys
import customtkinter as ctk
from tkinter import filedialog, messagebox
from pypdf import PdfReader, PdfWriter


def parse_page_spec(spec: str, max_pages: int):
    spec = spec.strip().replace(" ", "")
    if not spec:
        raise ValueError("Bạn chưa nhập trang.")

    parts = spec.split(",")
    pages, seen = [], set()

    range_pat = re.compile(r"^(\d+)-(\d+)$")
    num_pat = re.compile(r"^\d+$")

    for part in parts:
        if not part:
            raise ValueError("Chuỗi trang không hợp lệ (dấu phẩy thừa).")

        m = range_pat.match(part)
        if m:
            a, b = int(m.group(1)), int(m.group(2))
            if a < 1 or b < 1:
                raise ValueError("Trang phải >= 1.")
            if a > b:
                raise ValueError(f"Dải '{part}' không hợp lệ (đầu > cuối).")
            if b > max_pages:
                raise ValueError(f"Dải '{part}' vượt quá số trang (tối đa {max_pages}).")

            for p in range(a, b + 1):
                idx = p - 1
                if idx not in seen:
                    pages.append(idx)
                    seen.add(idx)
            continue

        if num_pat.match(part):
            p = int(part)
            if p < 1:
                raise ValueError("Trang phải >= 1.")
            if p > max_pages:
                raise ValueError(f"Trang '{p}' vượt quá số trang (tối đa {max_pages}).")

            idx = p - 1
            if idx not in seen:
                pages.append(idx)
                seen.add(idx)
            continue

        raise ValueError(f"Không hiểu '{part}'. Ví dụ: 2-5 hoặc 2,4,7-9")

    return pages


def format_pages_for_display(pages_0_based):
    pages = [p + 1 for p in pages_0_based]
    if not pages:
        return ""
    ranges = []
    start = prev = pages[0]
    for p in pages[1:]:
        if p == prev + 1:
            prev = p
        else:
            ranges.append((start, prev))
            start = prev = p
    ranges.append((start, prev))
    out = []
    for a, b in ranges:
        out.append(str(a) if a == b else f"{a}-{b}")
    return ",".join(out)


LANG = {
    "en": {
        "choose_pdf": "Choose PDF",
        "no_pdf": "No PDF selected",
        "pick_pages": "Pick pages",
        "pages_hint": "Pages (e.g. 2 | 2-5 | 2,4,7-9):",
        "enter_pages": "Enter pages…",
        "add": "Add",
        "tip_select_pdf": "Tip: Select a PDF first.",
        "tip_selected_pdf": "Selected: {name}. Enter pages 1..{n} then click Add.",
        "merge_order": "Merge order",
        "total_pages": "Total pages: {n}",
        "pdf_col": "PDF",
        "pages_col": "Pages",
        "actions": "Actions",
        "move_up": "Move Up",
        "move_down": "Move Down",
        "remove_selected": "Remove Selected",
        "clear_all": "Clear All",
        "export_pdf": "Export PDF",
        "ready": "Ready.",
        "lang": "Language",
        "mode": "Theme",
    },
    "vi": {
        "choose_pdf": "Chọn PDF",
        "no_pdf": "Chưa chọn PDF",
        "pick_pages": "Chọn trang",
        "pages_hint": "Trang (vd: 2 | 2-5 | 2,4,7-9):",
        "enter_pages": "Nhập trang…",
        "add": "Thêm",
        "tip_select_pdf": "Gợi ý: Hãy chọn PDF trước.",
        "tip_selected_pdf": "Đã chọn: {name}. Nhập trang 1..{n} rồi bấm Thêm.",
        "merge_order": "Thứ tự gộp",
        "total_pages": "Tổng trang: {n}",
        "pdf_col": "PDF",
        "pages_col": "Trang",
        "actions": "Thao tác",
        "move_up": "Lên",
        "move_down": "Xuống",
        "remove_selected": "Xoá mục chọn",
        "clear_all": "Xoá hết",
        "export_pdf": "Xuất PDF",
        "ready": "Sẵn sàng.",
        "lang": "Ngôn ngữ",
        "mode": "Giao diện",
    },
}

def tr(lang: str, key: str, **kwargs) -> str:
    s = LANG.get(lang, LANG["en"]).get(key, key)
    return s.format(**kwargs) if kwargs else s


def count_pages(pages_0_based):
    return len(pages_0_based)

def resource_path(rel_path: str) -> str:
    # khi chạy .py và khi chạy .exe (PyInstaller)
    if getattr(sys, 'frozen', False):
        return os.path.join(sys._MEIPASS, rel_path)
    return os.path.join(os.path.dirname(__file__), rel_path)


class PdfMergePickerCTK(ctk.CTk):
    def __init__(self):
        super().__init__()

        try:
            self.iconbitmap(resource_path("favicon.ico"))
        except Exception:
            pass

        ctk.set_appearance_mode("Light")
        ctk.set_default_color_theme("blue")

        self.btn_font = ctk.CTkFont(size=13, weight="bold")
        self.menu_font = ctk.CTkFont(size=13, weight="bold")

        self.lang = "en"  # đổi thành "vi" nếu muốn mặc định tiếng Việt

        self.title("PDF Page Picker & Merger")
        self.geometry("1000x640")
        self.minsize(1000, 640)

        self.current_pdf_path = None
        self.current_pdf_pages = 0
        self.selections = []  # {path, pages}
        self.selected_index = None

        self._build_ui()

    # ---------- UI ----------
    def _build_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        # Top bar
        top = ctk.CTkFrame(self, corner_radius=16, fg_color=("gray92", "gray14"))
        top.grid(row=0, column=0, sticky="ew", padx=16, pady=(16, 10))
        top.grid_columnconfigure(1, weight=1)

        self.btn_choose = ctk.CTkButton(
            top, text=tr(self.lang, "choose_pdf"), width=140, height=36,
            command=self.choose_pdf, font=self.btn_font
        )
        self.btn_choose.grid(row=0, column=0, padx=12, pady=12, sticky="w")

        self.lbl_pdf = ctk.CTkLabel(top, text=tr(self.lang, "no_pdf"), anchor="w")
        self.lbl_pdf.grid(row=0, column=1, padx=10, pady=12, sticky="ew")

        self.lbl_lang = ctk.CTkLabel(top, text=tr(self.lang, "lang"))
        self.lbl_lang.grid(row=0, column=2, padx=(10, 6), pady=12, sticky="e")

        self.lang_menu = ctk.CTkOptionMenu(
            top, values=["EN", "VI"],
            width=90, font=self.menu_font, anchor="center",
            command=self.change_language
        )
        self.lang_menu.configure(dropdown_font=self.menu_font)
        self.lang_menu.set("EN" if self.lang == "en" else "VI")
        self.lang_menu.grid(row=0, column=3, padx=(0, 12), pady=12, sticky="e")

        self.mode = ctk.CTkOptionMenu(
            top,
            values=["Light", "Dark", "System"],
            command=self.change_mode,
            width=130,
            font=self.menu_font,  # chữ in đậm
            anchor="center"  # căn giữa chữ
        )
        self.mode.configure(dropdown_font=self.menu_font)
        self.mode.set("Light")
        self.mode.grid(row=0, column=4, padx=12, pady=12, sticky="e")

        # Picker card
        picker = ctk.CTkFrame(self, corner_radius=16, fg_color=("gray95", "gray15"))
        picker.grid(row=1, column=0, sticky="ew", padx=16, pady=(0, 12))
        picker.grid_columnconfigure(1, weight=1)

        self.lbl_pick_title = ctk.CTkLabel(picker, text=tr(self.lang, "pick_pages"), font=ctk.CTkFont(size=16, weight="bold"))
        self.lbl_pick_title.grid(row=0, column=0, columnspan=3, padx=16, pady=(14, 6), sticky="w")

        self.lbl_pages_hint = ctk.CTkLabel(picker, text=tr(self.lang, "pages_hint"))
        self.lbl_pages_hint.grid(row=1, column=0, padx=16, pady=(0, 10), sticky="w")

        self.entry_pages = ctk.CTkEntry(picker, placeholder_text=tr(self.lang, ""), height=36)
        self.entry_pages.grid(row=1, column=1, padx=10, pady=(0, 10), sticky="ew")
        self.entry_pages.bind("<Return>", lambda _e: self.add_selection())

        self.btn_add = ctk.CTkButton(
            picker, text=tr(self.lang, "add"), width=120, height=36,
            command=self.add_selection, font=self.btn_font
        )
        self.btn_add.grid(row=1, column=2, padx=16, pady=(0, 10), sticky="e")

        self.lbl_tip = ctk.CTkLabel(picker, text=tr(self.lang, "tip_select_pdf"), text_color=("gray35", "gray75"))
        self.lbl_tip.grid(row=2, column=0, columnspan=3, padx=16, pady=(0, 14), sticky="w")

        # Main area: list + actions
        main = ctk.CTkFrame(self, corner_radius=16, fg_color=("gray95", "gray15"))
        main.grid(row=2, column=0, sticky="nsew", padx=16, pady=(0, 12))
        main.grid_columnconfigure(0, weight=1)
        main.grid_columnconfigure(1, weight=0)
        main.grid_rowconfigure(1, weight=1)

        # Left: list panel
        left = ctk.CTkFrame(main, corner_radius=16, fg_color=("gray97", "gray16"))
        left.grid(row=0, column=0, rowspan=2, sticky="nsew", padx=(14, 10), pady=14)
        left.grid_rowconfigure(2, weight=1)
        left.grid_columnconfigure(0, weight=1)

        header = ctk.CTkFrame(left, corner_radius=12, fg_color=("gray92", "gray18"))
        header.grid(row=0, column=0, sticky="ew", padx=14, pady=(14, 8))
        header.grid_columnconfigure(1, weight=1)

        self.lbl_merge_title = ctk.CTkLabel(header, text=tr(self.lang, "merge_order"), font=ctk.CTkFont(size=14, weight="bold"))
        self.lbl_merge_title.grid(row=0, column=0, padx=12, pady=10, sticky="w")

        self.badge_total = ctk.CTkLabel(
            header,
            text="Total pages: 0",
            text_color=("gray25", "gray80"),
            fg_color=("gray90", "gray22"),
            corner_radius=999,
            padx=12,
            pady=4
        )
        self.badge_total.grid(row=0, column=2, padx=12, pady=10, sticky="e")

        # Column hint row
        hint = ctk.CTkFrame(left, corner_radius=10, fg_color="transparent")
        hint.grid(row=1, column=0, sticky="ew", padx=18, pady=(0, 6))
        hint.grid_columnconfigure(0, weight=1)
        hint.grid_columnconfigure(1, weight=0)

        self.lbl_pdf_col = ctk.CTkLabel(hint, text=tr(self.lang, "pdf_col"), text_color=("gray35", "gray70"))
        self.lbl_pdf_col.grid(row=0, column=0, sticky="w")

        self.lbl_pages_col = ctk.CTkLabel(hint, text=tr(self.lang, "pages_col"), text_color=("gray35", "gray70"))
        self.lbl_pages_col.grid(row=0, column=1, sticky="e")

        self.list_frame = ctk.CTkScrollableFrame(left, corner_radius=12, fg_color=("gray95", "gray15"))
        self.list_frame.grid(row=2, column=0, sticky="nsew", padx=14, pady=(0, 14))

        # Empty state
        self.empty_label = ctk.CTkLabel(
            self.list_frame,
            text="Chưa có selection nào.\nChọn PDF → nhập trang → bấm Add.",
            text_color=("gray40", "gray70"),
            justify="center"
        )
        self.empty_label.pack(expand=True, pady=40)

        # Right: action panel
        right = ctk.CTkFrame(main, corner_radius=16, width=240, fg_color=("gray97", "gray16"))
        right.grid(row=0, column=1, rowspan=2, sticky="ns", padx=(10, 14), pady=14)

        self.lbl_actions_title = ctk.CTkLabel(right, text=tr(self.lang, "actions"),
                                              font=ctk.CTkFont(size=14, weight="bold"))
        self.lbl_actions_title.pack(anchor="w", padx=14, pady=(14, 10))

        self.btn_up = ctk.CTkButton(right, text=tr(self.lang, "move_up"), command=self.move_up, height=36, font=self.btn_font)
        self.btn_down = ctk.CTkButton(right, text=tr(self.lang, "move_down"), command=self.move_down, height=36, font=self.btn_font)
        self.btn_remove = ctk.CTkButton(right, text=tr(self.lang, "remove_selected"), command=self.remove_selected, height=36, font=self.btn_font)
        self.btn_clear = ctk.CTkButton(right, text=tr(self.lang, "clear_all"), command=self.clear_all, height=36, font=self.btn_font)

        for b in (self.btn_up, self.btn_down, self.btn_remove, self.btn_clear):
            b.pack(fill="x", padx=14, pady=6)

        ctk.CTkLabel(right, text="").pack(pady=6)

        self.btn_export = ctk.CTkButton(
            right, text=tr(self.lang, "export_pdf"), height=44,
            command=self.export_pdf, font=self.btn_font
        )
        self.btn_export.configure(font=ctk.CTkFont(size=15, weight="bold"))

        self.btn_export.pack(fill="x", padx=14, pady=(6, 14))

        # Status bar
        self.status = ctk.CTkLabel(self, text="Ready.", anchor="w", fg_color=("gray92", "gray14"), padx=12)
        self.status.grid(row=3, column=0, sticky="ew")
        self.apply_language()

    # ---------- Actions ----------
    def change_mode(self, mode):
        ctk.set_appearance_mode(mode)

    def change_language(self, value):
        self.lang = "en" if value == "EN" else "vi"
        self.apply_language()

    def apply_language(self):
        # Top
        self.btn_choose.configure(text=tr(self.lang, "choose_pdf"))
        self.lbl_lang.configure(text=tr(self.lang, "lang"))

        if not self.current_pdf_path:
            self.lbl_pdf.configure(text=tr(self.lang, "no_pdf"))
            self.lbl_tip.configure(text=tr(self.lang, "tip_select_pdf"))
        else:
            name = os.path.basename(self.current_pdf_path)
            self.lbl_tip.configure(text=tr(self.lang, "tip_selected_pdf", name=name, n=self.current_pdf_pages))

        # Picker
        self.lbl_pick_title.configure(text=tr(self.lang, "pick_pages"))
        self.lbl_pages_hint.configure(text=tr(self.lang, "pages_hint"))
        self.entry_pages.configure(placeholder_text=tr(self.lang, ""))
        self.btn_add.configure(text=tr(self.lang, "add"))

        # Merge + Actions
        self.lbl_merge_title.configure(text=tr(self.lang, "merge_order"))
        self.lbl_pdf_col.configure(text=tr(self.lang, "pdf_col"))
        self.lbl_pages_col.configure(text=tr(self.lang, "pages_col"))
        self.lbl_actions_title.configure(text=tr(self.lang, "actions"))

        self.btn_up.configure(text=tr(self.lang, "move_up"))
        self.btn_down.configure(text=tr(self.lang, "move_down"))
        self.btn_remove.configure(text=tr(self.lang, "remove_selected"))
        self.btn_clear.configure(text=tr(self.lang, "clear_all"))
        self.btn_export.configure(text=tr(self.lang, "export_pdf"))

        # Status (chỉ đổi nếu đang là Ready/Sẵn sàng)
        if self.status.cget("text") in ("Ready.", "Sẵn sàng."):
            self.status.configure(text=tr(self.lang, "ready"))

        self.refresh_list()

    def choose_pdf(self):
        path = filedialog.askopenfilename(title="Choose a PDF", filetypes=[("PDF files", "*.pdf")])
        if not path:
            return

        try:
            reader = PdfReader(path)
            n = len(reader.pages)
        except Exception as e:
            messagebox.showerror("Error", f"Không đọc được PDF:\n{e}")
            return

        self.current_pdf_path = path
        self.current_pdf_pages = n

        name = os.path.basename(path)
        self.lbl_pdf.configure(text=f"{name}  ({n} pages)")
        self.lbl_tip.configure(text=f"Selected: {name}. Nhập trang 1..{n} rồi bấm Add.")
        self.status.configure(text=f"Loaded: {name} ({n} pages).")
        self.entry_pages.focus()

    def add_selection(self):
        if not self.current_pdf_path:
            messagebox.showwarning("Missing PDF", "Bạn hãy chọn 1 file PDF trước.")
            return

        spec = self.entry_pages.get().strip()
        try:
            pages = parse_page_spec(spec, self.current_pdf_pages)
        except ValueError as e:
            messagebox.showerror("Invalid pages", str(e))
            return

        self.selections.append({"path": self.current_pdf_path, "pages": pages})
        self.selected_index = len(self.selections) - 1
        self.entry_pages.delete(0, "end")
        self.refresh_list()

        pdf_name = os.path.basename(self.current_pdf_path)
        self.status.configure(text=f"Added: {pdf_name} | {format_pages_for_display(pages)}")

    def refresh_list(self):
        for w in self.list_frame.winfo_children():
            w.destroy()

        if not self.selections:
            self.empty_label = ctk.CTkLabel(
                self.list_frame,
                text=tr(self.lang, "empty_state") if "empty_state" in LANG[self.lang] else "No selections yet.",
                text_color=("gray40", "gray70"),
                justify="center"
            )
            self.empty_label.pack(expand=True, pady=40)
            self.badge_total.configure(text=tr(self.lang, "total_pages", n=0))
            return

        total = sum(len(s["pages"]) for s in self.selections)
        self.badge_total.configure(text=tr(self.lang, "total_pages", n=total))

        for i, s in enumerate(self.selections):
            pdf_name = os.path.basename(s["path"])
            pages_display = format_pages_for_display(s["pages"])
            page_count = count_pages(s["pages"])

            is_selected = (i == self.selected_index)

            item = ctk.CTkFrame(
                self.list_frame,
                corner_radius=12,
                fg_color=("white", "gray19"),
                border_width=2 if is_selected else 1,
                border_color=("#2f7dd1" if is_selected else ("#d9d9d9" if ctk.get_appearance_mode() == "Light" else "#333333"))
            )
            item.pack(fill="x", padx=8, pady=8)

            item.grid_columnconfigure(1, weight=1)

            # Left icon-ish badge
            badge = ctk.CTkLabel(
                item, text="PDF", width=42, height=34,
                fg_color=("#2f7dd1" if is_selected else ("#e9eef6" if ctk.get_appearance_mode() == "Light" else "#2a2f3a")),
                text_color=("white" if is_selected else ("#2f7dd1" if ctk.get_appearance_mode() == "Light" else "white")),
                corner_radius=10
            )
            badge.grid(row=0, column=0, rowspan=2, padx=12, pady=12, sticky="w")

            title = ctk.CTkLabel(item, text=pdf_name, font=ctk.CTkFont(size=13, weight="bold"), anchor="w")
            title.grid(row=0, column=1, padx=(0, 12), pady=(12, 2), sticky="ew")

            sub = ctk.CTkLabel(
                item,
                text=f"Pages: {pages_display}   •   {page_count} page(s)",
                text_color=("gray35", "gray75"),
                anchor="w"
            )
            sub.grid(row=1, column=1, padx=(0, 12), pady=(0, 12), sticky="ew")

            def make_select(idx):
                return lambda _=None: self.select_index(idx)

            for w in (item, badge, title, sub):
                w.bind("<Button-1>", make_select(i))

    def select_index(self, idx):
        self.selected_index = idx
        self.refresh_list()

    def move_up(self):
        idx = self.selected_index
        if idx is None or idx <= 0:
            return
        self.selections[idx - 1], self.selections[idx] = self.selections[idx], self.selections[idx - 1]
        self.selected_index = idx - 1
        self.refresh_list()
        self.status.configure(text="Moved up.")

    def move_down(self):
        idx = self.selected_index
        if idx is None or idx >= len(self.selections) - 1:
            return
        self.selections[idx + 1], self.selections[idx] = self.selections[idx], self.selections[idx + 1]
        self.selected_index = idx + 1
        self.refresh_list()
        self.status.configure(text="Moved down.")

    def remove_selected(self):
        idx = self.selected_index
        if idx is None or not self.selections:
            return
        del self.selections[idx]
        self.selected_index = None if not self.selections else min(idx, len(self.selections) - 1)
        self.refresh_list()
        self.status.configure(text="Removed selection.")

    def clear_all(self):
        self.selections.clear()
        self.selected_index = None
        self.refresh_list()
        self.status.configure(text="Cleared all selections.")

    def export_pdf(self):
        if not self.selections:
            messagebox.showwarning("Nothing to export", "Danh sách gộp đang trống. Hãy Add selection trước.")
            return

        out_path = filedialog.asksaveasfilename(
            title="Save merged PDF as",
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")],
            initialfile="merged.pdf"
        )
        if not out_path:
            return

        writer = PdfWriter()
        try:
            for s in self.selections:
                reader = PdfReader(s["path"])
                max_pages = len(reader.pages)
                for p in s["pages"]:
                    if p < 0 or p >= max_pages:
                        raise ValueError(
                            f"File '{os.path.basename(s['path'])}' không còn đủ trang. "
                            f"Trang yêu cầu: {p+1}, tối đa hiện tại: {max_pages}"
                        )
                    writer.add_page(reader.pages[p])

            with open(out_path, "wb") as f:
                writer.write(f)

        except Exception as e:
            messagebox.showerror("Export failed", f"Không xuất được PDF:\n{e}")
            self.status.configure(text="Export failed.")
            return

        messagebox.showinfo("Done", f"Đã xuất file:\n{out_path}")
        self.status.configure(text=f"Exported: {out_path}")


if __name__ == "__main__":
    app = PdfMergePickerCTK()
    app.mainloop()


