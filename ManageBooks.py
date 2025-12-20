from tkinter import *
from tkinter import messagebox
from tkinter import ttk
import mysql.connector

#-------------Return Book function-----------
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

    confirm = messagebox.askyesno(
        "Confirm Delete",
        "Are you sure you want to delete the selected book?"
    )

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
        messagebox.showerror("Database Error", str(err))  # This means book is already borrowed by student

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
        cursor.execute("SELECT isbn, title, author FROM tbl_books")
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

    if isbn == "" or title == "" or author == "":
        messagebox.showerror("Error", "All fields are required")
        return

    try:
        conn = connect_db()
        cursor = conn.cursor()

        query = "INSERT INTO tbl_books (isbn, title, author) VALUES (%s, %s, %s)"
        cursor.execute(query, (isbn, title, author))
        conn.commit()

        messagebox.showinfo("Success", "Book added successfully")

        entry_isbn.delete(0, END)
        entry_title.delete(0, END)
        entry_author.delete(0, END)

        load_books()  # refresh table

    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", str(err))

    finally:
        cursor.close()
        conn.close()

# ---------- GUI WINDOW ----------
def init_gui():
 global root
 root = Tk()
 root.title("Library Management System - Librarian Panel")
 root.geometry("800x600")
 root.resizable(False, False)

# ---------- HEADING ----------
 Label(root, text="Librarian Dashboard", font=("Arial", 18, "bold")).pack(pady=10)

# ---------- MAIN FRAME ----------
 main_frame = Frame(root)
 main_frame.pack(pady=10, fill=BOTH, expand=True)

# ---------- BOOK TABLE FRAME ----------
 table_frame = LabelFrame(main_frame, text="All Books", padx=10, pady=10, font=("Arial", 12, "bold"))
 table_frame.pack(fill=BOTH, padx=10, pady=10)

 columns = ("ISBN", "Title", "Author")
 global book_table
 book_table = ttk.Treeview(
    table_frame,
    columns=columns,
    show="headings",
    height=8
)

 for col in columns:
    book_table.heading(col, text=col)
    book_table.column(col, width=200 if col != "ISBN" else 120)

 book_table.pack(side=LEFT, fill=BOTH, expand=True)

 scrollbar = ttk.Scrollbar(table_frame, orient=VERTICAL, command=book_table.yview)
 book_table.configure(yscroll=scrollbar.set)
 scrollbar.pack(side=RIGHT, fill=Y)

# ---------- RETURN BOOK BUTTON ----------
 Button(table_frame,
       text="Return Book",
       font=("Arial", 11, "bold"),
       bg="green",
       fg="white",
       width=15,
       command=return_book
       ).pack(pady=10, padx=10, side=BOTTOM)

# ---------- ADD BOOK FRAME ----------
 global entry_isbn, entry_title, entry_author
 add_frame = LabelFrame(main_frame, text="Add New Book", padx=10, pady=10, font=("Arial", 12, "bold"))
 add_frame.pack(fill=BOTH, padx=10, pady=10)

 Label(add_frame, text="ISBN:", font=("Arial", 11)).grid(row=0, column=0, padx=10, pady=5, sticky=W)
 entry_isbn = Entry(add_frame, width=30)
 entry_isbn.grid(row=0, column=1, pady=5)

 Label(add_frame, text="Title:", font=("Arial", 11)).grid(row=1, column=0, padx=10, pady=5, sticky=W)
 entry_title = Entry(add_frame, width=30)
 entry_title.grid(row=1, column=1, pady=5)

 Label(add_frame, text="Author:", font=("Arial", 11)).grid(row=2, column=0, padx=10, pady=5, sticky=W)
 entry_author = Entry(add_frame, width=30)
 entry_author.grid(row=2, column=1, pady=5)

 btn_frame = Frame(add_frame)
 btn_frame.grid(row=3, column=0, columnspan=2, pady=15)

 Button(
    btn_frame,
    text="Add Book",
    font=("Arial", 11, "bold"),
    bg="green",
    fg="white",
    width=12,
    command=add_book
).pack(side=LEFT, padx=5)

 Button(
    btn_frame,
    text="Update",
    font=("Arial", 11, "bold"),
    bg="#1e90ff",
    fg="white",
    width=12
    #command=update_book
).pack(side=LEFT, padx=5)

 Button(
    btn_frame,
    text="Delete",
    font=("Arial", 11, "bold"),
    bg="red",
    fg="white",
    width=12,
    command=delete_book
).pack(side=LEFT, padx=5)


# ---------- LOAD BOOKS AT START ----------
 load_books()

 root.mainloop()
