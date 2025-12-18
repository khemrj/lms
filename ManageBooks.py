from tkinter import *
from tkinter import messagebox
import mysql.connector

# ---------- DATABASE CONNECTION ----------
def connect_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",          # change if needed
        password="Sometimes@123",
        database="db_lms"
    )

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
        values = (isbn, title, author)

        cursor.execute(query, values)
        conn.commit()

        messagebox.showinfo("Success", "Book added successfully")

        # clear fields
        entry_isbn.delete(0, END)
        entry_title.delete(0, END)
        entry_author.delete(0, END)

    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", str(err))

    finally:
        cursor.close()
        conn.close()

# ---------- GUI WINDOW ----------
root = Tk()
root.title("Library Management System - Add Book")
root.geometry("400x300")
root.resizable(False, False)

# ---------- HEADING ----------
Label(root, text="Add New Book", font=("Arial", 16, "bold")).pack(pady=10)

# ---------- FORM FRAME ----------
frame = Frame(root)
frame.pack(pady=10)

Label(frame, text="ISBN:", font=("Arial", 11)).grid(row=0, column=0, padx=10, pady=5, sticky=W)
entry_isbn = Entry(frame, width=30)
entry_isbn.grid(row=0, column=1)

Label(frame, text="Title:", font=("Arial", 11)).grid(row=1, column=0, padx=10, pady=5, sticky=W)
entry_title = Entry(frame, width=30)
entry_title.grid(row=1, column=1)

Label(frame, text="Author:", font=("Arial", 11)).grid(row=2, column=0, padx=10, pady=5, sticky=W)
entry_author = Entry(frame, width=30)
entry_author.grid(row=2, column=1)

# ---------- BUTTON ----------
Button(
    root,
    text="Add Book",
    font=("Arial", 11, "bold"),
    bg="green",
    fg="white",
    width=15,
    command=add_book
).pack(pady=20)

root.mainloop()
