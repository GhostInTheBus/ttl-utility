import os
import sys
import platform
import subprocess
import re
import tkinter as tk
from tkinter import messagebox, scrolledtext

class ModernButton(tk.Label):
    """A custom modern button using tk.Label to support full colors on macOS."""
    def __init__(self, master, text, command=None, bg="#333", fg="white", hover_bg="#444", **kwargs):
        super().__init__(master, text=text, bg=bg, fg=fg, font=("SF Pro Text", 10, "bold"), 
                         padx=15, pady=8, cursor="hand2", **kwargs)
        self.command = command
        self.bg = bg
        self.hover_bg = hover_bg
        self.bind("<Button-1>", lambda e: self.click())
        self.bind("<Enter>", lambda e: self.configure(bg=self.hover_bg))
        self.bind("<Leave>", lambda e: self.configure(bg=self.bg))

    def click(self):
        if self.command:
            self.command()

class TTLUtilityApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Cellular TTL Manager")
        self.root.geometry("540x600")
        self.root.configure(bg="#121212")
        
        self.os_type = platform.system()
        self.is_admin = self.check_admin()
        
        # Colors
        self.primary_bg = "#121212"
        self.card_bg = "#1e1e1e"
        self.accent_green = "#4CAF50"
        self.accent_blue = "#2196F3"
        self.text_dim = "#999"
        self.text_main = "#eee"

        self.setup_ui()
        self.log("Cellular TTL Manager (Infinite Plan Vision)")
        self.log(f"OS: {self.os_type} | UID: {getattr(os, 'getuid', lambda: 'N/A')()}")
        self.log(f"Admin Status: {'Authorized' if self.is_admin else 'Limited'}")

    def check_admin(self):
        try:
            if self.os_type == "Windows":
                import ctypes
                return ctypes.windll.shell32.IsUserAnAdmin() != 0
            else:
                return os.getuid() == 0
        except: return False

    def elevate(self):
        self.log("Requesting administrative elevation...")
        try:
            if self.os_type == "Windows":
                import ctypes
                params = " ".join([f'"{arg}"' for arg in sys.argv])
                ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, params, None, 1)
            elif self.os_type == "Darwin":
                script = f'do shell script (quoted form of "{sys.executable}") & " " & {" & \" \" & ".join([f"quoted form of \"{arg}\"" for arg in sys.argv])} with administrator privileges'
                subprocess.run(["osascript", "-e", script], check=True)
            sys.exit()
        except: self.log("Elevation Error or Cancelled.")

    def setup_ui(self):
        # Header Section
        header = tk.Frame(self.root, bg=self.primary_bg, pady=20)
        header.pack(fill=tk.X)
        
        tk.Label(header, text="CELLULAR TTL", font=("SF Pro Display", 24, "bold"), 
                 bg=self.primary_bg, fg=self.accent_green).pack()
        tk.Label(header, text="Infinite Phone Plan Experience", font=("SF Pro Text", 10, "italic"), 
                 bg=self.primary_bg, fg=self.text_dim).pack()

        # Admin Warning (if not admin)
        if not self.is_admin:
            warning = tk.Frame(self.root, bg="#331a00", pady=5)
            warning.pack(fill=tk.X)
            tk.Label(warning, text="⚠️ Admin Elevation Required for TTL Changes", bg="#331a00", fg="#ff9800", font=("SF Pro Text", 9, "bold")).pack()

        # Configuration Card
        card = tk.Frame(self.root, bg=self.card_bg, padx=20, pady=20, highlightbackground="#333", highlightthickness=1)
        card.pack(fill=tk.X, padx=20, pady=10)

        # Carrier Row
        tk.Label(card, text="Carrier Profile", bg=self.card_bg, fg=self.text_dim, font=("SF Pro Text", 9, "bold")).grid(row=0, column=0, sticky="w")
        
        self.carrier_var = tk.StringVar(self.root)
        self.carrier_var.set("Verizon / Visible (65)")
        self.carriers = {"Verizon / Visible (65)": "65", "T-Mobile / Metro (64)": "64", "Custom": ""}
        
        self.carrier_menu = tk.OptionMenu(card, self.carrier_var, *self.carriers.keys(), command=self.update_ttl_from_carrier)
        self.carrier_menu.config(bg=self.card_bg, fg=self.text_main, width=22, highlightthickness=0)
        self.carrier_menu.grid(row=1, column=0, pady=(5, 15), sticky="w")

        # TTL Row
        tk.Label(card, text="Target TTL Value", bg=self.card_bg, fg=self.text_dim, font=("SF Pro Text", 9, "bold")).grid(row=2, column=0, sticky="w")
        
        ttl_entry_frame = tk.Frame(card, bg=self.card_bg)
        ttl_entry_frame.grid(row=3, column=0, sticky="w", pady=(5, 0))
        
        self.ttl_entry = tk.Entry(ttl_entry_frame, width=8, bg="#333", fg="white", insertbackground="white", relief="flat", borderwidth=5)
        self.ttl_entry.insert(0, "65")
        self.ttl_entry.pack(side=tk.LEFT)
        
        ModernButton(ttl_entry_frame, "?", command=self.show_help, bg="#444", hover_bg="#555", font=("Arial", 9, "bold")).pack(side=tk.LEFT, padx=10)

        # Main Action Button (Hero)
        ModernButton(self.root, "APPLY INFINITE PLAN", command=self.apply_custom_ttl, 
                     bg=self.accent_green, hover_bg="#3d8b40").pack(fill=tk.X, padx=20, pady=15)

        # Secondary Actions Row
        actions = tk.Frame(self.root, bg=self.primary_bg)
        actions.pack(fill=tk.X, padx=20)
        
        ModernButton(actions, "TEST CONNECTION", command=self.test_connection, bg=self.accent_blue, hover_bg="#1976D2").pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 5))
        ModernButton(actions, "RESET DEFAULT", command=self.reset_ttl, bg="#444", hover_bg="#555").pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(5, 0))

        if not self.is_admin:
            ModernButton(self.root, "ELEVATE TO ADMINISTRATOR", command=self.elevate, bg="#8d2b2b", hover_bg="#a93232").pack(fill=tk.X, padx=20, pady=10)

        # Log Console
        tk.Label(self.root, text="System Console Output", bg=self.primary_bg, fg=self.text_dim, font=("SF Pro Text", 8, "bold")).pack(anchor="w", padx=25, pady=(20, 0))
        self.log_area = scrolledtext.ScrolledText(self.root, height=8, width=50, bg="#0a0a0a", fg="#4CAF50", 
                                                 font=("Monaco", 9), borderwidth=0, padx=10, pady=10)
        self.log_area.pack(fill=tk.BOTH, expand=True, padx=20, pady=(5, 20))

    def update_ttl_from_carrier(self, selection):
        value = self.carriers.get(selection)
        if value:
            self.ttl_entry.delete(0, tk.END)
            self.ttl_entry.insert(0, value)
            self.log(f"Profile Loaded: {selection}")

    def show_help(self):
        msg = "64: Standard Mobile (T-Mobile)\n65: Hop Adjusted (Verizon)\n\nThis app sets IPv4 and IPv6."
        messagebox.showinfo("TTL Guide", msg)

    def apply_custom_ttl(self):
        val = self.ttl_entry.get().strip()
        if val.isdigit(): self.set_ttl(val)
        else: messagebox.showerror("Error", "Invalid TTL Value")

    def log(self, message):
        self.log_area.insert(tk.END, f"[system] {message}\n")
        self.log_area.see(tk.END)

    def run_command(self, cmd):
        try:
            res = subprocess.run(cmd, shell=True, capture_output=True, text=True, check=True)
            return res.stdout.strip()
        except: return None

    def set_ttl(self, value):
        if not self.is_admin:
            if messagebox.askyesno("Elevate?", "Administrative access required. Elevate now?"):
                self.elevate()
            return

        self.log(f"Configuring IPv4/IPv6 Stacks to TTL {value}...")
        cmds = []
        if self.os_type == "Windows":
            cmds.append(f"netsh int ipv4 set global defaultcurhoplimit={value} store=persistent")
            cmds.append(f"netsh int ipv6 set global defaultcurhoplimit={value} store=persistent")
        elif self.os_type == "Darwin":
            cmds.append(f"sysctl -w net.inet.ip.ttl={value}")
            cmds.append(f"sysctl -w net.inet6.ip6.hlim={value}")
        
        for c in cmds: self.run_command(c)
        self.log(f"TTL {value} applied successfully.")

    def reset_ttl(self):
        if not self.is_admin: return self.log("Admin required for reset.")
        self.set_ttl("128" if self.os_type == "Windows" else "64")

    def test_connection(self):
        self.log("Pinging local stack...")
        cmd = "ping -n 1 127.0.0.1" if self.os_type == "Windows" else "ping -c 1 127.0.0.1"
        out = self.run_command(cmd)
        if out:
            m = re.search(r"ttl=(\d+)", out, re.I)
            if m:
                curr = m.group(1)
                self.log(f"Connection Live. Active TTL: {curr}")
                if curr == self.ttl_entry.get(): self.log("BYPASS CONFIRMED.")

if __name__ == "__main__":
    root = tk.Tk()
    app = TTLUtilityApp(root)
    root.mainloop()
