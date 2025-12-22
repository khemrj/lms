from tkinter import *
from tkinter import messagebox
from tkinter import ttk
import mysql.connector
from datetime import date

def logout():
    confirm = messagebox.askyesno("Confirm Logout", "Are you sure you want to log out?")
    if confirm:
        root.destroy()
        import First
        First.main()

# ---------- THEME COLORS ----------
COLOR_BG = "#f0f2f5"
COLOR_PRIMARY = "#2c3e50"
COLOR_ACCENT = "#3498db"
COLOR_SUCCESS = "#27ae60"
COLOR_DANGER = "#e74c3c"
COLOR_WARNING = "#f39c12"

mem_id_global = None

# ---------- DATABASE CONNECTION ----------
def connect_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Sometimes@123",
        database="db_lms"
    )

#------------show borrowed books-----------
def show_borrowed_books(mem_id):
    for row in borrowed_table.get_children():
        borrowed_table.delete(row)

    try:
        conn = connect_db()
        cursor = conn.cursor()
        query = """
            SELECT t.title, b.borrow_date
            FROM borrowdetail b
            JOIN tbl_books t ON b.isbn = t.isbn
            WHERE b.mem_id = %s and b.return_date IS NULL
            ORDER BY b.borrow_date DESC
        """
        cursor.execute(query, (mem_id,))
        records = cursor.fetchall()
        today = date.today()

        for row in records:
            title, borrow_date = row
            borrowed_days = (today - borrow_date).days
            borrowed_table.insert("", END, values=(title, borrow_date, borrowed_days))

    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", str(err))
    finally:
        cursor.close()
        conn.close()

#--------back to login jane code---------
def go_back():
    root.destroy()
    import First
    First.main() 

def search_books(event=None):
    keyword = search_entry.get().strip()
    for row in book_table.get_children():
        book_table.delete(row)

    try:
        conn = connect_db()
        cursor = conn.cursor()
        query = """
            SELECT b.isbn, b.title, b.author 
            FROM tbl_books b 
            WHERE b.title LIKE %s 
            AND NOT EXISTS (
                SELECT 1 FROM borrowdetail bd 
                WHERE bd.isbn = b.isbn AND bd.mem_id = %s AND bd.return_date IS NULL
            )
        """
        cursor.execute(query, (f"%{keyword}%", mem_id_global))
        records = cursor.fetchall()
        for row in records:
            book_table.insert("", END, values=row)
    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", str(err))
    finally:
        cursor.close()
        conn.close()

def start(mem_id):
    global mem_id_global
    mem_id_global = mem_id
    init_GUI()

# ------------ Borrow Book Function ---------
def borrow_book():
    selected_item = book_table.selection()
    if not selected_item:
        messagebox.showwarning("No selection", "Please select a book to borrow from the available list.")
        return

    item_id = selected_item[0]
    book_data = book_table.item(item_id)["values"]
    isbn = book_data[0]
    book_name = book_data[1]

    try:
        conn = connect_db()
        cursor = conn.cursor()
        borrow_date = date.today()
        query = "INSERT INTO borrowdetail(mem_id, isbn, borrow_date) VALUES (%s, %s, %s)"
        cursor.execute(query, (mem_id_global, isbn, borrow_date))
        conn.commit()

        show_borrowed_books(mem_id_global)
        load_books()
        messagebox.showinfo("Success", f"'{book_name}' has been added to your borrowed list!")
        
    except Exception as e:
        messagebox.showerror("Database Error", str(e))
    finally:
        cursor.close()
        conn.close()

