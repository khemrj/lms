from tkinter import *
from tkinter import messagebox
import mysql.connector

#--------------------database connection-------------
def connect_db(): 
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Sometimes@123",
        database="db_lms"
    )

def open_admin_window(mem_id):
    import ManageBooks
    ManageBooks.init_gui()   

def open_student_window(mem_id):
    import BorrowBooks
    print("inside open_student_window function")
    print("login ma memId is ", mem_id)
    BorrowBooks.start(mem_id)

# ------------------ Main Window ------------------
root = Tk()
root.title("Library Management System")
root.geometry("450x350")
root.resizable(False, False)
root.configure(bg="#f4f1ec")

# ------------------ Header ------------------
header = Label(
    root,
    text="Library Management System",
    font=("Arial", 16, "bold"),
    bg="#2c3e50",
    fg="white",
    pady=10
)
header.pack(fill=X)

# ------------------ Main Frame ------------------
frame = Frame(root, bg="#f4f1ec", padx=30, pady=30)
frame.pack(expand=True)

# ------------------ Username ------------------
lbl_username = Label(
    frame,
    text="Email:",
    font=("Arial", 11),
    bg="#f4f1ec"
)
lbl_username.grid(row=0, column=0, sticky="e", pady=10, padx=10)

entry_username = Entry(frame, width=30)
entry_username.grid(row=0, column=1, pady=10)
entry_username.insert(0, "khemrajjoshijk@gmail.com")

# ------------------ Password ------------------
lbl_password = Label(
    frame,
    text="Password:",
    font=("Arial", 11),
    bg="#f4f1ec"
)
lbl_password.grid(row=1, column=0, sticky="e", pady=10, padx=10)

entry_password = Entry(frame, width=30, show="*")
entry_password.grid(row=1, column=1, pady=10)
entry_password.insert(0, "Sometimes@123")

# ------------------ Login Button Function ------------------
def login():
    username = entry_username.get().strip()
    password = entry_password.get().strip()

    if not username:
        messagebox.showwarning("Input Error", "Please enter Email")
        entry_username.focus()
        return

    if not password:
        messagebox.showwarning("Input Error", "Please enter password")
        entry_password.focus()
        return

    conn = connect_db()
    cursor = conn.cursor()

    query = """
        SELECT mem_id, role FROM memberinfo
        WHERE email=%s AND password=%s
    """
    cursor.execute(query, (username, password))
    result = cursor.fetchone()

    if result:
        mem_id, role = result
        messagebox.showinfo("Success", f"Login Successful ({role})")

        root.destroy()

        if role == "ADM":
            open_admin_window(mem_id)
        elif role == "USR":
            open_student_window(mem_id)
        else:
            messagebox.showerror("Error", "Unknown role!")
    else:
        messagebox.showerror("Error", "Invalid credentials")

    cursor.close()
    conn.close()

# ------------------ Signup Window Function ------------------
def open_signup():
    root.withdraw()
    signup_window = Toplevel(root)
    signup_window.title("Signup - Library Management System")
    signup_window.geometry("450x380")
    signup_window.resizable(False, False)
    signup_window.configure(bg="#f4f1ec")

    signup_frame = Frame(signup_window, bg="#f4f1ec", padx=30, pady=30)
    signup_frame.pack(expand=True)

    Label(signup_frame, text="Create Account", font=("Arial", 14, "bold"),
          bg="#f4f1ec").grid(row=0, column=0, columnspan=2, pady=10)

    Label(signup_frame, text="Full Name:", bg="#f4f1ec").grid(row=1, column=0, sticky="e", pady=8)
    entry_su_username = Entry(signup_frame, width=30)
    entry_su_username.grid(row=1, column=1, pady=8)

    Label(signup_frame, text="Email:", bg="#f4f1ec").grid(row=2, column=0, sticky="e", pady=8)
    entry_su_email = Entry(signup_frame, width=30)
    entry_su_email.grid(row=2, column=1, pady=8)

    Label(signup_frame, text="Password:", bg="#f4f1ec").grid(row=3, column=0, sticky="e", pady=8)
    entry_su_password = Entry(signup_frame, width=30, show="*")
    entry_su_password.grid(row=3, column=1, pady=8)

    Label(signup_frame, text="Confirm Password:", bg="#f4f1ec").grid(row=4, column=0, sticky="e", pady=8)
    entry_confirm = Entry(signup_frame, width=30, show="*")
    entry_confirm.grid(row=4, column=1, pady=8)

    def signup():
        su_username = entry_su_username.get()
        su_password = entry_su_password.get()
        confirm_password = entry_confirm.get()
        email = entry_su_email.get()

        if not su_username or not su_password or not email or not confirm_password:
            messagebox.showerror("Error", "All fields are required")
            return

        if su_password != confirm_password:
            messagebox.showerror("Error", "Passwords do not match")
            return

        conn = connect_db()
        cursor = conn.cursor()

        query = """
            INSERT INTO memberinfo (full_name, email, password)
            VALUES (%s, %s, %s)
        """
        values = (su_username, email, su_password)
        cursor.execute(query, values)
        conn.commit()

        cursor.close()
        conn.close()

        messagebox.showinfo(
            "Signup Successful",
            "Signup successful, Please login to continue"
        )

        signup_window.destroy()
        root.deiconify()

    Button(
        signup_frame,
        text="Signup",
        width=18,
        bg="#27ae60",
        fg="white",
        command=signup
    ).grid(row=5, column=0, columnspan=2, pady=20)

# ------------------ Buttons ------------------
btn_login = Button(
    frame,
    text="Login",
    width=14,
    bg="#2980b9",
    fg="white",
    command=login
)
btn_login.grid(row=2, column=0, pady=25)

btn_signup = Button(
    frame,
    text="Signup",
    width=14,
    bg="#8e44ad",
    fg="white",
    command=open_signup
)
btn_signup.grid(row=2, column=1, pady=25)

# ------------------ Run Application ------------------
root.mainloop()
