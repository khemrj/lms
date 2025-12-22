from tkinter import *
from tkinter import messagebox
from tkinter import ttk
import mysql.connector

# ---------- THEME COLORS ----------
COLOR_BG = "#f0f2f5"
COLOR_PRIMARY = "#2c3e50"
COLOR_ACCENT = "#3498db"
COLOR_SUCCESS = "#27ae60"
COLOR_DANGER = "#e74c3c"
COLOR_WARNING = "#f39c12"

# ---------- LOGOUT FUNCTION ----------
def logout():
    confirm = messagebox.askyesno("Confirm Logout", "Are you sure you want to log out?")
    if confirm:
        root.destroy()
        import First
        First.main()

# ---------- SEARCH FUNCTION ----------
def search_books():
    query_str = entry_search.get().strip()
    for row in book_table.get_children():
        book_table.delete(row)
    
    try:
        conn = connect_db()
        cursor = conn.cursor()
        sql = "SELECT isbn, title, author, quantity FROM tbl_books WHERE title LIKE %s OR author LIKE %s OR isbn LIKE %s"
        val = (f"%{query_str}%", f"%{query_str}%", f"%{query_str}%")
        cursor.execute(sql, val)
        records = cursor.fetchall()
        for row in records:
            book_table.insert("", END, values=row)
    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", str(err))
    finally:
        cursor.close()
        conn.close()

# ---------- Clear Entries Function ----------
def clear_entries():
    entry_isbn.config(state="normal")
    entry_isbn.delete(0, END)
    entry_title.delete(0, END)
    entry_author.delete(0, END)
    entry_quantity.delete(0, END)
    # Note: We keep the search entry separate for better UX
    load_books()

# ---------- FILL ENTRIES WHEN A ROW IS CLICKED ----------
def fill_entries(event):
    selected_item = book_table.selection()
    if selected_item:
        item = book_table.item(selected_item[0])
        values = item["values"]
        if values:
            entry_isbn.config(state="normal")
            entry_isbn.delete(0, END)
            entry_isbn.insert(0, values[0])
            entry_isbn.config(state="readonly")

            entry_title.delete(0, END)
            entry_title.insert(0, values[1])

            entry_author.delete(0, END)
            entry_author.insert(0, values[2])

            entry_quantity.delete(0, END)
            entry_quantity.insert(0, values[3])

# -------------Return Book function-----------
def return_book():
    root.withdraw()
    import ReturnBook

# ---------- DATABASE CONNECTION ----------
def connect_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Sometimes@123",
        database="db_lms"
    )

#--------------Delete book function---------------
def delete_book():
    selected_item = book_table.selection()
    if not selected_item:
        messagebox.showwarning("No Selection", "Please select a book to delete")
        return
    confirm = messagebox.askyesno("Confirm Delete", "Are you sure you want to delete the selected book?")
    if not confirm:
        return
    isbn = book_table.item(selected_item[0])["values"][0]
    try:
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM tbl_books WHERE isbn = %s", (isbn,))
        conn.commit()
        messagebox.showinfo("Success", "Book deleted successfully")
        load_books()
    except mysql.connector.Error as err:
        messagebox.showerror("Error", "The book has been borrowed and cannot be deleted")
    finally:
        cursor.close()
        conn.close()

# ---------- UPDATE BOOK FUNCTION ----------
def update_book():
    selected_items = book_table.selection()
    if not selected_items:
        messagebox.showwarning("No Selection", "Please select a book to update")
        return

    isbn = entry_isbn.get().strip()
    title = entry_title.get().strip()
    author = entry_author.get().strip()
    quantity = entry_quantity.get().strip()

    if not (isbn and title and author and quantity):
        messagebox.showerror("Error", "All fields are required")
        return

    try:
        conn = connect_db()
        cursor = conn.cursor()
        query = "UPDATE tbl_books SET title=%s, author=%s, quantity=%s WHERE isbn=%s"
        cursor.execute(query, (title, author, int(quantity), isbn))
        conn.commit()
        load_books()
        messagebox.showinfo("Success", "Book updated successfully")
    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", str(err))
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
        cursor.execute("SELECT isbn, title, author, quantity FROM tbl_books order by title")
        records = cursor.fetchall()
        for row in records:
            book_table.insert("", END, values=row)
    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", str(err))
    finally:
        cursor.close()
        conn.close()

# ---------- ADD BOOK FUNCTION ----------
def add_book():
    isbn = entry_isbn.get()
    title = entry_title.get()
    author = entry_author.get()
    quantity = entry_quantity.get()

    if isbn == "" or title == "" or author == "":
        messagebox.showerror("Error", "All fields are required")
        return

    try:
        conn = connect_db()
        cursor = conn.cursor()
        query = "INSERT INTO tbl_books (isbn, title, author, quantity) VALUES (%s, %s, %s, %s)"
        cursor.execute(query, (isbn, title, author, quantity))
        conn.commit()
        messagebox.showinfo("Success", "Book added successfully")
        clear_entries()
        load_books()
    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", str(err))
    finally:
        cursor.close()
        conn.close()

