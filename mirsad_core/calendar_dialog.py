# -*- coding: utf-8 -*-
"""
Interactive Calendar Date Picker Dialog for ArcMap Climate Atlas Tools.
Compatible with Python 2.7 (ArcGIS Desktop 10.x) and Python 3.x.
Provides a smooth, calm calendar window with month-by-month navigation arrows,
year/month dropdowns, clean day grid, and Start/End date setters.
"""

import sys
import os
import calendar
import datetime

try:
    import Tkinter as tk
    import ttk
except ImportError:
    import tkinter as tk
    from tkinter import ttk

MONTH_NAMES = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December"
]

MONTH_NAMES_AR = [
    u"يناير (01)", u"فبراير (02)", u"مارس (03)", u"أبريل (04)",
    u"مايو (05)", u"يونيو (06)", u"يوليو (07)", u"أغسطس (08)",
    u"سبتمبر (09)", u"أكتوبر (10)", u"نوفمبر (11)", u"ديسمبر (12)"
]

DAY_HEADERS = ["Sa", "Su", "Mo", "Tu", "We", "Th", "Fr"]


def parse_date_str(s):
    if not s:
        return None
    s = str(s).strip().split()[0]
    for fmt in ("%d/%m/%Y", "%Y-%m-%d", "%m/%d/%Y", "%Y/%m/%d", "%d-%m-%Y"):
        try:
            return datetime.datetime.strptime(s, fmt).date()
        except Exception:
            pass
    return None


