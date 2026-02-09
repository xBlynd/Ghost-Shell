import platform
import subprocess
import json
import os
from pathlib import Path

class InfoEngine:
    @staticmethod
    def get_cloud_paths():
        """Detects Cloud Storage Mounts"""
        home = Path.home()
        clouds = []
        
        # 1. OneDrive
        onedrive = os.environ.get("OneDrive")
        if onedrive and Path(onedrive).exists():
            clouds.append({"name": "OneDrive", "path": onedrive})
            
        # 2. Google Drive (Virtual G: or Folder)
        gdrive = home / "Google Drive"
        if gdrive.exists(): 
            clouds.append({"name": "Google Drive", "path": str(gdrive)})
        
        # Check for Virtual Drives (G:)
        if os.name == "nt":
            if Path("G:/").exists():
                clouds.append({"name": "Google Drive (Virtual)", "path": "G:/"})

        return clouds

    @staticmethod
    def scan_windows_deep():
        # The 'CPU-Z' Style Scanner using PowerShell
        ps_script = r"""
        $ErrorActionPreference = "SilentlyContinue"

        # --- MOTHERBOARD & BIOS ---
        $bios = Get-CimInstance Win32_BIOS
        $base = Get-CimInstance Win32_BaseBoard
        $cs = Get-CimInstance Win32_ComputerSystem

        # --- CPU DETAIL ---
        $cpu = Get-CimInstance Win32_Processor
        
        # --- RAM DETAILED (Stick by Stick) ---
        $mem = Get-CimInstance Win32_PhysicalMemory | Select-Object Manufacturer, PartNumber, Speed, Capacity, DeviceLocator

        # --- GPU DETAILED ---
        $gpu = Get-CimInstance Win32_VideoController | Select-Object Name, VideoProcessor, DriverVersion, AdapterRAM, CurrentRefreshRate

        # --- STORAGE (NVMe/SSD distinction) ---
        $disk = Get-PhysicalDisk | Select-Object FriendlyName, MediaType, BusType, Size, Model, FirmwareVersion

        # --- NETWORK (MAC & Connection) ---
        $net = Get-NetAdapter | Where-Object Status -eq 'Up' | Select-Object Name, InterfaceDescription, MacAddress, LinkSpeed

        # --- USB DEVICES (Coolers/Hubs) ---
        # Looking for specific enthusiast gear
        $usb = Get-PnpDevice -Class 'USB', 'HIDClass' -Status 'OK' | Where-Object { $_.FriendlyName -match 'Corsair|NZXT|Liquid|Pump|AIO|Cooler|Hub|Commander|Link|Kraken' } | Select-Object FriendlyName

        $info = @{
            System = @{
                Hostname = $cs.Name
                Model = $cs.Model
                Manufacturer = $cs.Manufacturer
            }
            BIOS = @{
                Version = $bios.SMBIOSBIOSVersion
                Date = $bios.ReleaseDate
                Serial = $bios.SerialNumber
            }
            Mobo = @{
                Make = $base.Manufacturer
                Model = $base.Product
                Serial = $base.SerialNumber
            }
            CPU = @{
                Name = $cpu.Name
                Cores = $cpu.NumberOfCores
                Threads = $cpu.NumberOfLogicalProcessors
                Socket = $cpu.SocketDesignation
            }
            RAM_Sticks = @($mem)
            GPUs = @($gpu)
            Disks = @($disk)
            Network = @($net)
            Cooling = @($usb)
        }
        $info | ConvertTo-Json -Depth 4 -Compress
        """
        try:
            res = subprocess.check_output(["powershell", "-NoProfile", "-Command", ps_script], encoding="utf-8", errors="ignore")
            return json.loads(res)
        except Exception as e:
            return {"Error": str(e)}

    @staticmethod
    def get_report():
        """Orchestrates the scan based on OS"""
        info = {
            "OS_Type": platform.system(),
            "Cloud": InfoEngine.get_cloud_paths(),
            "Data": {}
        }
        
        if info["OS_Type"] == "Windows":
            info["Data"] = InfoEngine.scan_windows_deep()
        elif info["OS_Type"] == "Linux":
            info["Data"] = {"Status": "Basic Linux Scan (TODO: Implement lscpu)"}
            
        return info