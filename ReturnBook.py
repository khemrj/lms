from tkinter import *
from tkinter import ttk, messagebox
import mysql.connector
from datetime import date

#----------go back --------------
def go_back_to_managebooks():
    root.withdraw()          # close ReturnBook window
    import ManageBooks
    ManageBooks.init_gui()
     # or pass mem_id if needed


# ---------- DATABASE CONNECTION ----------
def connect_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Sometimes@123",
        database="db_lms"
    )

# ---------- SEARCH STUDENT ----------
def search_student():
    name = entry_student.get().strip()

    if not name:
        messagebox.showwarning("Input Error", "Enter student name")
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
            messagebox.showinfo("No Records", "No borrowed books found")
            return

        for row in records:
            borrowed_table.insert("", END, values=row)

    except Exception as e:
        messagebox.showerror("Error", str(e))

    finally:
        cursor.close()
        conn.close()
8
# ---------- RETURN BOOK ----------
def return_book():
    selected = borrowed_table.selection()

    if not selected:
        messagebox.showwarning("No selection", "Select a book to return")
        return

    confirm = messagebox.askyesno(
        "Confirm Return",
        "Are you sure you want to return this book?"
    )

    if not confirm:
        return

    item = borrowed_table.item(selected[0])["values"]
    borrow_id = item[0]

    try:
        conn = connect_db()
        cursor = conn.cursor()

        query = """
            UPDATE borrowdetail
            SET return_date = CURDATE()
            WHERE borrow_id = %s
        """

        cursor.execute(query, (borrow_id,))
        conn.commit()

        messagebox.showinfo("Success", "Book returned successfully")
        search_student()  # refresh table

    except Exception as e:
        messagebox.showerror("Error", str(e))

    finally:
        cursor.close()
        conn.close()


# ---------- GUI ----------
root = Tk()
root.title("Library Management System - Return Book")
root.geometry("900x520")
root.resizable(False, False)

# ---------- MAIN CONTAINER ----------
main_frame = Frame(root, padx=20, pady=10)
main_frame.pack(fill=BOTH, expand=True)

Label(
    main_frame,
    text="Return Borrowed Books",
    font=("Arial", 18, "bold")
).pack(pady=10)

# ---------- SEARCH FRAME ----------
search_frame = LabelFrame(
    main_frame,
    text="Search Student",
    font=("Arial", 12, "bold"),
    padx=10,
    pady=10
)
search_frame.pack(fill=X, pady=10)

Label(search_frame, text="Student Name:", font=("Arial", 11)).grid(row=0, column=0, padx=5, pady=5, sticky=W)

entry_student = Entry(search_frame, width=30)
entry_student.grid(row=0, column=1, padx=5, pady=5)

Button(
    search_frame,
    text="Search",
    width=12,
    bg="green",
    fg="white",
    command=search_student
).grid(row=0, column=2, padx=10)

# ---------- TABLE FRAME ----------
table_frame = LabelFrame(
    main_frame,
    text="Borrowed Books",
    font=("Arial", 12, "bold"),
    padx=10,
    pady=10
)
table_frame.pack(fill=BOTH, expand=True, pady=10)

columns = ("BORROW_ID", "Student", "ISBN", "Title", "Borrow Date", "Days Borrowed")

borrowed_table = ttk.Treeview(
    table_frame,
    columns=columns,
    show="headings",
    height=10
)

borrowed_table.heading("BORROW_ID", text="ID")
borrowed_table.column("BORROW_ID", width=0, stretch=False)

for col, w in {
    "Student":150,
    "ISBN":120,
    "Title":250,
    "Borrow Date":120,
    "Days Borrowed":120
}.items():
    borrowed_table.heading(col, text=col)
    borrowed_table.column(col, width=w)

borrowed_table.pack(side=LEFT, fill=BOTH, expand=True)

scrollbar = ttk.Scrollbar(table_frame, orient=VERTICAL, command=borrowed_table.yview)
borrowed_table.configure(yscrollcommand=scrollbar.set)
scrollbar.pack(side=RIGHT, fill=Y)

# ---------- ACTION BUTTONS ----------
btn_frame = Frame(main_frame)
btn_frame.pack(pady=15)

Button(
    btn_frame,
    text="Return Book",
    font=("Arial", 12, "bold"),
    bg="red",
    fg="white",
    width=18,
    command=return_book
).grid(row=0, column=0, padx=10)

Button(
    btn_frame,
    text="⬅ Back",
    font=("Arial", 12, "bold"),
    bg="gray",
    fg="white",
    width=18,
    command=go_back_to_managebooks
).grid(row=0, column=1, padx=10)

root.mainloop()
