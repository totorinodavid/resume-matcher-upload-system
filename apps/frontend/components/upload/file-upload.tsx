'use client'

import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Upload, CheckCircle2, AlertCircle, Loader2 } from 'lucide-react'

interface UploadResult {
  id: string
  filename: string
  size: number
  uploadedAt: string
  duplicate: boolean
}

interface UploadError {
  code: string
  message: string
}

export function FileUpload() {
  const [file, setFile] = useState<File | null>(null)
  const [uploading, setUploading] = useState(false)
  const [result, setResult] = useState<UploadResult | null>(null)
  const [error, setError] = useState<UploadError | null>(null)

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0]
    if (selectedFile) {
      setFile(selectedFile)
      setResult(null)
      setError(null)
    }
  }

  const handleUpload = async () => {
    if (!file) return

    setUploading(true)
    setError(null)
    setResult(null)

    try {
      const formData = new FormData()
      formData.append('file', file)

      const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:4000'
      const response = await fetch(`${backendUrl}/api/uploads`, {
        method: 'POST',
        body: formData
      })

      const data = await response.json()

      if (!response.ok) {
        setError(data.error || { code: 'UNKNOWN', message: 'Upload failed' })
        return
      }

      setResult(data.upload)
    } catch (err) {
      setError({
        code: 'NETWORK_ERROR',
        message: 'Failed to connect to upload service'
      })
    } finally {
      setUploading(false)
    }
  }

  const handleDownload = async () => {
    if (!result) return

    try {
      const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:4000'
      const response = await fetch(`${backendUrl}/api/files/${result.id}`)
      
      if (!response.ok) {
        throw new Error('Download failed')
      }

      const blob = await response.blob()
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = result.filename
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)
    } catch (err) {
      setError({
        code: 'DOWNLOAD_ERROR',
        message: 'Failed to download file'
      })
    }
  }

  return (
    <Card className="w-full max-w-md mx-auto">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Upload className="h-5 w-5" />
          File Upload
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div>
          <Input
            type="file"
            accept=".pdf,.doc,.docx"
            onChange={handleFileChange}
            disabled={uploading}
          />
          <p className="text-sm text-gray-500 mt-1">
            Supports PDF and DOCX files up to 10MB
          </p>
        </div>

        {file && (
          <div className="text-sm text-gray-600">
            Selected: {file.name} ({Math.round(file.size / 1024)} KB)
          </div>
        )}

        <Button
          onClick={handleUpload}
          disabled={!file || uploading}
          className="w-full"
        >
          {uploading ? (
            <>
              <Loader2 className="h-4 w-4 mr-2 animate-spin" />
              Uploading...
            </>
          ) : (
            <>
              <Upload className="h-4 w-4 mr-2" />
              Upload File
            </>
          )}
        </Button>

        {error && (
          <Alert variant="destructive">
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>
              {error.message}
            </AlertDescription>
          </Alert>
        )}

        {result && (
          <Alert>
            <CheckCircle2 className="h-4 w-4" />
            <AlertDescription>
              <div className="space-y-2">
                <p>
                  {result.duplicate ? 'File already exists' : 'Upload successful'}
                </p>
                <div className="text-xs text-gray-600">
                  <p>Filename: {result.filename}</p>
                  <p>Size: {Math.round(result.size / 1024)} KB</p>
                  <p>ID: {result.id}</p>
                </div>
                <Button
                  size="sm"
                  variant="outline"
                  onClick={handleDownload}
                  className="mt-2"
                >
                  Download
                </Button>
              </div>
            </AlertDescription>
          </Alert>
        )}
      </CardContent>
    </Card>
  )
}
