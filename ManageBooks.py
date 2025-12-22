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
    
    lbl_err_isbn.config(text="")
    lbl_err_title.config(text="")
    lbl_err_author.config(text="")
    lbl_err_qty.config(text="")
    
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
            
            lbl_err_isbn.config(text="")
            lbl_err_title.config(text="")
            lbl_err_author.config(text="")
            lbl_err_qty.config(text="")

# -------------Return Book function-----------
def return_book():
    root.destroy()
    import ReturnBook
    ReturnBook.init_gui()

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
    isbn = entry_isbn.get().strip()
    title = entry_title.get().strip()
    author = entry_author.get().strip()
    quantity = entry_quantity.get().strip()

    lbl_err_isbn.config(text="")
    lbl_err_title.config(text="")
    lbl_err_author.config(text="")
    lbl_err_qty.config(text="")

    is_valid = True
    if not isbn:
        lbl_err_isbn.config(text="* Required")
        is_valid = False
    if not title:
        lbl_err_title.config(text="* Required")
        is_valid = False
    if not author:
        lbl_err_author.config(text="* Required")
        is_valid = False
    if not quantity:
        lbl_err_qty.config(text="* Required")
        is_valid = False

    if not is_valid: return

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
    global lbl_err_isbn, lbl_err_title, lbl_err_author, lbl_err_qty

    root = Tk()
    root.title("Library Management System")
    root.geometry("1100x780") # Increased height slightly for better fit
    root.configure(bg=COLOR_BG)

    style = ttk.Style()
    style.theme_use("clam")
    style.configure("Treeview", background="#ffffff", foreground="black", rowheight=28, fieldbackground="#ffffff", font=("Arial", 10))
    style.configure("Treeview.Heading", font=("Arial", 10, "bold"), background="#e1e1e1")

    header = Frame(root, bg=COLOR_PRIMARY, height=70)
    header.pack(fill=X)
    Label(header, text="LIBRARIAN DASHBOARD", font=("Helvetica", 18, "bold"), fg="white", bg=COLOR_PRIMARY).pack(pady=15)

    left_frame = Frame(root, bg=COLOR_BG, padx=20, pady=10)
    left_frame.pack(side=LEFT, fill=Y)

    form_frame = LabelFrame(left_frame, text=" Book Details ", font=("Arial", 11, "bold"), bg=COLOR_BG, padx=15, pady=5)
    form_frame.pack(fill=X)

    # Mini Reset Button
    Button(form_frame, text="Reset", font=("Arial", 8), bg="#bdc3c7", fg="#2c3e50", 
           command=clear_entries, cursor="hand2", bd=0).grid(row=0, column=1, sticky=E)

    # --- COMPACT GRID ---
    def add_compact_field(label_text, row_idx):
        Label(form_frame, text=label_text, font=("Arial", 9), bg=COLOR_BG).grid(row=row_idx, column=0, sticky=W, pady=(2,0))
        entry = Entry(form_frame, width=28, font=("Arial", 10))
        entry.grid(row=row_idx+1, column=0, columnspan=2, sticky=W)
        err_lbl = Label(form_frame, text="", font=("Arial", 7), fg=COLOR_DANGER, bg=COLOR_BG)
        err_lbl.grid(row=row_idx+2, column=0, sticky=W)
        return entry, err_lbl

    entry_isbn, lbl_err_isbn = add_compact_field("ISBN:", 1)
    entry_title, lbl_err_title = add_compact_field("Book Title:", 4)
    entry_author, lbl_err_author = add_compact_field("Author:", 7)
    entry_quantity, lbl_err_qty = add_compact_field("Quantity:", 10)

    # Actions Frame
    actions_frame = Frame(left_frame, bg=COLOR_BG)
    actions_frame.pack(pady=5, fill=X)

    btn_config = {"font": ("Arial", 9, "bold"), "fg": "white", "width": 22, "pady": 6, "cursor": "hand2", "bd": 0}
    
    Button(actions_frame, text="ADD NEW BOOK", bg=COLOR_SUCCESS, command=add_book, **btn_config).pack(pady=3)
    Button(actions_frame, text="UPDATE SELECTED", bg=COLOR_ACCENT, command=update_book, **btn_config).pack(pady=3)
    Button(actions_frame, text="DELETE FROM RECORD", bg=COLOR_DANGER, command=delete_book, **btn_config).pack(pady=3)
    
    Frame(actions_frame, height=1, bg="#dcdde1").pack(fill=X, pady=10)
    
    Button(actions_frame, text="RETURN BOOK PANEL", bg=COLOR_PRIMARY, command=return_book, **btn_config).pack(pady=3)
    Button(actions_frame, text="LOG OUT", bg="#7f8c8d", command=logout, **btn_config).pack(pady=(15, 0))

    # Right Side
    right_frame = Frame(root, bg=COLOR_BG, padx=20, pady=20)
    right_frame.pack(side=RIGHT, fill=BOTH, expand=True)

    search_frame = Frame(right_frame, bg=COLOR_BG)
    search_frame.pack(fill=X, pady=(0, 10))
    Label(search_frame, text="Search:", font=("Arial", 9, "bold"), bg=COLOR_BG).pack(side=LEFT, padx=5)
    entry_search = Entry(search_frame, font=("Arial", 10), width=30)
    entry_search.pack(side=LEFT, padx=5)
    Button(search_frame, text="Search", bg=COLOR_ACCENT, fg="white", font=("Arial", 8, "bold"), command=search_books, width=8).pack(side=LEFT, padx=2)
    Button(search_frame, text="Refresh", bg="#95a5a6", fg="white", font=("Arial", 8, "bold"), command=load_books, width=8).pack(side=LEFT)

    table_container = LabelFrame(right_frame, text=" Inventory Overview ", font=("Arial", 11, "bold"), bg=COLOR_BG)
    table_container.pack(fill=BOTH, expand=True)

    columns = ("ISBN", "Title", "Author", "Qty")
    book_table = ttk.Treeview(table_container, columns=columns, show="headings")
    for col in columns: book_table.heading(col, text=col)
    
    book_table.column("ISBN", width=100, anchor=CENTER)
    book_table.column("Title", width=220)
    book_table.column("Author", width=130)
    book_table.column("Qty", width=50, anchor=CENTER)

    scrollbar = ttk.Scrollbar(table_container, orient=VERTICAL, command=book_table.yview)
    book_table.configure(yscroll=scrollbar.set)
    book_table.pack(side=LEFT, fill=BOTH, expand=True, padx=5, pady=5)
    scrollbar.pack(side=RIGHT, fill=Y)

    book_table.bind("<<TreeviewSelect>>", fill_entries)
    load_books()
    root.mainloop()

if __name__ == "__main__":
    init_gui()