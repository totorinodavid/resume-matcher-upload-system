import { ImprovedResult } from '@/components/common/resume_previewer_context';

// New unified envelopes (backend wraps all responses as { request_id, data })
interface JobUploadEnvelope { request_id?: string; data?: { job_id: string[] | string } }
interface ImproveEnvelope { request_id?: string; data?: ImprovedResult }

// Route through the BFF proxy so NextAuth auth and backend base are handled consistently
const BFF_BASE = '/api/bff';
const timedFetch = async (url: string, init: RequestInit, ms: number) => {
    const controller = new AbortController();
    const t = setTimeout(() => controller.abort(), ms);
    try {
    // Ensure no caching proxies interfere and keep cookies for NextAuth
    return await fetch(url, { credentials: 'include', cache: 'no-store', ...init, signal: controller.signal });
    } finally {
        clearTimeout(t);
    }
};

/** Uploads job descriptions and returns a job_id */
export async function uploadJobDescriptions(
    descriptions: string[],
    resumeId: string
): Promise<string> {
    const res = await fetch(`${BFF_BASE}/api/v1/jobs/upload`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ job_descriptions: descriptions, resume_id: resumeId }),
        credentials: 'include',
    });
    if (!res.ok) throw new Error(`Upload failed with status ${res.status}`);
    const json: JobUploadEnvelope | (JobUploadEnvelope['data']) = await res.json();
    // unwrap envelope or fallback compat if server ever returns flat payload
    const payload = (json as JobUploadEnvelope)?.data ?? (json as JobUploadEnvelope['data']);
    const jobIdField = payload?.job_id as string | string[] | undefined;
    const idArray = Array.isArray(jobIdField) ? jobIdField : jobIdField ? [jobIdField] : [];
    if (!idArray[0]) throw new Error('No job_id returned from server');
    console.log('Job upload response:', json);
    return idArray[0];
}

/** Improves the resume and returns the full preview object */
export async function improveResume(
    resumeId: string,
    jobId: string,
    options?: { useLlm?: boolean; requireLlm?: boolean; preview?: boolean }
): Promise<ImprovedResult> {
    let response: Response;
    try {
    // Allow backend defaults; only pass explicit flags when set
    const params = new URLSearchParams();
    // Default to preview=false to reduce latency (LLM still required for Improve)
    params.set('preview', String(options?.preview ?? false));
    if (options?.useLlm === false) params.set('use_llm', 'false');
    if (typeof options?.requireLlm !== 'undefined') params.set('require_llm', String(!!options.requireLlm));
    const qp = params.toString() ? `?${params.toString()}` : '';
        response = await timedFetch(`${BFF_BASE}/api/v1/resumes/improve${qp}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' },
            body: JSON.stringify({ resume_id: resumeId, job_id: jobId }),
        }, 180000); // Allow up to 180s for LLM+embeddings
    } catch (networkError) {
        console.error('Network error during improveResume:', networkError);
        throw networkError;
    }

    const text = await response.text();
    if (!response.ok) {
        console.error('Improve failed response body:', text);
        throw new Error(`Improve failed with status ${response.status}: ${text}`);
    }

    let data: ImproveEnvelope | ImprovedResult;
    try {
        data = JSON.parse(text);
    } catch (parseError) {
        console.error('Failed to parse improveResume response:', parseError, 'Raw response:', text);
        throw parseError;
    }

    const payload: ImprovedResult = (data as ImproveEnvelope).data ?? (data as ImprovedResult);
    console.log('Resume improvement response:', payload);
    return payload;
}