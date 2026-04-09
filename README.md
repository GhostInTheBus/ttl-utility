# Cellular TTL Manager
**Bypass Hotspot Limits on Verizon & T-Mobile**

This utility allows your computer to share your phone's regular data plan instead of being restricted by hotspot caps. It works by adjusting your system's "TTL" (Time-to-Live) settings to match your phone's internal signature.

## 🚀 Quick Start
1. **Download:** Get the latest version from the [Releases](https://github.com/GhostInTheBus/ttl-utility/releases) page.
2. **Run:** 
   - **Mac:** Double-click `CellularTTL`. (If it blocks you, **Right-click > Open**).
   - **Windows:** Double-click `CellularTTL.exe`.
3. **Select Carrier:**
   - **Verizon / Visible:** Use **65**.
   - **T-Mobile / Metro:** Use **64**.
4. **Apply:** Click **"Apply Target TTL"**. You will be asked for your password/TouchID to confirm the system change.
5. **Verify:** Click **"Test Connection"**. If it says "CONFIRMED," you are good to go.

## 🛠 Why this works (The Vibe)
Most carriers track hotspot usage by looking for a specific "TTL" number in your data. Computers usually send a different number than phones. This tool makes your computer "whisper" the same number as your phone, so the carrier registers the data as coming from the device in your hand, not the laptop on your desk.

## 📜 License
This tool is open-source under the MIT License. Vibe coded by Gemini CLI.
