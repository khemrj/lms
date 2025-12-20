from tkinter import *
from tkinter import messagebox
from tkinter import ttk
import mysql.connector
mem_id_global = None

#------------show borrowed books-----------
def show_borrowed_books(mem_id):
    """
    Shows borrowed books for a member with additional info:
    - Title
    - Borrow Date
    - Borrowed Days (difference between today and borrow date)
    """
    # Clear existing rows
    for row in borrowed_table.get_children():
        borrowed_table.delete(row)

    try:
        conn = connect_db()
        cursor = conn.cursor()

        query = """
            SELECT 
                t.title,
                b.borrow_date
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
            borrowed_days = (today - borrow_date).days  # difference in days
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

    # Clear table
    for row in book_table.get_children():
        book_table.delete(row)

    try:
        conn = connect_db()
        cursor = conn.cursor()

        query = """
            SELECT b.isbn, b.title, b.author FROM tbl_books b WHERE NOT EXISTS ( SELECT 1 FROM borrowdetail bd WHERE bd.isbn = b.isbn AND bd.return_date IS NULL)
            and title LIKE %s
        """
        cursor.execute(query, (f"%{keyword}%",))
        records = cursor.fetchall()

        for row in records:
            book_table.insert("", END, values=row)

    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", str(err))

    finally:
        cursor.close()
        conn.close()

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
        show_borrowed_books(mem_id_global)
        load_books()
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
        cursor.execute("SELECT b.isbn, b.title, b.author FROM tbl_books b WHERE NOT EXISTS ( SELECT 1 FROM borrowdetail bd WHERE bd.isbn = b.isbn AND bd.return_date IS NULL)")
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
 root.geometry("700x650")
 root.resizable(False, False)
# ---------- HEADING ----------
 Label(root, text="Student Dashboard", font=("Arial", 18, "bold")).pack(pady=10)

 # ---------- SEARCH SECTION ----------
 search_frame = Frame(root)
 search_frame.pack(pady=5)

 Label(search_frame, text="Search Book:", font=("Arial", 11)).pack(side=LEFT, padx=5)

 global search_entry
 search_entry = Entry(search_frame, width=30)
 search_entry.pack(side=LEFT, padx=5)
 search_entry.bind("<Return>", search_books)  # Enter key search

 Button(
     search_frame,
     text="Search",
     command=search_books,
     width=10
 ).pack(side=LEFT, padx=5)

 Button(
     search_frame,
     text="Back",
     command=go_back,
     width=8
 ).pack(side=LEFT, padx=10)

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
 # ---------- BORROWED BOOKS TABLE ----------
 Label(root, text="Borrowed Books", font=("Arial", 14, "bold")).pack(pady=(15, 5))

 borrowed_frame = Frame(root)
 borrowed_frame.pack()

 borrowed_columns = ("Book name", "Borrowed date", "Held for(days)")
 global borrowed_table
 borrowed_table = ttk.Treeview(
    borrowed_frame,
    columns=borrowed_columns,
    show="headings",
    height=6
)

 for col in borrowed_columns:
    borrowed_table.heading(col, text=col)
    borrowed_table.column(col, width=130)

 borrowed_table.pack(side=LEFT)

 borrowed_scroll = ttk.Scrollbar(
    borrowed_frame,
    orient=VERTICAL,
    command=borrowed_table.yview
)
 borrowed_table.configure(yscrollcommand=borrowed_scroll.set)
 borrowed_scroll.pack(side=RIGHT, fill=Y)
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
    command=borrow_book,
 ).pack(pady=15)

# ---------- LOAD BOOKS AT START ----------
 load_books()
 show_borrowed_books(mem_id_global)
 book_table.bind("<ButtonRelease-1>", on_book_select)
 root.mainloop()
