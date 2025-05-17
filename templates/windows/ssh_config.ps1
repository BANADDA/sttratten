# PowerShell script to configure SSH on Windows
# Run on Windows VM template

# Install OpenSSH Server
Add-WindowsCapability -Online -Name OpenSSH.Server~~~~0.0.1.0

# Start and enable the service
Start-Service sshd
Set-Service -Name sshd -StartupType 'Automatic'

# Configure firewall
New-NetFirewallRule -Name sshd -DisplayName 'OpenSSH Server (sshd)' -Enabled True -Direction Inbound -Protocol TCP -Action Allow -LocalPort 22

# Create SSH directory structure if it doesn't exist
$sshdir = "C:\\ProgramData\\ssh"
if (!(Test-Path $sshdir)) {
    New-Item -ItemType Directory -Path $sshdir
}

# Create administrators_authorized_keys file
$keyfile = "C:\\ProgramData\\ssh\\administrators_authorized_keys"
$pubkey = "YOUR_SERVER_PUBLIC_KEY_HERE"
Set-Content -Path $keyfile -Value $pubkey

# Set proper permissions
icacls.exe $keyfile /inheritance:r /grant "Administrators:F" /grant "SYSTEM:F"

Write-Host "SSH Server configured successfully."