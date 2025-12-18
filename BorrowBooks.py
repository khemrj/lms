from tkinter import *
from tkinter import messagebox
from tkinter import ttk
import mysql.connector

# ---------- DATABASE CONNECTION ----------
def connect_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Sometimes@123",
        database="db_lms"
    )

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
root = Tk()
root.title("Library Management System - Student portal")
root.geometry("700x500")
root.resizable(False, False)

# ---------- HEADING ----------
Label(root, text="Student Dashboard", font=("Arial", 18, "bold")).pack(pady=10)

# ---------- TABLE FRAME ----------
table_frame = Frame(root)
table_frame.pack(pady=10)

columns = ("ISBN", "Title", "Author")

book_table = ttk.Treeview(
    table_frame,
    columns=columns,
    show="headings",
    height=8
)
# available books matra dekhauxa hola
book_table.heading("ISBN", text="ISBN")
book_table.heading("Title", text="Title")
book_table.heading("Author", text="Author")

book_table.column("ISBN", width=120)
book_table.column("Title", width=300)
book_table.column("Author", width=200)

book_table.pack(side=LEFT)

scrollbar = ttk.Scrollbar(table_frame, orient=VERTICAL, command=book_table.yview)
book_table.configure(yscroll=scrollbar.set)
scrollbar.pack(side=RIGHT, fill=Y)

# ---------- ADD BOOK SECTION ----------
Label(root, text="Add New Book", font=("Arial", 14, "bold")).pack(pady=10)

form_frame = Frame(root)
form_frame.pack()

Label(form_frame, text="ISBN:", font=("Arial", 11)).grid(row=0, column=0, padx=10, pady=5, sticky=W)
entry_isbn = Entry(form_frame, width=30)
entry_isbn.grid(row=0, column=1)

Label(form_frame, text="Title:", font=("Arial", 11)).grid(row=1, column=0, padx=10, pady=5, sticky=W)
entry_title = Entry(form_frame, width=30)
entry_title.grid(row=1, column=1)

Label(form_frame, text="Author:", font=("Arial", 11)).grid(row=2, column=0, padx=10, pady=5, sticky=W)
entry_author = Entry(form_frame, width=30)
entry_author.grid(row=2, column=1)

Button(
    root,
    text="Borrow Book",
    font=("Arial", 11, "bold"),
    bg="green",
    fg="white",
    width=15,
    command=add_book
).pack(pady=15)

# ---------- LOAD BOOKS AT START ----------
load_books()

root.mainloop()
