from tkinter import *
from tkinter import ttk, messagebox
import mysql.connector

# ---------- THEME COLORS ----------
COLOR_BG = "#f0f2f5"
COLOR_PRIMARY = "#2c3e50"
COLOR_ACCENT = "#3498db"
COLOR_SUCCESS = "#27ae60"
COLOR_DANGER = "#e74c3c"
COLOR_WARNING = "#f39c12"

# Global variable to hold root to avoid reference errors
root = None

#----------go back --------------
def go_back_to_managebooks():
    # FIX: Destroy this window and call the init function of the previous window
    global root
    root.destroy()
    import ManageBooks 
    ManageBooks.init_gui()

# ---------- DATABASE CONNECTION ----------
def connect_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Sometimes@123",
        database="db_lms"
    )

# ---------- CLEAR SEARCH ----------
def clear_search():
    entry_student.delete(0, END)
    for row in borrowed_table.get_children():
        borrowed_table.delete(row)

# ---------- SEARCH STUDENT ----------
def search_student():
    name = entry_student.get().strip()
    if not name:
        messagebox.showwarning("Input Error", "Enter student name to search")
        return

    for row in borrowed_table.get_children():
        borrowed_table.delete(row)

    try:
        conn = connect_db()
        cursor = conn.cursor()
        query = """
            SELECT 
                bd.borrow_id,
                m.full_name,
                b.isbn,
                b.title,
                bd.borrow_date,
                DATEDIFF(CURDATE(), bd.borrow_date) AS days_borrowed
            FROM borrowdetail bd
            JOIN memberinfo m ON bd.mem_id = m.mem_id
            JOIN tbl_books b ON bd.isbn = b.isbn
            WHERE m.full_name LIKE %s
              AND bd.return_date IS NULL
        """
        cursor.execute(query, (f"%{name}%",))
        records = cursor.fetchall()

        if not records:
            messagebox.showinfo("No Records", "No borrowed books found for this student.")
            return

        for row in records:
            borrowed_table.insert("", END, values=row)

    except Exception as e:
        messagebox.showerror("Error", str(e))
    finally:
        cursor.close()
        conn.close()

# ---------- RETURN BOOK ----------
def return_book():
    selected = borrowed_table.selection()
    if not selected:
        messagebox.showwarning("No selection", "Select a book from the table to return")
        return

    confirm = messagebox.askyesno("Confirm Return", "Are you sure you want to mark this book as returned?")
    if not confirm:
        return

    item = borrowed_table.item(selected[0])["values"]
    borrow_id = item[0]

    try:
        conn = connect_db()
        cursor = conn.cursor()
        query = "UPDATE borrowdetail SET return_date = CURDATE() WHERE borrow_id = %s"
        cursor.execute(query, (borrow_id,))
        conn.commit()
        
        search_student() # Refresh table
        messagebox.showinfo("Success", "Book returned successfully")

    except Exception as e:
        messagebox.showerror("Error", str(e))
    finally:
        cursor.close()
        conn.close()

# ---------- GUI INITIALIZATION WRAPPER ----------
def init_gui():
    global root, entry_student, borrowed_table
    root = Tk()
    root.title("Library Management System - Return Book")
    root.geometry("1000x650")
    root.configure(bg=COLOR_BG)

    # Styling Treeview
    style = ttk.Style()
    style.theme_use("clam")
    style.configure("Treeview", background="#ffffff", foreground="black", rowheight=30, fieldbackground="#ffffff", font=("Arial", 10))
    style.configure("Treeview.Heading", font=("Arial", 10, "bold"), background="#e1e1e1")
    style.map("Treeview", background=[('selected', COLOR_ACCENT)])

    # Header
    header = Frame(root, bg=COLOR_PRIMARY, height=70)
    header.pack(fill=X)
    Label(header, text="RETURN BOOK MANAGEMENT", font=("Helvetica", 18, "bold"), fg="white", bg=COLOR_PRIMARY).pack(pady=15)

    # Main Container
    container = Frame(root, bg=COLOR_BG, padx=30, pady=20)
    container.pack(fill=BOTH, expand=True)

    # ---------- SEARCH SECTION ----------
    search_section = LabelFrame(container, text=" Search Borrowed Books ", font=("Arial", 11, "bold"), bg=COLOR_BG, padx=15, pady=15)
    search_section.pack(fill=X, pady=(0, 20))

    Label(search_section, text="Student Name:", font=("Arial", 10), bg=COLOR_BG).pack(side=LEFT, padx=5)
    entry_student = Entry(search_section, font=("Arial", 11), width=35, bd=1, relief=SOLID)
    entry_student.pack(side=LEFT, padx=10, ipady=4)

    # Action buttons within the search section
    Button(search_section, text="SEARCH", bg=COLOR_ACCENT, fg="white", font=("Arial", 9, "bold"), 
           command=search_student, width=12, cursor="hand2", bd=0).pack(side=LEFT, padx=5)

    Button(search_section, text="RESET", bg="#bdc3c7", fg="#2c3e50", font=("Arial", 9, "bold"), 
           command=clear_search, width=10, cursor="hand2", bd=0).pack(side=LEFT, padx=5)

    # ---------- TABLE SECTION ----------
    table_frame = Frame(container, bg=COLOR_BG)
    table_frame.pack(fill=BOTH, expand=True)

    columns = ("BORROW_ID", "Student Name", "ISBN", "Book Title", "Borrow Date", "Days Held")
    borrowed_table = ttk.Treeview(table_frame, columns=columns, show="headings")

    # Column Configurations
    borrowed_table.heading("BORROW_ID", text="ID")
    borrowed_table.column("BORROW_ID", width=50, anchor=CENTER)

    column_widths = {
        "Student Name": 180,
        "ISBN": 120,
        "Book Title": 280,
        "Borrow Date": 120,
        "Days Held": 100
    }

    for col, width in column_widths.items():
        borrowed_table.heading(col, text=col)
        borrowed_table.column(col, width=width, anchor=W if "Title" in col else CENTER)

    # Scrollbar
    scrollbar = ttk.Scrollbar(table_frame, orient=VERTICAL, command=borrowed_table.yview)
    borrowed_table.configure(yscrollcommand=scrollbar.set)

    borrowed_table.pack(side=LEFT, fill=BOTH, expand=True)
    scrollbar.pack(side=RIGHT, fill=Y)

    # ---------- ACTION BUTTONS ----------
    footer_frame = Frame(container, bg=COLOR_BG)
    footer_frame.pack(fill=X, pady=20)

    btn_config = {"font": ("Arial", 11, "bold"), "fg": "white", "width": 20, "pady": 8, "cursor": "hand2"}

    # Back button on the left, Return button on the right for balanced UI
    Button(footer_frame, text="⬅ BACK TO DASHBOARD", bg="#7f8c8d", command=go_back_to_managebooks, **btn_config).pack(side=LEFT)
    Button(footer_frame, text="CONFIRM RETURN", bg=COLOR_DANGER, command=return_book, **btn_config).pack(side=RIGHT)

    root.mainloop()

if __name__ == "__main__":
    init_gui()