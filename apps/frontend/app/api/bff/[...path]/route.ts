import { NextRequest, NextResponse } from 'next/server';
import { auth } from "@/auth";

export const dynamic = 'force-dynamic';
export const revalidate = 0;
export const fetchCache = 'force-no-store';
export const runtime = 'nodejs';
export const maxDuration = 120;

// Backend configuration
const defaultBackend = process.env.NODE_ENV === 'development'
  ? 'http://localhost:8000'
  : 'https://resume-matcher-backend-j06k.onrender.com';
const BACKEND_BASE = (process.env.NEXT_PUBLIC_API_BASE || process.env.NEXT_PUBLIC_API_URL || defaultBackend).replace(/\/$/, '');

/**
 * Clean, production-ready BFF proxy that properly handles authentication
 * between NextAuth frontend and FastAPI backend
 */

export async function GET(req: NextRequest, ctx: { params: Promise<{ path: string[] }> }) {
  return await proxyToBackend(req, await ctx?.params);
}

export async function POST(req: NextRequest, ctx: { params: Promise<{ path: string[] }> }) {
  return await proxyToBackend(req, await ctx?.params);
}

export async function PUT(req: NextRequest, ctx: { params: Promise<{ path: string[] }> }) {
  return await proxyToBackend(req, await ctx?.params);
}

export async function PATCH(req: NextRequest, ctx: { params: Promise<{ path: string[] }> }) {
  return await proxyToBackend(req, await ctx?.params);
}

export async function DELETE(req: NextRequest, ctx: { params: Promise<{ path: string[] }> }) {
  return await proxyToBackend(req, await ctx?.params);
}

async function proxyToBackend(req: NextRequest, params: { path: string[] } | undefined) {
  const joined = (params?.path ?? []).join('/');
  
  // Security: Only allow API v1 endpoints
  if (!joined.startsWith('api/v1/')) {
    return NextResponse.json({ error: 'FORBIDDEN', detail: 'Invalid API path' }, { status: 403 });
  }

  // Check authentication for protected endpoints
  const session = await auth();
  const isProtectedEndpoint = requiresAuthentication(joined, req.method);
  
  if (isProtectedEndpoint && !session?.user) {
    console.log(`Authentication required for ${req.method} ${joined} - no session found`);
    return NextResponse.json({ 
      error: 'AUTHENTICATION_REQUIRED', 
      detail: 'Please sign in to access this resource' 
    }, { status: 401 });
  }

  // Build backend URL
  const backendUrl = `${BACKEND_BASE}/${joined}${req.nextUrl.search || ''}`;
  
  // Prepare headers for backend request
  const backendHeaders = await prepareBackendHeaders(req, session);
  
  // Prepare request body
  const requestBody = await prepareRequestBody(req);
  
  // Make request to backend
  try {
    console.log(`=== BACKEND PROXY REQUEST ===`);
    console.log(`Proxying ${req.method} ${joined} to backend`, {
      backendUrl,
      hasSession: !!session,
      hasAuth: backendHeaders.has('authorization'),
      authType: session?.accessToken ? 'accessToken' : session?.user ? 'fallback' : 'none',
      backend: BACKEND_BASE,
      requestBodyType: requestBody ? typeof requestBody : 'none',
      contentType: req.headers.get('content-type')
    });

    // Enhanced logging for upload requests
    if (joined.includes('upload')) {
      console.log(`=== UPLOAD REQUEST DETAILS ===`);
      console.log(`Method: ${req.method}`);
      console.log(`Path: ${joined}`);
      console.log(`Full backend URL: ${backendUrl}`);
      console.log(`Request body present: ${!!requestBody}`);
      console.log(`Request body type: ${typeof requestBody}`);
      console.log(`Request body constructor: ${requestBody?.constructor?.name || 'unknown'}`);
      console.log(`Content-Type: ${req.headers.get('content-type')}`);
      console.log(`Authorization header: ${backendHeaders.has('authorization') ? 'present' : 'missing'}`);
      console.log(`User ID: ${session?.user?.id || 'none'}`);
      
      // Log FormData details if it's a FormData object
      if (requestBody instanceof FormData) {
        console.log(`FormData entries:`, Array.from(requestBody.keys()));
        for (const [key, value] of requestBody.entries()) {
          if (value instanceof File) {
            console.log(`FormData file: ${key} = ${value.name} (${value.size} bytes, ${value.type})`);
          } else {
            console.log(`FormData field: ${key} = ${typeof value === 'string' ? value.substring(0, 100) : value}`);
          }
        }
      }
    }

    const backendResponse = await fetch(backendUrl, {
      method: req.method,
      headers: backendHeaders,
      body: requestBody,
      cache: 'no-store',
      redirect: 'manual',
    });

    // Handle backend response
    return await handleBackendResponse(backendResponse, joined);

  } catch (error) {
    console.error(`Backend request failed for ${joined}:`, error);
    return NextResponse.json(
      { 
        error: 'BACKEND_ERROR', 
        detail: 'Failed to communicate with backend service',
        backend_url: BACKEND_BASE 
      },
      { status: 502 }
    );
  }
}

