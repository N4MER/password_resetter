# Cisco device password resetter

# **Author:** Zhao Xiang Yang


## Description
Performs a full password-reset procedure on supported Cisco devices by temporarily bypassing or renaming the device’s startup configuration, restoring the previous configuration, and applying updated authentication settings. 
The component automates all bootloader-level interactions (ROMMON or Switch Bootloader), removes selected passwords, sets new ones if requested, and safely rewrites the device configuration.

## How to Use the Password Reset Tool

### 1. Connect the Serial Console Cable
Connect the console cable to both the Cisco device and your computer.  
Verify that the COM port appears in your system.

---

### 2. Select the Correct Device Model
Use the Device dropdown to choose the exact router or switch model.  
This is required because each device uses a different bootloader procedure.

---

### 3. Configure Connection Settings
Enter the serial connection parameters:

- **COM Port:** for example `COM1`, `COM3`, `COM5`  
- **Baud Rate:** typically `9600` for most Cisco devices

Ensure these values match your console cable and device configuration.

---

### 4. Choose What to Reset or Configure
Select the actions you want the tool to perform:

- Remove enable password  
- Remove enable secret password  
- Remove line console password  
- Set a new enable password or enable secret  
- Set a new line console password  

If setting new passwords, fill in the corresponding fields.

---

### 5. Start the Password Reset
Click **Start** to begin.
