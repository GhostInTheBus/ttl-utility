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
        self.root.title("Cellular TTL Utility")
        self.root.geometry("500x520")
        
        self.os_type = platform.system()
        self.is_admin = self.check_admin()
        
        self.setup_ui()
        self.log("Universal Cellular TTL Manager (Vibe Coded)")
        self.log(f"OS: {self.os_type} | UID: {getattr(os, 'getuid', lambda: 'N/A')()}")
        self.log(f"Admin Access Granted: {'Yes' if self.is_admin else 'No'}")
        
        if self.is_admin:
            self.log("Ready to apply system-level changes.")
        else:
            self.log("Limited access. Please use 'Elevate to Admin' for full features.")

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
        self.log("Requesting administrative elevation...")
        try:
            if self.os_type == "Windows":
                import ctypes
                ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
            elif self.os_type == "Darwin":
                script = f'do shell script "{sys.executable} {" ".join(sys.argv)}" with administrator privileges'
                subprocess.run(["osascript", "-e", script], check=True)
            elif self.os_type == "Linux":
                os.execvp("sudo", ["sudo", sys.executable] + sys.argv)
            sys.exit()
        except subprocess.CalledProcessError:
            self.log("Elevation cancelled by user.")
        except Exception as e:
            self.log(f"Elevation Error: {str(e)}")

    def setup_ui(self):
        # Header
        tk.Label(self.root, text="Cellular TTL Manager", font=("Arial", 16, "bold")).pack(pady=(10, 0))
        tk.Label(self.root, text="Turns your hotspot into an infinite phone plan.", font=("Arial", 9, "italic"), fg="#4CAF50").pack(pady=(0, 10))

        # Carrier Selection Dropdown
        carrier_frame = tk.Frame(self.root)
        carrier_frame.pack(pady=5)
        tk.Label(carrier_frame, text="Select Carrier:").grid(row=0, column=0, padx=5)

        self.carrier_var = tk.StringVar(self.root)
        self.carrier_var.set("Verizon / Visible (65)") # Default
        self.carriers = {
            "Verizon / Visible (65)": "65",
            "T-Mobile / Metro (64)": "64",
            "Custom": ""
        }

        self.carrier_menu = tk.OptionMenu(carrier_frame, self.carrier_var, *self.carriers.keys(), command=self.update_ttl_from_carrier)
        self.carrier_menu.config(width=20)
        self.carrier_menu.grid(row=0, column=1, padx=5)

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

        tk.Button(btn_frame, text="Apply Target TTL (IPv4+v6)", command=self.apply_custom_ttl, width=25, bg="#4CAF50", fg="white").grid(row=0, column=0, columnspan=2, padx=5, pady=5)
        tk.Button(btn_frame, text="Reset to Default", command=self.reset_ttl, width=20).grid(row=1, column=0, padx=5, pady=5)
        tk.Button(btn_frame, text="Test Connection (Ping)", command=self.test_connection, width=20, bg="#2196F3", fg="white").grid(row=1, column=1, padx=5, pady=5)
        tk.Button(btn_frame, text="Elevate to Admin", command=self.elevate, width=20).grid(row=2, column=0, columnspan=2, pady=5)

        # Log Output
        tk.Label(self.root, text="Activity Log:").pack(anchor="w", padx=20)
        self.log_area = scrolledtext.ScrolledText(self.root, height=12, width=55)
        self.log_area.pack(padx=20, pady=5)

    def update_ttl_from_carrier(self, selection):
        value = self.carriers.get(selection)
        if value:
            self.ttl_entry.delete(0, tk.END)
            self.ttl_entry.insert(0, value)
            self.log(f"Switched to {selection} configuration.")

    def show_help(self):
        help_text = (
            "Which TTL should I use?\n\n"
            "64 (T-Mobile/Metro): The standard default for mobile devices. "
            "Use this if you are on T-Mobile to make your computer look like a phone.\n\n"
            "65 (Verizon/Visible): Verizon often expects a 'hop' from the phone. "
            "Starting at 65 ensures the signal reaches them at 64.\n\n"
            "Tip: If one doesn't work, try the other!\n"
            "(This app now sets both IPv4 and IPv6 settings simultaneously.)"
        )
        messagebox.showinfo("Carrier TTL Guide", help_text)

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

        self.log(f"Setting IPv4 and IPv6 TTL to {value}...")
        cmds = []
        if self.os_type == "Windows":
            cmds.append(f"netsh int ipv4 set global defaultcurhoplimit={value} store=persistent")
            cmds.append(f"netsh int ipv6 set global defaultcurhoplimit={value} store=persistent")
        elif self.os_type == "Darwin":
            cmds.append(f"sysctl -w net.inet.ip.ttl={value}")
            cmds.append(f"sysctl -w net.inet6.ip6.hlim={value}")
        elif self.os_type == "Linux":
            cmds.append(f"sysctl -w net.ipv4.ip_default_ttl={value}")
            cmds.append(f"sysctl -w net.ipv6.conf.all.hop_limit={value}")
            cmds.append(f"sysctl -w net.ipv6.conf.default.hop_limit={value}")
        else:
            self.log("Unsupported OS for this operation.")
            return

        success = True
        for cmd in cmds:
            if self.run_command(cmd) is None:
                success = False
        
        if success:
            self.log(f"Successfully applied TTL {value} to all stacks.")

    def reset_ttl(self):
        if not self.is_admin:
            messagebox.showwarning("Admin Required", "Please elevate to administrator to reset TTL.")
            return

        default_ttl = 128 if self.os_type == "Windows" else 64
        self.log(f"Resetting IPv4 and IPv6 to default ({default_ttl})...")
        self.set_ttl(default_ttl)

    def test_connection(self):
        self.log("Testing connection (pinging localhost)...")
        ping_cmd = "ping -n 1 127.0.0.1" if self.os_type == "Windows" else "ping -c 1 127.0.0.1"
        output = self.run_command(ping_cmd)
        
        if output:
            ttl_match = re.search(r"ttl=(\d+)", output, re.IGNORECASE)
            if ttl_match:
                current_ttl = ttl_match.group(1)
                self.log(f"Test Successful! Current Active TTL: {current_ttl}")
                target = self.ttl_entry.get().strip()
                if current_ttl == target:
                    self.log(f"CONFIRMED: Your connection is using the custom TTL ({target}).")
                else:
                    self.log(f"NOTICE: System is currently using TTL {current_ttl}.")
            else:
                self.log("Could not parse TTL from ping output.")
                self.log(f"Raw Output: {output}")

if __name__ == "__main__":
    root = tk.Tk()
    app = TTLUtilityApp(root)
    root.mainloop()
