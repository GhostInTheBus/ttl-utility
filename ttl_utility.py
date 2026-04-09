import os
import sys
import platform
import subprocess
import re
import tkinter as tk
from tkinter import messagebox, scrolledtext

class TTLUtilityApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Verizon TTL Utility")
        self.root.geometry("500x450")
        
        self.os_type = platform.system()
        self.is_admin = self.check_admin()
        
        self.setup_ui()
        self.log("Verizon Optimized TTL Manager (TTL=65)")
        self.log("Vibe coded by Gemini CLI.")
        self.log(f"Detected OS: {self.os_type}")
        self.log(f"Admin Privileges: {'Yes' if self.is_admin else 'No'}")
        
        if not self.is_admin:
            self.log("WARNING: Certain features require administrative privileges.")

    def check_admin(self):
        """Check if the current process has administrative/root privileges."""
        try:
            if self.os_type == "Windows":
                import ctypes
                return ctypes.windll.shell32.IsUserAnAdmin() != 0
            else:
                return os.getuid() == 0
        except AttributeError:
            return False

    def elevate(self):
        """Re-run the script with administrative privileges."""
        if self.os_type == "Windows":
            import ctypes
            ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
        elif self.os_type in ["Darwin", "Linux"]:
            os.execvp("sudo", ["sudo", sys.executable] + sys.argv)
        sys.exit()

    def setup_ui(self):
        # Header
        tk.Label(self.root, text="Verizon TTL Manager", font=("Arial", 16, "bold")).pack(pady=(10, 0))
        tk.Label(self.root, text="Changes TTL so usage registers as phone data, not hotspot.", font=("Arial", 9, "italic"), fg="#555").pack(pady=(0, 10))
        
        # Custom TTL Input
        input_frame = tk.Frame(self.root)
        input_frame.pack(pady=5)
        tk.Label(input_frame, text="Target TTL:").grid(row=0, column=0, padx=5)
        self.ttl_entry = tk.Entry(input_frame, width=5)
        self.ttl_entry.insert(0, "65")
        self.ttl_entry.grid(row=0, column=1, padx=5)
        tk.Button(input_frame, text="?", command=self.show_help, width=2).grid(row=0, column=2, padx=5)

        # Action Buttons
        btn_frame = tk.Frame(self.root)
        btn_frame.pack(pady=10)
        
        tk.Button(btn_frame, text="Apply Target TTL", command=self.apply_custom_ttl, width=20, bg="#4CAF50", fg="white").grid(row=0, column=0, padx=5, pady=5)
        tk.Button(btn_frame, text="Reset to Default", command=self.reset_ttl, width=20).grid(row=0, column=1, padx=5, pady=5)
        tk.Button(btn_frame, text="Test Connection (Ping)", command=self.test_connection, width=20, bg="#2196F3", fg="white").grid(row=1, column=0, padx=5, pady=5)
        tk.Button(btn_frame, text="Elevate to Admin", command=self.elevate, width=20).grid(row=1, column=1, padx=5, pady=5)

        # Log Output
        tk.Label(self.root, text="Activity Log:").pack(anchor="w", padx=20)
        self.log_area = scrolledtext.ScrolledText(self.root, height=12, width=55)
        self.log_area.pack(padx=20, pady=5)

    def show_help(self):
        help_text = (
            "Why 64 vs 65?\n\n"
            "64: The standard default for Android/iOS/Linux/macOS.\n\n"
            "65: Often used because your phone acts as a 'hop'. By starting at 65, "
            "the packet reaches the carrier with a TTL of 64, making it look exactly "
            "like it originated from the phone itself.\n\n"
            "Try 65 first; if it doesn't work, try 64."
        )
        messagebox.showinfo("TTL Explained", help_text)

    def apply_custom_ttl(self):
        target_ttl = self.ttl_entry.get().strip()
        if not target_ttl.isdigit():
            messagebox.showerror("Error", "Please enter a valid number for TTL.")
            return
        self.set_ttl(target_ttl)

    def log(self, message):
        self.log_area.insert(tk.END, f"> {message}\n")
        self.log_area.see(tk.END)

    def run_command(self, cmd):
        """Utility to run shell commands and return output."""
        try:
            result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            self.log(f"Error: {e.stderr.strip()}")
            return None

    def set_ttl(self, value):
        if not self.is_admin:
            if messagebox.askyesno("Admin Required", "This action requires administrative privileges. Elevate now?"):
                self.elevate()
            return

        self.log(f"Setting TTL to {value}...")
        if self.os_type == "Windows":
            cmd = f"netsh int ipv4 set global defaultcurhoplimit={value} store=persistent"
        elif self.os_type == "Darwin":
            cmd = f"sysctl -w net.inet.ip.ttl={value}"
        elif self.os_type == "Linux":
            cmd = f"sysctl -w net.ipv4.ip_default_ttl={value}"
        else:
            self.log("Unsupported OS for this operation.")
            return

        if self.run_command(cmd) is not None:
            self.log(f"Successfully set TTL to {value}.")

    def set_ttl_65(self):
        self.set_ttl("65")

    def reset_ttl(self):
        if not self.is_admin:
            messagebox.showwarning("Admin Required", "Please elevate to administrator to reset TTL.")
            return

        default_ttl = 128 if self.os_type == "Windows" else 64
        self.log(f"Resetting TTL to default ({default_ttl})...")
        
        if self.os_type == "Windows":
            cmd = f"netsh int ipv4 set global defaultcurhoplimit={default_ttl} store=persistent"
        elif self.os_type == "Darwin":
            cmd = f"sysctl -w net.inet.ip.ttl={default_ttl}"
        elif self.os_type == "Linux":
            cmd = f"sysctl -w net.ipv4.ip_default_ttl={default_ttl}"
        
        if self.run_command(cmd) is not None:
            self.log(f"Successfully reset TTL to {default_ttl}.")

    def test_connection(self):
        self.log("Testing connection (pinging localhost)...")
        ping_cmd = "ping -n 1 127.0.0.1" if self.os_type == "Windows" else "ping -c 1 127.0.0.1"
        output = self.run_command(ping_cmd)
        
        if output:
            # Parse TTL from output using Regex (case insensitive)
            ttl_match = re.search(r"ttl=(\d+)", output, re.IGNORECASE)
            if ttl_match:
                current_ttl = ttl_match.group(1)
                self.log(f"Test Successful! Current Active TTL: {current_ttl}")
                if current_ttl == "65":
                    self.log("CONFIRMED: Your connection is using the custom TTL (65).")
                else:
                    self.log(f"NOTICE: System is currently using TTL {current_ttl}.")
            else:
                self.log("Could not parse TTL from ping output.")
                self.log(f"Raw Output: {output}")

if __name__ == "__main__":
    root = tk.Tk()
    app = TTLUtilityApp(root)
    root.mainloop()
