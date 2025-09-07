# PowerShell Script für Test-Upload
# Test-Upload-Script für Resume Matcher

Write-Host "🚀 Teste Upload-Funktionalität..." -ForegroundColor Green

# 1. Health Check
Write-Host "`n1️⃣ Health Check..." -ForegroundColor Yellow
try {
    $healthResponse = Invoke-WebRequest -Uri "http://localhost:3000/api/health" -Method GET
    Write-Host "✅ Health Check Status: $($healthResponse.StatusCode)" -ForegroundColor Green
    Write-Host "Response: $($healthResponse.Content)" -ForegroundColor Cyan
} catch {
    Write-Host "❌ Health Check fehlgeschlagen: $($_.Exception.Message)" -ForegroundColor Red
}

# 2. Test-Upload vorbereiten
$testFile = "test-resume.pdf"
if (-not (Test-Path $testFile)) {
    Write-Host "`n📄 Erstelle Test-PDF..." -ForegroundColor Yellow
    # Einfacher PDF-Inhalt
    $pdfContent = @"
%PDF-1.4
1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj
2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj
3 0 obj<</Type/Page/Parent 2 0 R/MediaBox[0 0 612 792]/Contents 4 0 R>>endobj
4 0 obj<</Length 44>>stream
BT/F1 12 Tf 100 700 Td(Test Resume Upload)Tj ET
endstream endobj
xref 0 5
0000000000 65535 f 
0000000009 00000 n 
0000000058 00000 n 
0000000115 00000 n 
0000000206 00000 n 
trailer<</Size 5/Root 1 0 R>>startxref 299 %%EOF
"@
    $pdfContent | Out-File -FilePath $testFile -Encoding ASCII -NoNewline
}

# 3. Upload testen
Write-Host "`n2️⃣ Teste Upload..." -ForegroundColor Yellow
try {
    # Multipart Form-Data für Upload
    $boundary = [System.Guid]::NewGuid().ToString()
    $filePath = (Resolve-Path $testFile).Path
    $fileBytes = [System.IO.File]::ReadAllBytes($filePath)
    $fileName = (Get-Item $filePath).Name
    
    $body = @"
--$boundary
Content-Disposition: form-data; name="file"; filename="$fileName"
Content-Type: application/pdf

$([System.Text.Encoding]::Default.GetString($fileBytes))
--$boundary
Content-Disposition: form-data; name="kind"

resume
--$boundary
Content-Disposition: form-data; name="userId"

test-user-123
--$boundary--
"@
    
    $uploadResponse = Invoke-WebRequest -Uri "http://localhost:3000/api/uploads" -Method POST -Body $body -ContentType "multipart/form-data; boundary=$boundary"
    Write-Host "✅ Upload Status: $($uploadResponse.StatusCode)" -ForegroundColor Green
    Write-Host "Response: $($uploadResponse.Content)" -ForegroundColor Cyan
    
    # Upload-ID extrahieren
    $uploadData = $uploadResponse.Content | ConvertFrom-Json
    $uploadId = $uploadData.uploadId
    
    if ($uploadId) {
        Write-Host "`n3️⃣ Teste Download..." -ForegroundColor Yellow
        $downloadResponse = Invoke-WebRequest -Uri "http://localhost:3000/api/files/$uploadId" -Method GET
        Write-Host "✅ Download Status: $($downloadResponse.StatusCode)" -ForegroundColor Green
        Write-Host "Content-Type: $($downloadResponse.Headers.'Content-Type')" -ForegroundColor Cyan
        Write-Host "Content-Length: $($downloadResponse.Headers.'Content-Length')" -ForegroundColor Cyan
    }
    
} catch {
    Write-Host "❌ Upload fehlgeschlagen: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "Details: $($_.ErrorDetails.Message)" -ForegroundColor Red
}

# 4. Admin-Endpunkte testen
Write-Host "`n4️⃣ Teste Admin-Endpunkte..." -ForegroundColor Yellow
try {
    $headers = @{ "Authorization" = "Bearer change-me" }
    
    # Disk-Status
    $diskResponse = Invoke-WebRequest -Uri "http://localhost:3000/api/admin/disk" -Method GET -Headers $headers
    Write-Host "✅ Admin Disk Status: $($diskResponse.StatusCode)" -ForegroundColor Green
    Write-Host "Response: $($diskResponse.Content)" -ForegroundColor Cyan
    
    # Export
    $exportResponse = Invoke-WebRequest -Uri "http://localhost:3000/api/admin/export" -Method POST -Headers $headers
    Write-Host "✅ Admin Export Status: $($exportResponse.StatusCode)" -ForegroundColor Green
    Write-Host "Response: $($exportResponse.Content)" -ForegroundColor Cyan
    
} catch {
    Write-Host "❌ Admin-Tests fehlgeschlagen: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`n🎉 Upload-Tests abgeschlossen!" -ForegroundColor Green
Write-Host "📊 Prisma Studio: http://localhost:5555" -ForegroundColor Blue
Write-Host "🌐 Frontend: http://localhost:3000" -ForegroundColor Blue
