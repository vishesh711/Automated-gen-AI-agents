import tkinter as tk
from tkinter import scrolledtext


def main():
    root = tk.Tk()
    root.title("Simple Test")
    root.geometry("500x400")

    text_area = scrolledtext.ScrolledText(root)
    text_area.pack(expand=True, fill="both", padx=10, pady=10)

    text_area.insert(
        tk.END, "This is a simple test to check if Tkinter is working properly."
    )

    root.mainloop()


if __name__ == "__main__":
    main()
