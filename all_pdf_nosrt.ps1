# PowerShell Script

# Get list of mp4 files in the current directory
Get-ChildItem -Filter "*.mp4" | ForEach-Object {
    # Check if corresponding pdf exists
    $pdf_name = [System.IO.Path]::GetFileNameWithoutExtension($_.Name) + ".pdf"
    if (-Not (Test-Path $pdf_name)) {
        # pdf doesn't exist, print the file name
        Write-Host "Processing file: $($_.Name)"

        # Run python script
        python D:\Video2PDF\Video2PDF\video2pdf2.py --noshow $_.Name
    }
}