# ---------- LOAD BOOKS INTO TABLE ----------
def load_books():
    for row in book_table.get_children():
        book_table.delete(row)
    try:
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT b.isbn, b.title, b.author 
            FROM tbl_books b 
            WHERE NOT EXISTS (
                SELECT 1 FROM borrowdetail bd 
                WHERE bd.isbn = b.isbn AND bd.return_date IS NULL
            )
        """)
        records = cursor.fetchall()
        for row in records:
            book_table.insert("", END, values=row)
    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", str(err))
    finally:
        cursor.close()
        conn.close()

# ---------- GUI WINDOW ----------
def init_GUI():
    global root, book_table, borrowed_table, search_entry
    root = Tk()
    root.title("Library Management System - Student Portal")
    root.geometry("1000x750")
    root.configure(bg=COLOR_BG)

    # Styling
    style = ttk.Style()
    style.theme_use("clam")
    style.configure("Treeview", background="#ffffff", foreground="black", rowheight=28, fieldbackground="#ffffff", font=("Arial", 10))
    style.configure("Treeview.Heading", font=("Arial", 10, "bold"), background="#e1e1e1")
    style.map("Treeview", background=[('selected', COLOR_ACCENT)])

    # Header
    header = Frame(root, bg=COLOR_PRIMARY, height=80)
    header.pack(fill=X)
    Label(header, text="STUDENT DASHBOARD", font=("Helvetica", 20, "bold"), fg="white", bg=COLOR_PRIMARY).pack(pady=20)

    # Main Content Area
    main_container = Frame(root, bg=COLOR_BG, padx=20, pady=10)
    main_container.pack(fill=BOTH, expand=True)

    # ---------- SEARCH & NAV SECTION ----------
    nav_frame = Frame(main_container, bg=COLOR_BG)
    nav_frame.pack(fill=X, pady=10)

    Label(nav_frame, text="Search Library:", font=("Arial", 11, "bold"), bg=COLOR_BG).pack(side=LEFT, padx=5)
    search_entry = Entry(nav_frame, font=("Arial", 11), width=40)
    search_entry.pack(side=LEFT, padx=5, ipady=3)
    search_entry.bind("<Return>", search_books)

    Button(nav_frame, text="Search", bg=COLOR_ACCENT, fg="white", font=("Arial", 9, "bold"), 
           command=search_books, width=12, cursor="hand2").pack(side=LEFT, padx=5)
    
    Button(nav_frame, text="Logout", bg=COLOR_DANGER, fg="white", font=("Arial", 9, "bold"), 
           command=go_back, width=12, cursor="hand2").pack(side=RIGHT, padx=5)

    # ---------- AVAILABLE BOOKS TABLE ----------
    available_label_frame = LabelFrame(main_container, text=" Available for Borrowing ", font=("Arial", 11, "bold"), bg=COLOR_BG, padx=10, pady=10)
    available_label_frame.pack(fill=BOTH, expand=True, pady=10)

    columns = ("ISBN", "Title", "Author")
    book_table = ttk.Treeview(available_label_frame, columns=columns, show="headings", height=8)
    
    book_table.heading("ISBN", text="ISBN")
    book_table.heading("Title", text="Book Title")
    book_table.heading("Author", text="Author")
    
    book_table.column("ISBN", width=120, anchor=CENTER)
    book_table.column("Title", width=400)
    book_table.column("Author", width=250)

    available_scroll = ttk.Scrollbar(available_label_frame, orient=VERTICAL, command=book_table.yview)
    book_table.configure(yscrollcommand=available_scroll.set)
    
    book_table.pack(side=LEFT, fill=BOTH, expand=True)
    available_scroll.pack(side=RIGHT, fill=Y)

    # Borrow Button (Center)
    Button(main_container, text="BORROW SELECTED BOOK", bg=COLOR_SUCCESS, fg="white", 
           font=("Arial", 11, "bold"), width=30, pady=10, command=borrow_book, cursor="hand2").pack(pady=10)

    # ---------- BORROWED BOOKS TABLE ----------
    borrowed_label_frame = LabelFrame(main_container, text=" My Borrowed Books ", font=("Arial", 11, "bold"), bg=COLOR_BG, padx=10, pady=10)
    borrowed_label_frame.pack(fill=BOTH, expand=True, pady=10)

    borrowed_columns = ("Book Name", "Borrowed Date", "Days Held")
    borrowed_table = ttk.Treeview(borrowed_label_frame, columns=borrowed_columns, show="headings", height=6)

    borrowed_table.heading("Book Name", text="Book Name")
    borrowed_table.heading("Borrowed Date", text="Borrowed Date")
    borrowed_table.heading("Days Held", text="Days Held")

    borrowed_table.column("Book Name", width=400)
    borrowed_table.column("Borrowed Date", width=200, anchor=CENTER)
    borrowed_table.column("Days Held", width=150, anchor=CENTER)

    borrowed_scroll = ttk.Scrollbar(borrowed_label_frame, orient=VERTICAL, command=borrowed_table.yview)
    borrowed_table.configure(yscrollcommand=borrowed_scroll.set)
    
    borrowed_table.pack(side=LEFT, fill=BOTH, expand=True)
    borrowed_scroll.pack(side=RIGHT, fill=Y)

    # ---------- INITIAL LOAD ----------
    load_books()
    show_borrowed_books(mem_id_global)
    
    root.mainloop()