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
    ManageBooks.start(mem_id)
    

def open_student_window(mem_id):
    import BorrowBooks
    print("login ma memId is ",mem_id)
    BorrowBooks.start(mem_id)
# ------------------ Main Window ------------------
root = Tk()
root.title("Library Management System")
root.geometry("450x300")
root.resizable(False, False)

# ------------------ Main Frame ------------------
frame = Frame(root, padx=20, pady=20)
frame.pack(expand=True)

# ------------------ Username ------------------
lbl_username = Label(frame, text="Username:")
lbl_username.grid(row=0, column=0, sticky="w", pady=10)

entry_username = Entry(frame, width=30)
entry_username.grid(row=0, column=1, pady=10)
entry_username.insert(0,"9876765456")


# ------------------ Password ------------------
lbl_password = Label(frame, text="Password:")
lbl_password.grid(row=1, column=0, sticky="w", pady=10)

entry_password = Entry(frame, width=30, show="*")
entry_password.grid(row=1, column=1, pady=10)
entry_password.insert(0,"Sometimes@123")

# ------------------ Login Button Function ------------------
def login():
    username = entry_username.get().strip()
    password = entry_password.get().strip()

    # -------- Input Validation --------
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

        root.destroy()   # close login window

        # -------- Role-based window --------
        if role == "ADM":
            print("admin login")
            open_admin_window(mem_id)   # call your admin dashboard
        elif role == "USR":
            print("User login")
            print("memberis is ", mem_id)
            open_student_window(mem_id) # call your student dashboard
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
    signup_window.geometry("450x350")
    signup_window.resizable(False, False)

    signup_frame = Frame(signup_window, padx=20, pady=20)
    signup_frame.pack(expand=True)

    # -------- Signup Username --------
    lbl_su_username = Label(signup_frame, text="Full name:")
    lbl_su_username.grid(row=0, column=0, sticky="w", pady=10)

    entry_su_username = Entry(signup_frame, width=30)
    entry_su_username.grid(row=0, column=1, pady=10)
    #entry_su_username.insert(0, "9876765456")

    #-------------email -----------------------

    lbl_su_email = Label(signup_frame, text="Email:")
    lbl_su_email.grid(row=1, column=0, sticky="w", pady=10)

    entry_su_email = Entry(signup_frame, width=30)
    entry_su_email.grid(row=1, column=1, pady=10)
    
    # -------- Signup Password --------
    lbl_su_password = Label(signup_frame, text="Password:")
    lbl_su_password.grid(row=2, column=0, sticky="w", pady=10)

    entry_su_password = Entry(signup_frame, width=30, show="*")
    entry_su_password.grid(row=2, column=1, pady=10)

    # -------- Confirm Password --------
    lbl_confirm = Label(signup_frame, text="Confirm Password:")
    lbl_confirm.grid(row=3, column=0, sticky="w", pady=10)

    entry_confirm = Entry(signup_frame, width=30, show="*")
    entry_confirm.grid(row=3, column=1, pady=10)

    # -------- Signup Button Function --------
    def signup():
        su_username = entry_su_username.get()
        su_password = entry_su_password.get()
        confirm_password = entry_confirm.get()
        email =entry_su_email.get()

        if not su_username or not su_password or not email or not confirm_password:
            messagebox.showerror("Error", "All fields are required")
            return

        if su_password != confirm_password:
            messagebox.showerror("Error", "Passwords do not match")
            return
        
    
        conn = connect_db()
        cursor = conn.cursor()

        
        print("before  insert query in signup")
        query = """
            INSERT INTO memberinfo (full_name, email, password)
            VALUES (%s, %s, %s)
        """
        
        print("isbn is after query ")
        values = (su_username, email, su_password)  # return_date is NULL initially

        cursor.execute(query, values)
        conn.commit()

        messagebox.showinfo("Success", f"User is registered ")
        cursor.close()
        conn.close()
        




        # ---- If signup is successful ----
        messagebox.showinfo(
            "Signup Successful",
            "Signup successful, Please login to continue"
        )

        signup_window.destroy()   # Close signup window
        root.deiconify()

    # -------- Signup Button --------
    btn_signup = Button(signup_frame, text="Signup", width=15, command=signup)
    btn_signup.grid(row=4, column=0, columnspan=2, pady=20)

# ------------------ Buttons ------------------
btn_login = Button(frame, text="Login", width=12, command=login)
btn_login.grid(row=2, column=0, pady=20)

btn_signup = Button(frame, text="Signup", width=12, command=open_signup)
btn_signup.grid(row=2, column=1, pady=20)

# ------------------ Run Application ------------------
root.mainloop()
