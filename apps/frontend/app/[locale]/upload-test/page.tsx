import { FileUpload } from '@/components/upload/file-upload'

export default function UploadTestPage() {
  return (
    <div className="container mx-auto py-8">
      <div className="text-center mb-8">
        <h1 className="text-3xl font-bold">File Upload Test</h1>
        <p className="text-gray-600 mt-2">
          Test the file upload system with Render Persistent Disk
        </p>
      </div>
      
      <FileUpload />
      
      <div className="mt-8 text-center text-sm text-gray-500">
        <p>Files are stored securely on Render Persistent Disk</p>
        <p>Backend URL: {process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:4000'}</p>
      </div>
    </div>
  )
}
