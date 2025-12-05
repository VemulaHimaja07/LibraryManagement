from tkinter import *
import tkinter.ttk as ttk
import tkinter.messagebox as mb
import tkinter.simpledialog as sd
import mysql.connector

# ---------- CONNECT TO MYSQL ----------
# First connect WITHOUT database
connector = mysql.connector.connect(
    host="localhost",
    user="root",
    password="hitanshu@16113"
)
cursor = connector.cursor()

# Create database if not exists
cursor.execute("CREATE DATABASE IF NOT EXISTS library")
connector.commit()

# Connect to the new database
connector = mysql.connector.connect(
    host="localhost",
    user="root",
    password="hitanshu@16113",
    database="library"
)
cursor = connector.cursor()

# Create table if not exists
cursor.execute(
    '''CREATE TABLE IF NOT EXISTS Library (
        BK_NAME VARCHAR(255),
        BK_ID VARCHAR(255) PRIMARY KEY NOT NULL,
        AUTHOR_NAME VARCHAR(255),
        BK_STATUS VARCHAR(255),
        CARD_ID VARCHAR(255)
    )'''
)

# ---------- FUNCTIONS ----------
def issuer_card():
    Cid = sd.askstring('Issuer Card ID', 'What is the Issuer\'s Card ID?\t\t\t')
    if not Cid:
        mb.showerror('Issuer ID cannot be zero!', 'Issuer ID cannot be empty')
    else:
        return Cid

def display_records():
    tree.delete(*tree.get_children())
    cursor.execute("SELECT * FROM Library")
    data = cursor.fetchall()
    for record in data:
        tree.insert("", END, values=record)

def clear_fields():
    bk_status.set("Available")
    bk_id.set("")
    bk_name.set("")
    author_name.set("")
    card_id.set("")
    bk_id_entry.config(state='normal')

def clear_and_display():
    clear_fields()
    display_records()

def add_record():
    if bk_status.get() == "Issued":
        card_id.set(issuer_card())
    else:
        card_id.set("N/A")

    sure = mb.askyesno("Confirm", "Add this record?")
    if sure:
        try:
            cursor.execute(
                "INSERT INTO Library VALUES (%s,%s,%s,%s,%s)",
                (bk_name.get(), bk_id.get(), author_name.get(),
                 bk_status.get(), card_id.get())
            )
            connector.commit()
            clear_and_display()
            mb.showinfo("Success", "Record Added")
        except mysql.connector.IntegrityError:
            mb.showerror("Error", "Book ID already exists")

def view_record():
    if not tree.focus():
        mb.showerror("Error", "Select a record first")
        return
    selected = tree.item(tree.focus())['values']
    bk_name.set(selected[0])
    bk_id.set(selected[1])
    author_name.set(selected[2])
    bk_status.set(selected[3])
    card_id.set(selected[4])

def update_record():
    def update():
        if bk_status.get() == "Issued":
            card_id.set(issuer_card())
        else:
            card_id.set("N/A")

        cursor.execute(
            "UPDATE Library SET BK_NAME=%s, AUTHOR_NAME=%s, BK_STATUS=%s, CARD_ID=%s WHERE BK_ID=%s",
            (bk_name.get(), author_name.get(), bk_status.get(), card_id.get(), bk_id.get())
        )
        connector.commit()
        clear_and_display()
        edit_btn.destroy()
        bk_id_entry.config(state="normal")

    view_record()
    bk_id_entry.config(state="disabled")

    edit_btn = Button(left_frame, text="Update", font=btn_font, bg=btn_hlb_bg, command=update)
    edit_btn.place(x=50, y=375)

def remove_record():
    if not tree.selection():
        mb.showerror("Error", "Select a record")
        return

    selected = tree.item(tree.focus())['values']
    cursor.execute("DELETE FROM Library WHERE BK_ID=%s", (selected[1],))
    connector.commit()
    clear_and_display()
    mb.showinfo("Deleted", "Record deleted")

def delete_inventory():
    if mb.askyesno("Confirm", "Delete ALL records?"):
        cursor.execute("DELETE FROM Library")
        connector.commit()
        clear_and_display()

def change_availability():
    if not tree.selection():
        mb.showerror("Error", "Select a record")
        return

    selected = tree.item(tree.focus())['values']
    book_id = selected[1]
    status = selected[3]

    if status == "Issued":
        if mb.askyesno("Confirm Return", "Has the book been returned?"):
            cursor.execute("UPDATE Library SET BK_STATUS='Available', CARD_ID='N/A' WHERE BK_ID=%s", (book_id,))
            connector.commit()
    else:
        cursor.execute("UPDATE Library SET BK_STATUS='Issued', CARD_ID=%s WHERE BK_ID=%s",
                       (issuer_card(), book_id))
        connector.commit()

    clear_and_display()


# ---------- GUI ----------
root = Tk()
root.title("Library Management System")
root.geometry("1010x530")
root.resizable(False, False)

Label(root, text="LIBRARY MANAGEMENT SYSTEM", font=("Arial", 16, "bold"),
      bg="SteelBlue", fg="white").pack(fill=X)

# Variables
bk_status = StringVar()
bk_name = StringVar()
bk_id = StringVar()
author_name = StringVar()
card_id = StringVar()
bk_status.set("Available")

# Left Frame
left_frame = Frame(root, bg="LightSkyBlue")
left_frame.place(x=0, y=30, relwidth=0.3, relheight=0.96)

lbl_font = ('Georgia', 13)
entry_font = ('Times New Roman', 12)
btn_font = ('Gill Sans MT', 13)
btn_hlb_bg = 'SteelBlue'

Label(left_frame, text="Book Name", bg="LightSkyBlue", font=lbl_font).place(x=98, y=25)
Entry(left_frame, textvariable=bk_name, width=25, font=entry_font).place(x=45, y=55)

Label(left_frame, text="Book ID", bg="LightSkyBlue", font=lbl_font).place(x=110, y=105)
bk_id_entry = Entry(left_frame, textvariable=bk_id, width=25, font=entry_font)
bk_id_entry.place(x=45, y=135)

Label(left_frame, text="Author Name", bg="LightSkyBlue", font=lbl_font).place(x=90, y=185)
Entry(left_frame, textvariable=author_name, width=25, font=entry_font).place(x=45, y=215)

Label(left_frame, text="Status", bg="LightSkyBlue", font=lbl_font).place(x=75, y=265)
OptionMenu(left_frame, bk_status, "Available", "Issued").place(x=75, y=300)

Button(left_frame, text="Add Record", font=btn_font, bg=btn_hlb_bg,
       width=20, command=add_record).place(x=50, y=375)

Button(left_frame, text="Clear Fields", font=btn_font, bg=btn_hlb_bg,
       width=20, command=clear_fields).place(x=50, y=435)

# Right Frame (Inventory)
tree = ttk.Treeview(root, columns=('Book Name', 'Book ID', 'Author', 'Status', 'Card ID'), show='headings')
tree.place(relx=0.3, rely=0.24, relheight=0.76, relwidth=0.7)

for col in ('Book Name', 'Book ID', 'Author', 'Status', 'Card ID'):
    tree.heading(col, text=col)

display_records()
root.mainloop()