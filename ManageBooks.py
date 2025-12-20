from tkinter import *
from tkinter import messagebox
from tkinter import ttk
import mysql.connector

# ---------- Clear Entries Function ----------
def clear_entries():
    entry_isbn.config(state="normal")  # make editable when clearing
    entry_isbn.delete(0, END)
    entry_title.delete(0, END)
    entry_author.delete(0, END)
    entry_quantity.delete(0, END)

# ---------- FILL ENTRIES WHEN A ROW IS CLICKED ----------
def fill_entries(event):
    selected_item = book_table.selection()
    if selected_item:
        item = book_table.item(selected_item[0])
        values = item["values"]
        if values:
            entry_isbn.config(state="normal")  # temporarily enable to set value
            entry_isbn.delete(0, END)
            entry_isbn.insert(0, values[0])
            entry_isbn.config(state="readonly")

            entry_title.delete(0, END)
            entry_title.insert(0, values[1])

            entry_author.delete(0, END)
            entry_author.insert(0, values[2])

            entry_quantity.delete(0, END)
            entry_quantity.insert(0, values[3])

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
        messagebox.showerror("Cannnot delete book ; it is borrowed ", str(err))  # This means book is already borrowed by student

    finally:
        cursor.close()
        conn.close()

# ---------- UPDATE BOOK FUNCTION ----------
def update_book():
    # Get selected book from table
    selected_items = book_table.selection()
    if not selected_items:
        messagebox.showwarning("No Selection", "Please select a book to update")
        return

    selected_item = selected_items[0]
    selected_values = book_table.item(selected_item)["values"]
    isbn_original, title_original, author_original, quantity_original = selected_values

    # Get current entry values
    isbn = entry_isbn.get().strip()
    title = entry_title.get().strip()
    author = entry_author.get().strip()
    quantity = entry_quantity.get().strip()
    quantity = int(quantity)

    # Check if any changes were made
    if (isbn, title, author, quantity) == (isbn_original, title_original, author_original, quantity_original):
        messagebox.showinfo("Info", "Please make changes before updating — Nothing to update")
        return

    # Check if all fields are filled
    if not (isbn and title and author and quantity):
        messagebox.showerror("Error", "All fields are required")
        return

    # Update the book in database
    try:
        conn = connect_db()
        cursor = conn.cursor()
        query = """
            UPDATE tbl_books
            SET title=%s, author=%s, quantity=%s
            WHERE isbn=%s
        """
        cursor.execute(query, (title, author, quantity, isbn))
        conn.commit()

        load_books()  # refresh table
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

        query = "INSERT INTO tbl_books (isbn, title, author,quantity) VALUES (%s, %s, %s,%s)"
        cursor.execute(query, (isbn, title, author,quantity))
        conn.commit()

        messagebox.showinfo("Success", "Book added successfully")

        entry_isbn.delete(0, END)
        entry_title.delete(0, END)
        entry_author.delete(0, END)
        entry_quantity.delete(0,END)

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

 #table + scrollbar frame
 table_inner_frame = Frame(table_frame)
 table_inner_frame.pack(fill=BOTH, expand=True)

 columns = ("ISBN", "Title", "Author","Quantity")
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

 book_table.bind("<<TreeviewSelect>>", fill_entries)

# ---------- RETURN BOOK BUTTON ----------
 Button(main_frame,
       text="Return Book",
       font=("Arial", 11, "bold"),
       bg="green",
       fg="white",
       width=15,
       command=return_book
       ).pack(pady=10, padx=10, side=BOTTOM)

# ---------- ADD BOOK FRAME ----------
 global entry_isbn, entry_title, entry_author,entry_quantity
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

 Label(add_frame, text="Quantity:", font=("Arial", 11)).grid(row=3, column=0, padx=10, pady=5, sticky=W)
 entry_quantity = Entry(add_frame, width=30)
 entry_quantity.grid(row=3, column=1, pady=5)

 btn_frame = Frame(add_frame)
 btn_frame.grid(row=4, column=0, columnspan=2, pady=15)

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
    width=12,
    command=update_book
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

 Button(btn_frame, text="Clear Fields", font=("Arial", 11, "bold"), bg="orange", fg="white",
       width=12, command=lambda: clear_entries()).pack(side=LEFT, padx=5)


# ---------- LOAD BOOKS AT START ----------
 load_books()
 root.mainloop()
