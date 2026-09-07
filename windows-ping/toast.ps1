param(
  [string]$Title = "Ping",
  [string]$Body = "",
  [switch]$Sound
)
$ErrorActionPreference = "SilentlyContinue"
if (Test-Path (Join-Path $PSScriptRoot "MUTE")) { return }
$Aumid = "Tools.Ping"
$key = "HKCU:\Software\Classes\AppUserModelId\$Aumid"
if (-not (Test-Path $key)) { New-Item -Path $key -Force | Out-Null }
New-ItemProperty -Path $key -Name "DisplayName" -Value "Tools ping" -PropertyType String -Force | Out-Null
Add-Type -AssemblyName System.Runtime.WindowsRuntime | Out-Null
[Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] | Out-Null
[Windows.Data.Xml.Dom.XmlDocument, Windows.Data.Xml.Dom, ContentType = WindowsRuntime] | Out-Null
function Esc([string]$s) {
  ($s -replace "&", "&amp;" -replace "<", "&lt;" -replace ">", "&gt;" -replace '"', "&quot;")
}
$audio = if ($Sound) { '<audio src="ms-winsoundevent:Notification.Default"/>' } else { '<audio silent="true"/>' }
$xmlText = @"
<toast duration="short">
  <visual>
    <binding template="ToastGeneric">
      <text>$(Esc $Title)</text>
      <text>$(Esc $Body)</text>
    </binding>
  </visual>
  $audio
</toast>
"@
$xml = New-Object Windows.Data.Xml.Dom.XmlDocument
$xml.LoadXml($xmlText)
$toast = [Windows.UI.Notifications.ToastNotification]::new($xml)
[Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier($Aumid).Show($toast)
