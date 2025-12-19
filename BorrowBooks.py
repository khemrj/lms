from tkinter import *
from tkinter import messagebox
from tkinter import ttk
import mysql.connector
mem_id_global = None

#------------if clicked in a particular field-------------
def on_book_select(event):
    selected_item = book_table.selection()  # returns a tuple of selected item ids
    if selected_item:
        item_id = selected_item[0]  # get first selected item
        book_data = book_table.item(item_id)  # dictionary with "values"
        isbn, title, author = book_data["values"]
        print("ISBN:", isbn)
        print("Title:", title)
        print("Author:", author)

def start(mem_id):
    global mem_id_global  # tell Python we mean the global variable
    mem_id_global = mem_id
    print("member ID is now", mem_id_global)
    init_GUI()

# ---------- DATABASE CONNECTION ----------
def connect_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Sometimes@123",
        database="db_lms"
    )





# ------------ Borrow Book Function ---------
from datetime import date
from tkinter import messagebox

def borrow_book():
    print("member ID is ",mem_id_global)
    # Get selected row
    selected_item = book_table.selection()  # returns tuple of selected items
    if not selected_item:
        messagebox.showwarning("No selection", "Please select a book to borrow")
        return

    item_id = selected_item[0]
    book_data = book_table.item(item_id)["values"]
    isbn = book_data[0]  # first column is ISBN
    book_name = book_data[1]

    # Insert into DB
    try:
        conn = connect_db()
        cursor = conn.cursor()

        borrow_date = date.today()  # today's date
        print("before  insert query")
        query = """
            INSERT INTO borrowdetail(mem_id, isbn, borrow_date)
            VALUES (%s, %s, %s)
        """
        
        print("isbn is ")
        print(isbn)
        values = (mem_id_global, isbn, borrow_date)  # return_date is NULL initially

        cursor.execute(query, values)
        print("isbn is after query ",isbn)
        conn.commit()

        messagebox.showinfo("Success", f"Book {book_name} borrowed successfully!")

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

    
# ---------- GUI WINDOW ----------

def init_GUI():
 global root,book_table
 root = Tk()
 root.title("Library Management System - Student portal")
 root.geometry("700x500")
 root.resizable(False, False)

# ---------- HEADING ----------
 Label(root, text="Student Dashboard", font=("Arial", 18, "bold")).pack(pady=10)

# ---------- TABLE FRAME ----------
 global table_frame
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


 Button(
    root,
    text="Borrow Book",
    font=("Arial", 11, "bold"),
    bg="green",
    fg="white",
    width=15,
    command=borrow_book
).pack(pady=15)

# ---------- LOAD BOOKS AT START ----------
 load_books()
 book_table.bind("<ButtonRelease-1>", on_book_select)
 root.mainloop()
