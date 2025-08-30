import { NextRequest, NextResponse } from 'next/server';
import { auth } from "@/auth";

export const dynamic = 'force-dynamic';
export const revalidate = 0;

export async function POST(req: NextRequest) {
  try {
    // Check if user is authenticated
    const session = await auth();
    
    if (!session?.user) {
      return NextResponse.json(
        { error: 'AUTHENTICATION_REQUIRED', detail: 'Please sign in to upload files' },
        { status: 401 }
      );
    }

    // Extract file from form data
    const formData = await req.formData();
    const file = formData.get('file') as File | null;

    if (!file) {
      return NextResponse.json(
        { error: 'NO_FILE', detail: 'No file provided' },
        { status: 400 }
      );
    }

    // Validate file type
    const allowedTypes = [
      'application/pdf',
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    ];

    if (!allowedTypes.includes(file.type)) {
      return NextResponse.json(
        { error: 'INVALID_FILE_TYPE', detail: 'Only PDF and DOCX files are allowed' },
        { status: 400 }
      );
    }

    // Validate file size (2MB limit)
    const maxSize = 2 * 1024 * 1024; // 2MB
    if (file.size > maxSize) {
      return NextResponse.json(
        { error: 'FILE_TOO_LARGE', detail: 'File must be smaller than 2MB' },
        { status: 400 }
      );
    }

    // For now, we'll create a mock response since we need to handle backend integration
    // In production, this would forward to the actual backend
    const mockResumeId = `resume_${Date.now()}_${Math.random().toString(36).substring(2, 15)}`;
    
    // Simulate processing time
    await new Promise(resolve => setTimeout(resolve, 1000));

    // Mock successful response that matches what the frontend expects
    const response = {
      resume_id: mockResumeId,
      message: 'Resume uploaded successfully',
      file_name: file.name,
      file_size: file.size,
      user_id: session.user.id || session.user.email,
      uploaded_at: new Date().toISOString()
    };

    console.log('File upload successful:', {
      fileName: file.name,
      fileSize: file.size,
      userId: session.user.id || session.user.email,
      resumeId: mockResumeId
    });

    return NextResponse.json(response, { status: 200 });

  } catch (error) {
    console.error('Resume upload error:', error);
    return NextResponse.json(
      { error: 'UPLOAD_FAILED', detail: 'An error occurred while uploading the file' },
      { status: 500 }
    );
  }
}