function requiresAuthentication(path: string, method: string): boolean {
  // List of endpoints that require authentication
  const protectedPaths = [
    'api/v1/resumes/upload',
    'api/v1/resumes/improve', 
    'api/v1/jobs/upload',
    'api/v1/match',
    'api/v1/me/credits',
    'api/v1/use-credits',
    'api/v1/credits/debit'
  ];

  // All non-GET requests to /api/v1/resumes and /api/v1/jobs require auth
  if (method !== 'GET' && (path.startsWith('api/v1/resumes') || path.startsWith('api/v1/jobs'))) {
    return true;
  }

  // Check specific protected paths
  return protectedPaths.some(protectedPath => path.startsWith(protectedPath));
}

async function prepareBackendHeaders(req: NextRequest, session: any): Promise<Headers> {
  const headers = new Headers();
  
  const contentType = req.headers.get('content-type') || '';
  const isMultipart = contentType.includes('multipart/form-data');
  
  // Copy relevant headers from original request, but handle multipart specially
  const preserveHeaders = ['accept', 'user-agent'];
  
  // For non-multipart requests, preserve content-type
  if (!isMultipart) {
    preserveHeaders.push('content-type');
  }
  
  preserveHeaders.forEach(header => {
    const value = req.headers.get(header);
    if (value) headers.set(header, value);
  });

  // For multipart/form-data, DON'T set content-type header
  // Let fetch() set it automatically with the correct boundary
  if (isMultipart) {
    console.log('Multipart upload detected - letting fetch() set content-type with boundary');
  }

  // Set default accept header if not present
  if (!headers.has('accept')) {
    headers.set('accept', 'application/json');
  }

  // Enhanced authentication logging
  console.log('=== BFF AUTH PROCESSING ===');
  console.log('Session data:', {
    hasSession: !!session,
    hasAccessToken: !!session?.accessToken,
    hasUser: !!session?.user,
    userId: session?.user?.id,
    userEmail: session?.user?.email
  });

  // Add authentication if session exists
  if (session?.accessToken) {
    // Use the backend token from NextAuth
    console.log('Using session.accessToken for backend auth:', session.accessToken.substring(0, 20) + '...');
    headers.set('authorization', `Bearer ${session.accessToken}`);
  } else if (session?.user) {
    // Fallback: create a simple auth header with user info
    const authValue = createFallbackAuth(session.user);
    console.log('Creating fallback auth token:', authValue.substring(0, 30) + '...');
    headers.set('authorization', authValue);
    
    // Also send user info in custom headers for backend user identification
    headers.set('x-user-id', session.user.id || '');
    headers.set('x-user-email', session.user.email || '');
    headers.set('x-auth-provider', 'nextauth-google');
    
    console.log('Added custom headers for user identification');
  } else {
    console.log('No authentication available - sending unauthenticated request');
  }

  console.log('Final headers prepared for backend:', {
    hasAuth: headers.has('authorization'),
    hasUserId: headers.has('x-user-id'),
    contentType: headers.get('content-type')
  });

  return headers;
}

