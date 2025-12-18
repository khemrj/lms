from tkinter import *
from tkinter import messagebox
import mysql.connector

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

# ------------------ Password ------------------
lbl_password = Label(frame, text="Password:")
lbl_password.grid(row=1, column=0, sticky="w", pady=10)

entry_password = Entry(frame, width=30, show="*")
entry_password.grid(row=1, column=1, pady=10)

# ------------------ Login Button Function ------------------
def login():
    username = entry_username.get()
    password = entry_password.get()
    print("Login clicked")
    print("Username:", username)

# ------------------ Signup Window Function ------------------
def open_signup():
    signup_window = Toplevel(root)
    signup_window.title("Signup - Library Management System")
    signup_window.geometry("450x350")
    signup_window.resizable(False, False)

    signup_frame = Frame(signup_window, padx=20, pady=20)
    signup_frame.pack(expand=True)

    # -------- Signup Username --------
    lbl_su_username = Label(signup_frame, text="Username:")
    lbl_su_username.grid(row=0, column=0, sticky="w", pady=10)

    entry_su_username = Entry(signup_frame, width=30)
    entry_su_username.grid(row=0, column=1, pady=10)

    # -------- Signup Password --------
    lbl_su_password = Label(signup_frame, text="Password:")
    lbl_su_password.grid(row=1, column=0, sticky="w", pady=10)

    entry_su_password = Entry(signup_frame, width=30, show="*")
    entry_su_password.grid(row=1, column=1, pady=10)

    # -------- Confirm Password --------
    lbl_confirm = Label(signup_frame, text="Confirm Password:")
    lbl_confirm.grid(row=2, column=0, sticky="w", pady=10)

    entry_confirm = Entry(signup_frame, width=30, show="*")
    entry_confirm.grid(row=2, column=1, pady=10)

    # -------- Signup Button Function --------
    def signup():
        su_username = entry_su_username.get()
        su_password = entry_su_password.get()
        confirm_password = entry_confirm.get()

        if not su_username or not su_password:
            messagebox.showerror("Error", "All fields are required")
            return

        if su_password != confirm_password:
            messagebox.showerror("Error", "Passwords do not match")
            return

        # ---- If signup is successful ----
        messagebox.showinfo(
            "Signup Successful",
            "Signup successful, Please login to continue"
        )

        signup_window.destroy()   # Close signup window

    # -------- Signup Button --------
    btn_signup = Button(signup_frame, text="Signup", width=15, command=signup)
    btn_signup.grid(row=3, column=0, columnspan=2, pady=20)

# ------------------ Buttons ------------------
btn_login = Button(frame, text="Login", width=12, command=login)
btn_login.grid(row=2, column=0, pady=20)

btn_signup = Button(frame, text="Signup", width=12, command=open_signup)
btn_signup.grid(row=2, column=1, pady=20)

# ------------------ Run Application ------------------
root.mainloop()
