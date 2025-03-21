import tkinter as tk
import time
import threading

class RansomwareSim:
    def __init__(self, root):
        self.root = root
        self.root.title("Your Files Are Encrypted!")
        self.root.geometry("500x300")
        self.root.configure(bg="black")
        
        self.label = tk.Label(root, text="YOUR FILES HAVE BEEN ENCRYPTED!", fg="red", bg="black", font=("Arial", 14, "bold"))
        self.label.pack(pady=20)
        
        self.timer_label = tk.Label(root, text="Time left: 10:00", fg="white", bg="black", font=("Arial", 12))
        self.timer_label.pack(pady=10)
        
        self.info_label = tk.Label(root, text="Pay 1 BTC to the provided address or lose your files forever!", fg="white", bg="black", font=("Arial", 10))
        self.info_label.pack(pady=10)
        
        self.bitcoin_address = tk.Label(root, text="BTC Address: 1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa", fg="white", bg="black", font=("Arial", 10, "italic"))
        self.bitcoin_address.pack(pady=5)
        
        self.countdown(600)  # 10 minutos
        
    def countdown(self, seconds):
        def update_timer():
            for i in range(seconds, 0, -1):
                mins, secs = divmod(i, 60)
                self.timer_label.config(text=f"Time left: {mins:02}:{secs:02}")
                time.sleep(1)
            self.timer_label.config(text="TIME OVER! FILES DELETED!")
        
        threading.Thread(target=update_timer, daemon=True).start()

def start_ransomware():
    root = tk.Tk()
    app = RansomwareSim(root)
    root.mainloop()

if __name__ == "__main__":
    start_ransomware()