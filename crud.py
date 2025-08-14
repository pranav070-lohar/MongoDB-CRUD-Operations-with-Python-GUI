import customtkinter as ctk
from tkinter import ttk, messagebox
from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime

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
            messagebox.showinfo("✅ Success", "Record inserted successfully!")
            clear_fields()
            fetch_data()
        except Exception as e:
            messagebox.showerror("Error", str(e))
    else:
        messagebox.showwarning("⚠ Input Error", "Please enter valid Name, Age (number), and Course.")

def fetch_data():
    for row in tree.get_children():
        tree.delete(row)
    # Show newest first
    for doc in collection.find().sort("_id", -1):
        tree.insert("", "end", iid=str(doc["_id"]), values=(doc["name"], doc["age"], doc["course"]))
    last_refreshed.configure(text=f"Last Refreshed: {datetime.now().strftime('%H:%M:%S')}")

def update_data():
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("⚠ Selection Error", "Please select a record to update.")
        return

    record_id = ObjectId(selected[0])
    name = entry_name.get().strip()
    age = entry_age.get().strip()
    course = entry_course.get().strip()

    if name and age.isdigit() and course:
        try:
            collection.update_one({"_id": record_id}, {"$set": {"name": name, "age": int(age), "course": course}})
            messagebox.showinfo("✅ Success", "Record updated successfully!")
            clear_fields()
            fetch_data()
        except Exception as e:
            messagebox.showerror("Error", str(e))
    else:
        messagebox.showwarning("⚠ Input Error", "Please enter valid Name, Age (number), and Course.")

def delete_data():
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("⚠ Selection Error", "Please select a record to delete.")
        return

    record_id = ObjectId(selected[0])
    confirm = messagebox.askyesno("🗑 Confirm Delete", "Are you sure you want to delete this record?")
    if confirm:
        try:
            collection.delete_one({"_id": record_id})
            messagebox.showinfo("✅ Success", "Record deleted successfully!")
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
ctk.set_appearance_mode("Dark")  
ctk.set_default_color_theme("green")  

root = ctk.CTk()
root.title("📚 Student Manager")
root.geometry("900x500")

# Layout frames
left_frame = ctk.CTkFrame(root, width=250)
left_frame.pack(side="left", fill="y", padx=10, pady=10)

right_frame = ctk.CTkFrame(root)
right_frame.pack(side="right", expand=True, fill="both", padx=10, pady=10)

# Title
title_label = ctk.CTkLabel(left_frame, text="Student Form", font=ctk.CTkFont(size=20, weight="bold"))
title_label.pack(pady=10)

# Form Inputs
entry_name = ctk.CTkEntry(left_frame, placeholder_text="Name")
entry_name.pack(pady=5)

entry_age = ctk.CTkEntry(left_frame, placeholder_text="Age")
entry_age.pack(pady=5)

entry_course = ctk.CTkEntry(left_frame, placeholder_text="Course")
entry_course.pack(pady=5)

# Buttons
ctk.CTkButton(left_frame, text="➕ Add", command=insert_data, fg_color="green").pack(pady=5, fill="x")
ctk.CTkButton(left_frame, text="✏ Update", command=update_data, fg_color="blue").pack(pady=5, fill="x")
ctk.CTkButton(left_frame, text="🗑 Delete", command=delete_data, fg_color="red").pack(pady=5, fill="x")
ctk.CTkButton(left_frame, text="🔄 Read", command=fetch_data, fg_color="orange").pack(pady=5, fill="x")
ctk.CTkButton(left_frame, text="🧹 Clear", command=clear_fields, fg_color="gray").pack(pady=5, fill="x")

last_refreshed = ctk.CTkLabel(left_frame, text="Last Refreshed: -", font=ctk.CTkFont(size=12))
last_refreshed.pack(pady=5)

# Table
columns = ("Name", "Age", "Course")
tree = ttk.Treeview(right_frame, columns=columns, show="headings")
for col in columns:
    tree.heading(col, text=col)
    tree.column(col, anchor="center", width=200)
tree.pack(fill="both", expand=True)

tree.bind("<<TreeviewSelect>>", select_record)

# Fetch initial data
fetch_data()

root.mainloop()
