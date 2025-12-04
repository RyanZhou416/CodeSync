import tkinter as tk
from .gui import CodeSyncApp

def main():
    root = tk.Tk()
    app = CodeSyncApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()