import tkinter as tk
from tkinter import ttk, messagebox, simpledialog

class LoginPage:

    def __init__(self, root):
        self.root = root
        root.title("Login Page")
        root.state("zoomed")
        root.config(background = "#2C323A")

        self.create_login_interface()
        self.create_register_interface()
        self.create_forgot_password_interface()
        self.create_main_interface()
        self.show_login_interface()

    def create_login_interface(self):

        self.login_frame = tk.Frame(self.root, bg="#2C323A")
        self.login_frame.place(relwidth=1, relheight=1)

        tk.Label(self.login_frame, text="Login", font=("Helvetica", 24), bg="#2C323A", fg="white").pack(pady=20)
        tk.Label(self.login_frame, text="Username:", bg="#2C323A", fg="white").pack(pady=5)
        self.username_entry = tk.Entry(self.login_frame)
        self.username_entry.pack(pady=5)

        tk.Label(self.login_frame, text="Password:", bg="#2C323A", fg="white").pack(pady=5)
        self.password_entry = tk.Entry(self.login_frame, show='*')
        self.password_entry.pack(pady=5)

        tk.Button(self.login_frame, text="Login", command=self.login).pack(pady=10)
        tk.Button(self.login_frame, text="Register", command=self.show_register_interface).pack(pady=5)
        tk.Button(self.login_frame, text="Forgot Password?", command=self.show_forgot_password_interface).pack(pady=5)
        tk.Button(self.login_frame, text="Exit", command=self.root.quit).pack(pady=5)
    
    def create_register_interface(self):

        self.register_frame = tk.Frame(self.root, bg="#2C323A")
        tk.Label(self.register_frame, text="Register", font=("Helvetica", 24), bg="#2C323A", fg="white").pack(pady=20)
        tk.Label(self.register_frame, text="Username:", bg="#2C323A", fg="white").pack(pady=5)
        self.new_username_entry = tk.Entry(self.register_frame)
        self.new_username_entry.pack(pady=5)

        tk.Label(self.register_frame, text="Password:", bg="#2C323A", fg="white").pack(pady=5)
        self.new_password_entry = tk.Entry(self.register_frame, show='*')
        self.new_password_entry.pack(pady=5)

        tk.Button(self.register_frame, text="Register", command=self.register).pack(pady=10)
        tk.Button(self.register_frame, text="Back to Login", command=self.show_login_interface).pack(pady=5)
        tk.Button(self.register_frame, text="Exit", command=self.root.quit).pack(pady=5)
    
    def create_forgot_password_interface(self):
        self.forgot_frame = tk.Frame(self.root, bg="#2C323A")
        tk.Label(self.forgot_frame, text="Forgot Password", font=("Helvetica", 24), bg="#2C323A", fg="white").pack(pady=20)
        tk.Label(self.forgot_frame, text="Username:", bg="#2C323A", fg="white").pack(pady=5)
        self.forgot_username_entry = tk.Entry(self.forgot_frame)
        self.forgot_username_entry.pack(pady=5)

        tk.Button(self.forgot_frame, text="Reset Password", command=self.reset_password).pack(pady=10)
        tk.Button(self.forgot_frame, text="Back to Login", command=self.show_login_interface).pack(pady=5)
        tk.Button(self.forgot_frame, text="Exit", command=self.root.quit).pack(pady=5)

    def create_main_interface(self):
        self.main_frame = tk.Frame(self.root, bg="#2C323A")
        tk.Label(self.main_frame, text="Welcome to the Main Page", font=("Helvetica", 24), bg="#2C323A", fg="white").pack(pady=20)
        tk.Button(self.main_frame, text="Logout", command=self.show_login_interface).pack(pady=10)
        tk.Button(self.main_frame, text="Exit", command=self.root.quit).pack(pady=5)

    def show_login_interface(self):
        self.login_frame.tkraise()
        self.login_frame.place(relwidth=1, relheight=1)
        self.register_frame.place_forget()
        self.forgot_frame.place_forget()
        self.main_frame.place_forget()

    def show_register_interface(self):
        self.register_frame.tkraise()
        self.register_frame.place(relwidth=1, relheight=1)
        self.login_frame.place_forget()
        self.forgot_frame.place_forget()
        self.main_frame.place_forget()

    def show_forgot_password_interface(self):
        self.forgot_frame.tkraise()
        self.forgot_frame.place(relwidth=1, relheight=1)
        self.login_frame.place_forget()
        self.register_frame.place_forget()
        self.main_frame.place_forget()
    
    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        if username == "admin" and password == "password":
            messagebox.showinfo("Login Successful", "Welcome to the main page!")
            self.show_main_interface()
        else:
            messagebox.showerror("Login Failed", "Invalid username or password.")

    def register(self):
        username = self.new_username_entry.get()
        password = self.new_password_entry.get()

        if username and password:
            messagebox.showinfo("Registration Successful", f"User {username} registered successfully!")
            self.show_login_interface()
        else:
            messagebox.showerror("Registration Failed", "Please fill in all fields.")
    
    def show_main_interface(self):
        self.main_frame.tkraise()
        self.main_frame.place(relwidth=1, relheight=1)
        self.login_frame.place_forget()
        self.register_frame.place_forget()
        self.forgot_frame.place_forget()

    def reset_password(self):
        username = self.forgot_username_entry.get()

        if username:
            new_password = simpledialog.askstring("Reset Password", "Enter new password:")
            if new_password:
                messagebox.showinfo("Password Reset", f"Password for {username} has been reset.")
                self.show_login_interface()
            else:
                messagebox.showerror("Error", "Please enter a new password.")
        else:
            messagebox.showerror("Error", "Please enter your username.")

root = tk.Tk()
app = LoginPage(root)
root.mainloop()