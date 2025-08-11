import customtkinter as ctk
from tkinter import ttk, messagebox
from pymongo import MongoClient
from bson.objectid import ObjectId

# ------------------ MongoDB Connection ------------------
try:
    client = MongoClient("mongodb://localhost:27017/")
    db = client["student_db"]
    collection = db["students"]
except Exception as e:
    print("Error connecting to MongoDB:", e)
    exit()

# ------------------ CRUD Functions ------------------
def insert_data():
    name = entry_name.get().strip()
    age = entry_age.get().strip()
    course = entry_course.get().strip()

    if name and age.isdigit() and course:
        try:
            collection.insert_one({"name": name, "age": int(age), "course": course})
            messagebox.showinfo("Success", "Record inserted successfully!")
            clear_fields()
            fetch_data()
        except Exception as e:
            messagebox.showerror("Error", str(e))
    else:
        messagebox.showwarning("Input Error", "Please enter valid Name, Age (number), and Course.")

def fetch_data():
    for row in tree.get_children():
        tree.delete(row)
    for doc in collection.find():
        tree.insert("", "end", iid=str(doc["_id"]), values=(doc["name"], doc["age"], doc["course"]))

def update_data():
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("Selection Error", "Please select a record to update.")
        return

    record_id = ObjectId(selected[0])
    name = entry_name.get().strip()
    age = entry_age.get().strip()
    course = entry_course.get().strip()

    if name and age.isdigit() and course:
        try:
            collection.update_one({"_id": record_id}, {"$set": {"name": name, "age": int(age), "course": course}})
            messagebox.showinfo("Success", "Record updated successfully!")
            clear_fields()
            fetch_data()
        except Exception as e:
            messagebox.showerror("Error", str(e))
    else:
        messagebox.showwarning("Input Error", "Please enter valid Name, Age (number), and Course.")

def delete_data():
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("Selection Error", "Please select a record to delete.")
        return

    record_id = ObjectId(selected[0])
    confirm = messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this record?")
    if confirm:
        try:
            collection.delete_one({"_id": record_id})
            messagebox.showinfo("Success", "Record deleted successfully!")
            fetch_data()
        except Exception as e:
            messagebox.showerror("Error", str(e))

def clear_fields():
    entry_name.delete(0, "end")
    entry_age.delete(0, "end")
    entry_course.delete(0, "end")

def select_record(event):
    selected = tree.selection()
    if selected:
        record = collection.find_one({"_id": ObjectId(selected[0])})
        if record:
            clear_fields()
            entry_name.insert(0, record["name"])
            entry_age.insert(0, str(record["age"]))
            entry_course.insert(0, record["course"])

# ------------------ CustomTkinter Setup ------------------
ctk.set_appearance_mode("System")  # Light/Dark theme based on OS
ctk.set_default_color_theme("blue")

root = ctk.CTk()
root.title("MongoDB CRUD App")
root.geometry("800x550")

# Title
title_label = ctk.CTkLabel(root, text="📚 Student Management System", font=ctk.CTkFont(size=22, weight="bold"))
title_label.pack(pady=15)

# Form Frame
form_frame = ctk.CTkFrame(root)
form_frame.pack(pady=10, padx=20, fill="x")

entry_name = ctk.CTkEntry(form_frame, placeholder_text="Enter Name", width=200)
entry_name.grid(row=0, column=0, padx=10, pady=10)

entry_age = ctk.CTkEntry(form_frame, placeholder_text="Enter Age", width=100)
entry_age.grid(row=0, column=1, padx=10, pady=10)

entry_course = ctk.CTkEntry(form_frame, placeholder_text="Enter Course", width=200)
entry_course.grid(row=0, column=2, padx=10, pady=10)

# Buttons
btn_frame = ctk.CTkFrame(root)
btn_frame.pack(pady=5)

ctk.CTkButton(btn_frame, text="Add", command=insert_data, fg_color="green").grid(row=0, column=0, padx=10, pady=5)
ctk.CTkButton(btn_frame, text="Update", command=update_data, fg_color="blue").grid(row=0, column=1, padx=10, pady=5)
ctk.CTkButton(btn_frame, text="Delete", command=delete_data, fg_color="red").grid(row=0, column=2, padx=10, pady=5)
ctk.CTkButton(btn_frame, text="Clear", command=clear_fields, fg_color="gray").grid(row=0, column=3, padx=10, pady=5)

# Table
tree_frame = ctk.CTkFrame(root)
tree_frame.pack(pady=10, padx=20, fill="both", expand=True)

columns = ("Name", "Age", "Course")
tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=12)
for col in columns:
    tree.heading(col, text=col)
    tree.column(col, anchor="center", width=200)
tree.pack(fill="both", expand=True)

tree.bind("<<TreeviewSelect>>", select_record)

# Fetch data initially
fetch_data()

root.mainloop()