function createFallbackAuth(user: any): string {
  // Create a simple auth token for backend identification
  const authData = {
    user_id: user.id,
    email: user.email,
    name: user.name,
    provider: 'google',
    timestamp: Date.now()
  };
  
  const token = Buffer.from(JSON.stringify(authData)).toString('base64url');
  return `Bearer gojob_fallback_${token}`;
}

async function prepareRequestBody(req: NextRequest): Promise<BodyInit | undefined> {
  if (req.method === 'GET' || req.method === 'HEAD') {
    return undefined;
  }

  const contentType = req.headers.get('content-type') || '';
  
  // For file uploads (multipart/form-data), we need to recreate the FormData
  // because req.body ReadableStream can only be read once in Next.js App Router
  if (contentType.includes('multipart/form-data')) {
    try {
      // Read the FormData from the request
      const formData = await req.formData();
      console.log('FormData successfully parsed for upload:', {
        hasFormData: !!formData,
        entries: Array.from(formData.keys()),
        fileField: formData.has('file') ? 'present' : 'missing'
      });
      return formData;
    } catch (error) {
      console.error('Failed to parse FormData from request:', error);
      throw error;
    }
  }

  // For JSON requests, read the JSON body
  if (contentType.includes('application/json')) {
    try {
      const text = await req.text();
      return text;
    } catch (error) {
      console.error('Failed to read JSON body:', error);
      return undefined;
    }
  }

  // For other request types, try to read as text
  try {
    const text = await req.text();
    return text || undefined;
  } catch (error) {
    console.error('Failed to read request body as text:', error);
    return undefined;
  }
}

async function handleBackendResponse(response: Response, path: string): Promise<NextResponse> {
  const contentType = response.headers.get('content-type') || '';
  
  // Enhanced response logging
  console.log(`=== BACKEND RESPONSE ===`);
  console.log(`Response for ${path}:`, {
    status: response.status,
    statusText: response.statusText,
    contentType,
    ok: response.ok
  });
  
  // Prepare response headers
  const responseHeaders = new Headers();
  responseHeaders.set('content-type', contentType);
  responseHeaders.set('cache-control', 'no-store');

  try {
    if (contentType.includes('application/json')) {
      const data = await response.text();
      console.log(`Response data for ${path}:`, data.substring(0, 200) + (data.length > 200 ? '...' : ''));
      
      // Try to parse and normalize JSON response
      let jsonData;
      try {
        jsonData = data ? JSON.parse(data) : {};
      } catch (parseError) {
        console.error(`JSON parse error for ${path}:`, parseError);
        jsonData = { raw: data };
      }

      // Special handling for credits endpoint
      if (path === 'api/v1/me/credits') {
        jsonData = normalizeCreditsResponse(jsonData);
      }

      // Log response for debugging
      if (!response.ok) {
        console.error(`Backend error for ${path}:`, {
          status: response.status,
          statusText: response.statusText,
          data: jsonData
        });
      } else {
        console.log(`Successful response for ${path}:`, {
          status: response.status,
          dataKeys: typeof jsonData === 'object' ? Object.keys(jsonData) : 'not-object'
        });
      }

      const responseBody = JSON.stringify(jsonData);
      return new NextResponse(responseBody, {
        status: response.status,
        headers: responseHeaders
      });
    }

    // For non-JSON responses, pass through as-is
    return new NextResponse(response.body, {
      status: response.status,
      headers: responseHeaders
    });

  } catch (error) {
    console.error(`Failed to process backend response for ${path}:`, error);
    return NextResponse.json(
      { error: 'RESPONSE_PROCESSING_ERROR', detail: 'Failed to process backend response' },
      { status: 500 }
    );
  }
}

function normalizeCreditsResponse(data: any): any {
  // Normalize different possible credit response formats
  const balance = (
    typeof data?.data?.balance === 'number' ? data.data.balance
    : typeof data?.balance === 'number' ? data.balance
    : typeof data?.data?.credits === 'number' ? data.data.credits
    : typeof data?.credits === 'number' ? data.credits
    : 0
  );
  
  return { balance, raw: data };
}
