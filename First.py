from tkinter import *
from tkinter import messagebox
import mysql.connector

# ---------- THEME COLORS ----------
COLOR_BG = "#f0f2f5"
COLOR_PRIMARY = "#2c3e50"
COLOR_ACCENT = "#3498db"
COLOR_SUCCESS = "#27ae60"
COLOR_SECONDARY = "#95a5a6"

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
    BorrowBooks.start(mem_id)

# ------------------ Main Window ------------------
root = Tk()
root.title("Library Management System - Login")
root.geometry("500x450")
root.resizable(False, False)
root.configure(bg=COLOR_BG)

# ------------------ Header ------------------
header = Frame(root, bg=COLOR_PRIMARY, height=100)
header.pack(fill=X)

Label(
    header,
    text="Welcome Back",
    font=("Helvetica", 22, "bold"),
    bg=COLOR_PRIMARY,
    fg="white"
).pack(pady=(20, 0))

Label(
    header,
    text="Please sign in to your account",
    font=("Helvetica", 10),
    bg=COLOR_PRIMARY,
    fg="#bdc3c7"
).pack(pady=(0, 20))

# ------------------ Main Login Frame ------------------
main_frame = Frame(root, bg=COLOR_BG, padx=40, pady=30)
main_frame.pack(expand=True, fill=BOTH)

# Email Section
Label(main_frame, text="Email Address", font=("Arial", 10, "bold"), bg=COLOR_BG, fg=COLOR_PRIMARY).pack(anchor=W)
entry_username = Entry(main_frame, width=40, font=("Arial", 11), bd=1, relief=SOLID)
entry_username.pack(pady=(5, 20), ipady=5)
entry_username.insert(0, "khemrajjoshijk@gmail.com")

# Password Section
Label(main_frame, text="Password", font=("Arial", 10, "bold"), bg=COLOR_BG, fg=COLOR_PRIMARY).pack(anchor=W)
entry_password = Entry(main_frame, width=40, font=("Arial", 11), bd=1, relief=SOLID, show="*")
entry_password.pack(pady=(5, 25), ipady=5)
entry_password.insert(0, "Sometimes@123")

# ------------------ Login Logic ------------------
def login():
    username = entry_username.get().strip()
    password = entry_password.get().strip()

    if not username or not password:
        messagebox.showwarning("Input Error", "All fields are required")
        return

    try:
        conn = connect_db()
        cursor = conn.cursor()
        query = "SELECT mem_id, role FROM memberinfo WHERE email=%s AND password=%s"
        cursor.execute(query, (username, password))
        result = cursor.fetchone()

        if result:
            mem_id, role = result
            messagebox.showinfo("Success", f"Login Successful! Role: {role}")
            root.destroy()
            if role == "ADM":
                open_admin_window(mem_id)
            elif role == "USR":
                open_student_window(mem_id)
        else:
            messagebox.showerror("Error", "Invalid email or password")
    except Exception as e:
        messagebox.showerror("Database Error", str(e))
    finally:
        if 'conn' in locals():
            cursor.close()
            conn.close()

# ------------------ Signup Window ------------------
def open_signup():
    root.withdraw()
    signup_window = Toplevel(root)
    signup_window.title("Create Account")
    signup_window.geometry("500x550")
    signup_window.configure(bg=COLOR_BG)

    # Simple Header for Signup
    S_Header = Frame(signup_window, bg=COLOR_ACCENT, height=80)
    S_Header.pack(fill=X)
    Label(S_Header, text="Join the Library", font=("Arial", 16, "bold"), bg=COLOR_ACCENT, fg="white").pack(pady=20)

    s_frame = Frame(signup_window, bg=COLOR_BG, padx=40, pady=20)
    s_frame.pack(fill=BOTH)

    def create_field(label_text):
        Label(s_frame, text=label_text, font=("Arial", 9, "bold"), bg=COLOR_BG).pack(anchor=W, pady=(10, 0))
        ent = Entry(s_frame, width=40, font=("Arial", 10), bd=1, relief=SOLID)
        ent.pack(ipady=4)
        return ent

    e_name = create_field("Full Name")
    e_email = create_field("Email")
    e_pass = create_field("Password")
    e_pass.config(show="*")
    e_conf = create_field("Confirm Password")
    e_conf.config(show="*")

    def signup_action():
        if e_pass.get() != e_conf.get():
            messagebox.showerror("Error", "Passwords do not match")
            return
        
        try:
            conn = connect_db()
            cursor = conn.cursor()
            query = "INSERT INTO memberinfo (full_name, email, password, role) VALUES (%s, %s, %s, 'USR')"
            cursor.execute(query, (e_name.get(), e_email.get(), e_pass.get()))
            conn.commit()
            messagebox.showinfo("Success", "Account created! Please login.")
            signup_window.destroy()
            root.deiconify()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    Button(s_frame, text="REGISTER NOW", bg=COLOR_SUCCESS, fg="white", font=("Arial", 10, "bold"), 
           width=30, pady=10, command=signup_action, cursor="hand2").pack(pady=30)
    
    Button(s_frame, text="Cancel", bg=COLOR_SECONDARY, fg="white", font=("Arial", 9), 
           command=lambda: [signup_window.destroy(), root.deiconify()]).pack()

# ------------------ Login Buttons ------------------
btn_login = Button(
    main_frame,
    text="SIGN IN",
    font=("Arial", 11, "bold"),
    bg=COLOR_ACCENT,
    fg="white",
    width=35,
    pady=10,
    cursor="hand2",
    command=login
)
btn_login.pack(pady=5)

signup_link = Label(
    main_frame, 
    text="Don't have an account? Create one here", 
    fg=COLOR_ACCENT, 
    bg=COLOR_BG, 
    font=("Arial", 9, "underline"), 
    cursor="hand2"
)
signup_link.pack(pady=10)
signup_link.bind("<Button-1>", lambda e: open_signup())

root.mainloop()