export interface ApiErrorShape {
  error: string; // machine-readable code
  message?: string; // optional human-readable
  details?: any; // optional extra context (non-sensitive)
}

export function err(code: string, message?: string, details?: any): ApiErrorShape {
  const obj: ApiErrorShape = { error: code }
  if (message) obj.message = message
  if (details !== undefined) obj.details = details
  return obj
}