class CalendarDialog(object):
    def __init__(self, parent=None, initial_start="01/01/2024", initial_end="31/12/2024"):
        self.result = {
            "start_date": initial_start or "01/01/2024",
            "end_date": initial_end or "31/12/2024",
            "applied": False
        }

        d_s = parse_date_str(initial_start) or datetime.date(2024, 1, 1)
        self.cur_year = d_s.year
        self.cur_month = d_s.month
        self.selected_date = d_s

        self.start_date = initial_start or "%02d/%02d/%04d" % (d_s.day, d_s.month, d_s.year)
        self.end_date = initial_end or "31/12/%04d" % d_s.year

        if parent:
            self.root = tk.Toplevel(parent)
        else:
            self.root = tk.Tk()

        self.root.title(u"Climate Atlas — Calendar Date Picker | محدد التواريخ")
        self.root.geometry("440x520")
        self.root.resizable(False, False)

        # Center window on screen
        self.root.update_idletasks()
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        x = max(0, (sw - 440) // 2)
        y = max(0, (sh - 520) // 2)
        self.root.geometry("+%d+%d" % (x, y))

        self._build_ui()
        self._refresh_calendar()

    def _build_ui(self):
        # Top banner
        header_frame = tk.Frame(self.root, bg="#1e3d59", padx=10, pady=8)
        header_frame.pack(fill=tk.X)

        title_lbl = tk.Label(
            header_frame,
            text=u"تقويم اختيار التواريخ المناخية (Custom Date Picker)",
            font=("Arial", 11, "bold"),
            fg="#ffffff",
            bg="#1e3d59"
        )
        title_lbl.pack()

        sub_lbl = tk.Label(
            header_frame,
            text=u"Select Start and End Dates smoothly without jumping",
            font=("Arial", 8),
            fg="#c5d7e8",
            bg="#1e3d59"
        )
        sub_lbl.pack()

        # Month / Year navigation bar
        nav_frame = tk.Frame(self.root, padx=10, pady=8, bg="#f5f7fa")
        nav_frame.pack(fill=tk.X)

        btn_prev = tk.Button(
            nav_frame, text=u"◀ السابق", width=7, font=("Arial", 9, "bold"),
            bg="#e0e6ed", command=self._prev_month
        )
        btn_prev.pack(side=tk.LEFT, padx=2)

        # Month dropdown
        self.month_var = tk.StringVar()
        self.month_var.set(MONTH_NAMES[self.cur_month - 1])
        self.month_cb = ttk.Combobox(
            nav_frame, textvariable=self.month_var,
            values=MONTH_NAMES, width=11, state="readonly"
        )
        self.month_cb.pack(side=tk.LEFT, padx=3)
        self.month_cb.bind("<<ComboboxSelected>>", self._on_month_change)

        # Year dropdown
        years_list = [str(y) for y in range(2026, 1980, -1)]
        self.year_var = tk.StringVar()
        self.year_var.set(str(self.cur_year))
        self.year_cb = ttk.Combobox(
            nav_frame, textvariable=self.year_var,
            values=years_list, width=6, state="readonly"
        )
        self.year_cb.pack(side=tk.LEFT, padx=3)
        self.year_cb.bind("<<ComboboxSelected>>", self._on_year_change)

        btn_next = tk.Button(
            nav_frame, text=u"التالي ▶", width=7, font=("Arial", 9, "bold"),
            bg="#e0e6ed", command=self._next_month
        )
        btn_next.pack(side=tk.LEFT, padx=2)

        # Fast year jump buttons
        btn_py = tk.Button(nav_frame, text="-1Y", width=3, font=("Arial", 8), command=self._prev_year)
        btn_py.pack(side=tk.RIGHT, padx=1)
        btn_ny = tk.Button(nav_frame, text="+1Y", width=3, font=("Arial", 8), command=self._next_year)
        btn_ny.pack(side=tk.RIGHT, padx=1)

        # Calendar grid frame
        self.cal_frame = tk.Frame(self.root, padx=10, pady=5, bg="#ffffff", relief=tk.GROOVE, bd=1)
        self.cal_frame.pack(fill=tk.BOTH, expand=True, padx=12, pady=5)

        # Active selection display & setters
        act_frame = tk.Frame(self.root, padx=10, pady=6, bg="#f5f7fa")
        act_frame.pack(fill=tk.X)

        self.sel_lbl = tk.Label(
            act_frame,
            text=u"التاريخ المحدد: %02d/%02d/%04d" % (self.selected_date.day, self.selected_date.month, self.selected_date.year),
            font=("Arial", 10, "bold"),
            fg="#1e3d59",
            bg="#f5f7fa"
        )
        self.sel_lbl.pack(pady=2)

        setter_frame = tk.Frame(act_frame, bg="#f5f7fa")
        setter_frame.pack(pady=3)

        btn_set_s = tk.Button(
            setter_frame,
            text=u"✔ تحديد كبداية (Set Start)",
            font=("Arial", 9, "bold"),
            bg="#2b580c", fg="#ffffff", padx=6, pady=2,
            command=self._set_as_start
        )
        btn_set_s.pack(side=tk.LEFT, padx=5)

        btn_set_e = tk.Button(
            setter_frame,
            text=u"✔ تحديد كنهاية (Set End)",
            font=("Arial", 9, "bold"),
            bg="#00587a", fg="#ffffff", padx=6, pady=2,
            command=self._set_as_end
        )
        btn_set_e.pack(side=tk.LEFT, padx=5)

        # Summary box
        sum_frame = tk.LabelFrame(self.root, text=u"الفترة المختارة (Selected Range)", font=("Arial", 9, "bold"), padx=8, pady=4)
        sum_frame.pack(fill=tk.X, padx=12, pady=4)

        row1 = tk.Frame(sum_frame)
        row1.pack(fill=tk.X, pady=2)
        tk.Label(row1, text=u"تاريخ البداية (Start Date):", width=22, anchor="w", font=("Arial", 9)).pack(side=tk.LEFT)
        self.start_entry = tk.Entry(row1, font=("Arial", 9, "bold"), width=16)
        self.start_entry.insert(0, self.start_date)
        self.start_entry.pack(side=tk.LEFT, padx=4)

        row2 = tk.Frame(sum_frame)
        row2.pack(fill=tk.X, pady=2)
        tk.Label(row2, text=u"تاريخ النهاية (End Date):", width=22, anchor="w", font=("Arial", 9)).pack(side=tk.LEFT)
        self.end_entry = tk.Entry(row2, font=("Arial", 9, "bold"), width=16)
        self.end_entry.insert(0, self.end_date)
        self.end_entry.pack(side=tk.LEFT, padx=4)

        # Confirm & Close buttons
        btn_bar = tk.Frame(self.root, padx=10, pady=8)
        btn_bar.pack(fill=tk.X)

        btn_apply = tk.Button(
            btn_bar,
            text=u"تأكيد وتطبيق في الأداة (Apply & Close)",
            font=("Arial", 10, "bold"),
            bg="#007acc", fg="#ffffff",
            padx=10, pady=4,
            command=self._on_apply
        )
        btn_apply.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=4)

        btn_cancel = tk.Button(
            btn_bar,
            text=u"إلغاء (Cancel)",
            font=("Arial", 10),
            padx=8, pady=4,
            command=self._on_cancel
        )
        btn_cancel.pack(side=tk.RIGHT, padx=4)

    def _refresh_calendar(self):
        for widget in self.cal_frame.winfo_children():
            widget.destroy()

        # Day name headers (Saturday to Friday)
        # Using calendar.setfirstweekday(calendar.SATURDAY)
        calendar.setfirstweekday(calendar.SATURDAY)
        day_names = [u"السبت\nSa", u"الأحد\nSu", u"الاثنين\nMo", u"الثلاثاء\nTu", u"الأربعاء\nWe", u"الخميس\nTh", u"الجمعة\nFr"]
        for col, dn in enumerate(day_names):
            lbl = tk.Label(
                self.cal_frame, text=dn, font=("Arial", 8, "bold"),
                bg="#eef2f7", fg="#333333", relief=tk.FLAT, pady=2
            )
            lbl.grid(row=0, column=col, sticky="nsew", padx=1, pady=1)

        weeks = calendar.monthcalendar(self.cur_year, self.cur_month)

        for row_i, week in enumerate(weeks):
            for col_i, day in enumerate(week):
                if day == 0:
                    lbl_empty = tk.Label(self.cal_frame, text="", bg="#ffffff")
                    lbl_empty.grid(row=row_i + 1, column=col_i, sticky="nsew", padx=1, pady=1)
                else:
                    is_sel = (
                        self.selected_date.year == self.cur_year and
                        self.selected_date.month == self.cur_month and
                        self.selected_date.day == day
                    )
                    btn_bg = "#007acc" if is_sel else "#f8f9fa"
                    btn_fg = "#ffffff" if is_sel else "#111111"
                    btn_day = tk.Button(
                        self.cal_frame,
                        text=str(day),
                        font=("Arial", 9, "bold" if is_sel else "normal"),
                        bg=btn_bg, fg=btn_fg,
                        relief=tk.RAISED if is_sel else tk.GROOVE,
                        bd=1,
                        command=lambda d=day: self._on_day_click(d)
                    )
                    btn_day.grid(row=row_i + 1, column=col_i, sticky="nsew", padx=1, pady=1)

        for i in range(7):
            self.cal_frame.grid_columnconfigure(i, weight=1)
        for i in range(len(weeks) + 1):
            self.cal_frame.grid_rowconfigure(i, weight=1)

    def _on_day_click(self, day):
        self.selected_date = datetime.date(self.cur_year, self.cur_month, day)
        self.sel_lbl.config(
            text=u"التاريخ المحدد: %02d/%02d/%04d" % (self.selected_date.day, self.selected_date.month, self.selected_date.year)
        )
        self._refresh_calendar()

    def _prev_month(self):
        if self.cur_month == 1:
            self.cur_month = 12
            self.cur_year -= 1
        else:
            self.cur_month -= 1
        self._sync_header()
        self._refresh_calendar()

    def _next_month(self):
        if self.cur_month == 12:
            self.cur_month = 1
            self.cur_year += 1
        else:
            self.cur_month += 1
        self._sync_header()
        self._refresh_calendar()

    def _prev_year(self):
        self.cur_year -= 1
        self._sync_header()
        self._refresh_calendar()

    def _next_year(self):
        self.cur_year += 1
        self._sync_header()
        self._refresh_calendar()

    def _on_month_change(self, event=None):
        m_name = self.month_var.get()
        if m_name in MONTH_NAMES:
            self.cur_month = MONTH_NAMES.index(m_name) + 1
            self._refresh_calendar()

    def _on_year_change(self, event=None):
        try:
            self.cur_year = int(self.year_var.get())
            self._refresh_calendar()
        except Exception:
            pass

    def _sync_header(self):
        self.month_var.set(MONTH_NAMES[self.cur_month - 1])
        self.year_var.set(str(self.cur_year))

    def _set_as_start(self):
        date_str = "%02d/%02d/%04d" % (self.selected_date.day, self.selected_date.month, self.selected_date.year)
        self.start_entry.delete(0, tk.END)
        self.start_entry.insert(0, date_str)

    def _set_as_end(self):
        date_str = "%02d/%02d/%04d" % (self.selected_date.day, self.selected_date.month, self.selected_date.year)
        self.end_entry.delete(0, tk.END)
        self.end_entry.insert(0, date_str)

    def _on_apply(self):
        self.result["start_date"] = self.start_entry.get().strip()
        self.result["end_date"] = self.end_entry.get().strip()
        self.result["applied"] = True
        self.root.destroy()

    def _on_cancel(self):
        self.result["applied"] = False
        self.root.destroy()


def open_calendar_picker(initial_start=None, initial_end=None):
    """Open the modal calendar dialog and return dict with start_date and end_date."""
    app = CalendarDialog(initial_start=initial_start, initial_end=initial_end)
    app.root.mainloop()
    return app.result


# Backward compatibility alias
show_calendar_dialog = open_calendar_picker


if __name__ == "__main__":
    import json
    import optparse
    parser = optparse.OptionParser()
    parser.add_option("--start", dest="start", default="01/01/2024")
    parser.add_option("--end", dest="end", default="31/12/2024")
    options, args = parser.parse_args()

    res = open_calendar_picker(options.start, options.end)
    sys.stdout.write(json.dumps(res))
