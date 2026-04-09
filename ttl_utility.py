import os
import sys
import platform
import subprocess
import re
import tkinter as tk
from tkinter import messagebox, scrolledtext, ttk

class TTLUtilityApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Cellular TTL Utility")
        self.root.geometry("520x560")
        
        # Configure Styles
        self.style = ttk.Style()
        self.style.theme_use('aqua' if platform.system() == "Darwin" else 'clam')
        
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
                # ShellExecuteW with 'runas' is the standard way to trigger UAC on Windows
                params = " ".join([f'"{arg}"' for arg in sys.argv])
                result = ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, params, None, 1)
                if result <= 32:
                    self.log(f"Windows UAC Error Code: {result}")
                else:
                    self.log("UAC prompt triggered. Restarting...")
                    sys.exit()
            elif self.os_type == "Darwin":
                # Use 'quoted form of' in AppleScript for rock-solid path handling
                script = f'do shell script (quoted form of "{sys.executable}") & " " & {" & \" \" & ".join([f"quoted form of \"{arg}\"" for arg in sys.argv])} with administrator privileges'
                self.log("Launching AppleScript elevation prompt...")
                result = subprocess.run(["osascript", "-e", script], capture_output=True, text=True)
                if result.returncode != 0:
                    self.log(f"AppleScript Error: {result.stderr.strip()}")
                else:
                    self.log("Elevation command sent successfully. Restarting...")
                    sys.exit()
            elif self.os_type == "Linux":
                os.execvp("sudo", ["sudo", sys.executable] + sys.argv)
            sys.exit()
        except subprocess.CalledProcessError:
            self.log("Elevation cancelled by user.")
        except Exception as e:
            self.log(f"Elevation Error: {str(e)}")

    def setup_ui(self):
        # Main Container with padding
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Header Section
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Label(header_frame, text="Cellular TTL Manager", font=("Arial", 20, "bold")).pack()
        ttk.Label(header_frame, text="Turns your hotspot into an infinite phone plan.", font=("Arial", 10, "italic"), foreground="#4CAF50").pack()

        # Configuration Card
        config_frame = ttk.LabelFrame(main_frame, text=" Configuration ", padding="15")
        config_frame.pack(fill=tk.X, pady=10)

        # Carrier Row
        ttk.Label(config_frame, text="Select Carrier:").grid(row=0, column=0, sticky="w", pady=5)
        self.carrier_var = tk.StringVar(self.root)
        self.carrier_var.set("Verizon / Visible (65)")
        self.carriers = {
            "Verizon / Visible (65)": "65",
            "T-Mobile / Metro (64)": "64",
            "Custom": ""
        }
        self.carrier_menu = ttk.OptionMenu(config_frame, self.carrier_var, self.carrier_var.get(), *self.carriers.keys(), command=self.update_ttl_from_carrier)
        self.carrier_menu.grid(row=0, column=1, sticky="ew", padx=(10, 0), pady=5)

        # TTL Row
        ttk.Label(config_frame, text="Target TTL:").grid(row=1, column=0, sticky="w", pady=5)
        ttl_input_frame = ttk.Frame(config_frame)
        ttl_input_frame.grid(row=1, column=1, sticky="w", padx=(10, 0), pady=5)
        
        self.ttl_entry = ttk.Entry(ttl_input_frame, width=8)
        self.ttl_entry.insert(0, "65")
        self.ttl_entry.pack(side=tk.LEFT)
        ttk.Button(ttl_input_frame, text="?", width=3, command=self.show_help).pack(side=tk.LEFT, padx=5)

        # Main Action Button (Hero Button)
        self.apply_btn = ttk.Button(main_frame, text="Apply Infinite Plan (IPv4 + IPv6)", command=self.apply_custom_ttl)
        self.apply_btn.pack(fill=tk.X, pady=15)

        # Secondary Actions
        action_frame = ttk.Frame(main_frame)
        action_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(action_frame, text="Test Connection", command=self.test_connection).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 5))
        ttk.Button(action_frame, text="Reset Defaults", command=self.reset_ttl).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(5, 0))

        # Admin Button (only if not admin)
        if not self.is_admin:
            ttk.Button(main_frame, text="Elevate to Administrator", command=self.elevate).pack(fill=tk.X, pady=10)

        # Log Output Section
        log_label_frame = ttk.Frame(main_frame)
        log_label_frame.pack(fill=tk.X, pady=(15, 0))
        ttk.Label(log_label_frame, text="Activity Log:", font=("Arial", 10, "bold")).pack(side=tk.LEFT)
        
        self.log_area = scrolledtext.ScrolledText(main_frame, height=10, width=50, font=("Monaco", 10), background="#f8f8f8")
        self.log_area.pack(fill=tk.BOTH, expand=True, pady=(5, 0))

    def update_ttl_from_carrier(self, selection):
        value = self.carriers.get(selection)
        if value:
            self.ttl_entry.delete(0, tk.END)
            self.ttl_entry.insert(0, value)
            self.log(f"Switched to {selection} configuration.")

    def show_help(self):
        help_text = (
            "Which TTL should I use?\n\n"
            "64 (T-Mobile/Metro): The standard default for mobile devices.\n\n"
            "65 (Verizon/Visible): Verizon often expects a 'hop' from the phone. "
            "Starting at 65 ensures the signal reaches them at 64.\n\n"
            "Tip: This app sets both IPv4 and IPv6 settings simultaneously."
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