# ---------- GUI WINDOW ----------
def init_gui():
    global root, book_table, entry_isbn, entry_title, entry_author, entry_quantity, entry_search
    root = Tk()
    root.title("Library Management System")
    root.geometry("1000x700")
    root.configure(bg=COLOR_BG)

    style = ttk.Style()
    style.theme_use("clam")
    style.configure("Treeview", background="#ffffff", foreground="black", rowheight=28, fieldbackground="#ffffff", font=("Arial", 10))
    style.configure("Treeview.Heading", font=("Arial", 10, "bold"), background="#e1e1e1")
    style.map("Treeview", background=[('selected', COLOR_ACCENT)])

    # Header
    header = Frame(root, bg=COLOR_PRIMARY, height=80)
    header.pack(fill=X)
    Label(header, text="LIBRARIAN DASHBOARD", font=("Helvetica", 20, "bold"), fg="white", bg=COLOR_PRIMARY).pack(pady=20)

    # Left Side: Management Form
    left_frame = Frame(root, bg=COLOR_BG, padx=20, pady=20)
    left_frame.pack(side=LEFT, fill=Y)

    # --- UPDATED FORM AREA ---
    form_frame = LabelFrame(left_frame, text=" Book Details ", font=("Arial", 12, "bold"), bg=COLOR_BG, padx=15, pady=10)
    form_frame.pack(fill=X)

    # Small Clear Button placed inside the form header area using a clever grid trick
    Button(form_frame, text="Reset Form", font=("Arial", 8, "bold"), bg="#bdc3c7", fg="#2c3e50", 
           command=clear_entries, cursor="hand2", bd=0, padx=5).grid(row=0, column=2, sticky=E)

    Label(form_frame, text="ISBN:", font=("Arial", 10), bg=COLOR_BG).grid(row=1, column=0, sticky=W, pady=8)
    entry_isbn = Entry(form_frame, width=25, font=("Arial", 10))
    entry_isbn.grid(row=1, column=1, pady=8, padx=5)
    
    Label(form_frame, text="Book Title:", font=("Arial", 10), bg=COLOR_BG).grid(row=2, column=0, sticky=W, pady=8)
    entry_title = Entry(form_frame, width=25, font=("Arial", 10))
    entry_title.grid(row=2, column=1, pady=8, padx=5)
    
    Label(form_frame, text="Author:", font=("Arial", 10), bg=COLOR_BG).grid(row=3, column=0, sticky=W, pady=8)
    entry_author = Entry(form_frame, width=25, font=("Arial", 10))
    entry_author.grid(row=3, column=1, pady=8, padx=5)
    
    Label(form_frame, text="Quantity:", font=("Arial", 10), bg=COLOR_BG).grid(row=4, column=0, sticky=W, pady=8)
    entry_quantity = Entry(form_frame, width=25, font=("Arial", 10))
    entry_quantity.grid(row=4, column=1, pady=8, padx=5)

    # Actions Frame
    actions_frame = Frame(left_frame, bg=COLOR_BG)
    actions_frame.pack(pady=10, fill=X)

    btn_config = {"font": ("Arial", 10, "bold"), "fg": "white", "width": 20, "pady": 8, "cursor": "hand2", "bd": 0}
    
    Button(actions_frame, text="ADD NEW BOOK", bg=COLOR_SUCCESS, command=add_book, **btn_config).pack(pady=5)
    Button(actions_frame, text="UPDATE SELECTED", bg=COLOR_ACCENT, command=update_book, **btn_config).pack(pady=5)
    Button(actions_frame, text="DELETE FROM RECORD", bg=COLOR_DANGER, command=delete_book, **btn_config).pack(pady=5)
    
    # Visual separator
    Frame(actions_frame, height=2, bg="#dcdde1").pack(fill=X, pady=15)
    
    Button(actions_frame, text="RETURN BOOK PANEL", bg=COLOR_PRIMARY, command=return_book, **btn_config).pack(pady=5)
    Button(actions_frame, text="LOG OUT", bg="#7f8c8d", command=logout, **btn_config).pack(pady=(20, 5))

    # Right Side: Table View + Search
    right_frame = Frame(root, bg=COLOR_BG, padx=20, pady=20)
    right_frame.pack(side=RIGHT, fill=BOTH, expand=True)

    # Search Bar Section
    search_frame = Frame(right_frame, bg=COLOR_BG)
    search_frame.pack(fill=X, pady=(0, 15))
    
    Label(search_frame, text="Search Inventory:", font=("Arial", 10, "bold"), bg=COLOR_BG).pack(side=LEFT, padx=5)
    entry_search = Entry(search_frame, font=("Arial", 11), width=35)
    entry_search.pack(side=LEFT, padx=5, ipady=3)
    
    Button(search_frame, text="Search", bg=COLOR_ACCENT, fg="white", font=("Arial", 9, "bold"), 
           command=search_books, width=10).pack(side=LEFT, padx=5)
    Button(search_frame, text="Refresh", bg="#95a5a6", fg="white", font=("Arial", 9, "bold"), 
           command=load_books, width=10).pack(side=LEFT)

    table_container = LabelFrame(right_frame, text=" Inventory Overview ", font=("Arial", 11, "bold"), bg=COLOR_BG)
    table_container.pack(fill=BOTH, expand=True)

    columns = ("ISBN", "Title", "Author", "Qty")
    book_table = ttk.Treeview(table_container, columns=columns, show="headings")
    
    for col in columns:
        book_table.heading(col, text=col)
    
    book_table.column("ISBN", width=120, anchor=CENTER)
    book_table.column("Title", width=250)
    book_table.column("Author", width=150)
    book_table.column("Qty", width=60, anchor=CENTER)

    scrollbar = ttk.Scrollbar(table_container, orient=VERTICAL, command=book_table.yview)
    book_table.configure(yscroll=scrollbar.set)
    
    book_table.pack(side=LEFT, fill=BOTH, expand=True, padx=5, pady=5)
    scrollbar.pack(side=RIGHT, fill=Y)

    book_table.bind("<<TreeviewSelect>>", fill_entries)

    load_books()
    root.mainloop()

if __name__ == "__main__":
    init_gui()