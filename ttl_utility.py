import os
import sys
import platform
import subprocess
import re
import tkinter as tk
from tkinter import messagebox, scrolledtext

def is_admin():
    """Check if the current process has administrative/root privileges."""
    try:
        if platform.system() == "Windows":
            import ctypes
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        else:
            return os.getuid() == 0
    except:
        return False

def elevate():
    """Request administrative privileges and restart the app."""
    os_type = platform.system()
    try:
        if os_type == "Windows":
            import ctypes
            params = " ".join([f'"{arg}"' for arg in sys.argv])
            ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, params, None, 1)
        elif os_type == "Darwin":
            # Direct osascript elevation for macOS
            args = " ".join([f"quoted form of \"{arg}\"" for arg in sys.argv])
            script = f'do shell script "{sys.executable}" & " " & {args} with administrator privileges'
            subprocess.run(["osascript", "-e", script], check=True)
        elif os_type == "Linux":
            os.execvp("sudo", ["sudo", sys.executable] + sys.argv)
        sys.exit()
    except Exception as e:
        print(f"Elevation failed or cancelled: {e}")
        sys.exit()

class ModernButton(tk.Label):
    def __init__(self, master, text, command=None, bg="#333", fg="white", hover_bg="#444", **kwargs):
        super().__init__(master, text=text, bg=bg, fg=fg, font=("Arial", 10, "bold"), 
                         padx=15, pady=8, cursor="hand2", relief="flat", **kwargs)
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
        
        # Colors
        self.primary_bg = "#121212"
        self.card_bg = "#1e1e1e"
        self.accent_green = "#4CAF50"
        self.accent_blue = "#2196F3"
        self.text_dim = "#999"
        self.text_main = "#eee"

        self.setup_ui()
        self.log("System Initialized with Administrator Privileges.")
        self.log(f"Platform: {platform.system()} | UID: {getattr(os, 'getuid', lambda: 'N/A')()}")

    def setup_ui(self):
        header = tk.Frame(self.root, bg=self.primary_bg, pady=20)
        header.pack(fill=tk.X)
        tk.Label(header, text="CELLULAR TTL", font=("Arial", 24, "bold"), bg=self.primary_bg, fg=self.accent_green).pack()
        tk.Label(header, text="The Infinite Phone Plan Utility", font=("Arial", 10, "italic"), bg=self.primary_bg, fg=self.text_dim).pack()

        card = tk.Frame(self.root, bg=self.card_bg, padx=20, pady=20, highlightbackground="#333", highlightthickness=1)
        card.pack(fill=tk.X, padx=20, pady=10)

        tk.Label(card, text="Select Carrier Profile", bg=self.card_bg, fg=self.text_dim, font=("Arial", 9, "bold")).pack(anchor="w")
        self.carrier_var = tk.StringVar(self.root)
        self.carrier_var.set("Verizon / Visible (65)")
        self.carriers = {"Verizon / Visible (65)": "65", "T-Mobile / Metro (64)": "64", "Custom": ""}
        self.carrier_menu = tk.OptionMenu(card, self.carrier_var, *self.carriers.keys(), command=self.update_ttl_from_carrier)
        self.carrier_menu.config(bg=self.card_bg, fg=self.text_main, width=25, highlightthickness=0)
        self.carrier_menu.pack(anchor="w", pady=(5, 15))

        tk.Label(card, text="Target TTL Value", bg=self.card_bg, fg=self.text_dim, font=("Arial", 9, "bold")).pack(anchor="w")
        ttl_entry_frame = tk.Frame(card, bg=self.card_bg)
        ttl_entry_frame.pack(anchor="w", pady=(5, 0))
        self.ttl_entry = tk.Entry(ttl_entry_frame, width=10, bg="#333", fg="white", insertbackground="white", relief="flat")
        self.ttl_entry.insert(0, "65")
        self.ttl_entry.pack(side=tk.LEFT, ipady=3)
        ModernButton(ttl_entry_frame, "?", command=self.show_help, bg="#444", hover_bg="#555").pack(side=tk.LEFT, padx=10)

        ModernButton(self.root, "APPLY INFINITE PLAN", command=self.apply_custom_ttl, bg=self.accent_green, hover_bg="#3d8b40").pack(fill=tk.X, padx=20, pady=15)

        actions = tk.Frame(self.root, bg=self.primary_bg)
        actions.pack(fill=tk.X, padx=20)
        ModernButton(actions, "TEST CONNECTION", command=self.test_connection, bg=self.accent_blue, hover_bg="#1976D2").pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 5))
        ModernButton(actions, "RESET TO DEFAULT", command=self.reset_ttl, bg="#444", hover_bg="#555").pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(5, 0))

        tk.Label(self.root, text="Activity Log", bg=self.primary_bg, fg=self.text_dim, font=("Arial", 8, "bold")).pack(anchor="w", padx=25, pady=(15, 0))
        self.log_area = scrolledtext.ScrolledText(self.root, height=10, width=50, bg="#0a0a0a", fg="#4CAF50", font=("Courier", 10), borderwidth=0, padx=10, pady=10)
        self.log_area.pack(fill=tk.BOTH, expand=True, padx=20, pady=(5, 20))

    def update_ttl_from_carrier(self, selection):
        value = self.carriers.get(selection)
        if value:
            self.ttl_entry.delete(0, tk.END)
            self.ttl_entry.insert(0, value)
            self.log(f"Profile: {selection}")

    def show_help(self):
        msg = "Verizon: 65\nT-Mobile: 64\n\nSets IPv4/v6 Stack + Windows Registry."
        messagebox.showinfo("Guide", msg)

    def log(self, message):
        self.log_area.insert(tk.END, f"> {message}\n")
        self.log_area.see(tk.END)

    def run_command(self, cmd):
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, check=True)
            return result.stdout.strip()
        except Exception as e:
            self.log(f"Error: {str(e).split(':')[-1]}")
            return None

    def set_windows_registry(self, value):
        try:
            import winreg
            keys = [
                (winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Services\Tcpip\Parameters"),
                (winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Services\Tcpip6\Parameters")
            ]
            for root_key, sub_key in keys:
                with winreg.OpenKey(root_key, sub_key, 0, winreg.KEY_SET_VALUE) as key:
                    winreg.SetValueEx(key, "DefaultTTL", 0, winreg.REG_DWORD, int(value))
            self.log("Registry updated.")
            return True
        except Exception as e:
            self.log(f"Registry Error: {str(e)}")
            return False

    def apply_custom_ttl(self):
        val = self.ttl_entry.get().strip()
        if not val.isdigit():
            messagebox.showerror("Error", "Invalid TTL.")
            return

        self.log(f"Applying TTL {val}...")
        if platform.system() == "Windows":
            self.run_command(f"netsh int ipv4 set global defaultcurhoplimit={val} store=persistent")
            self.run_command(f"netsh int ipv6 set global defaultcurhoplimit={val} store=persistent")
            self.set_windows_registry(val)
        else:
            self.run_command(f"sysctl -w net.inet.ip.ttl={val}")
            self.run_command(f"sysctl -w net.inet6.ip6.hlim={val}")
        self.log("Configuration applied.")

    def reset_ttl(self):
        default = "128" if platform.system() == "Windows" else "64"
        self.log(f"Resetting to {default}...")
        if platform.system() == "Windows":
            self.run_command(f"netsh int ipv4 set global defaultcurhoplimit={default} store=persistent")
            self.run_command(f"netsh int ipv6 set global defaultcurhoplimit={default} store=persistent")
            self.set_windows_registry(default)
        else:
            self.run_command(f"sysctl -w net.inet.ip.ttl={default}")
            self.run_command(f"sysctl -w net.inet6.ip6.hlim={default}")
        self.log("Reset complete.")

    def test_connection(self):
        self.log("Testing active TTL...")
        cmd = "ping -n 1 127.0.0.1" if platform.system() == "Windows" else "ping -c 1 127.0.0.1"
        out = self.run_command(cmd)
        if out:
            match = re.search(r"ttl=(\d+)", out, re.I)
            if match:
                curr = match.group(1)
                self.log(f"Active TTL: {curr}")
                if curr == self.ttl_entry.get().strip(): self.log("BYPASS VERIFIED.")

if __name__ == "__main__":
    if not is_admin():
        elevate()
    else:
        root = tk.Tk()
        app = TTLUtilityApp(root)
        root.mainloop()
