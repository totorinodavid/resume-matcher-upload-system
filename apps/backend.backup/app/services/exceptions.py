from typing import Optional


class ResumeMatcherException(Exception):
    """Base exception for Resume Matcher operations."""
    pass


class ResumeNotFoundError(ResumeMatcherException):
    """
    Exception raised when a resume is not found in the database.
    """

    def __init__(self, resume_id: Optional[str] = None, message: Optional[str] = None):
        if resume_id and not message:
            message = f"Resume with ID {resume_id} not found."
        elif not message:
            message = "Resume not found."
        super().__init__(message)
        self.resume_id = resume_id


class JobNotFoundError(ResumeMatcherException):
    """
    Exception raised when a job is not found in the database.
    """

    def __init__(self, job_id: Optional[str] = None, message: Optional[str] = None):
        if job_id and not message:
            message = f"Job with ID {job_id} not found."
        elif not message:
            message = "Job not found."
        super().__init__(message)
        self.job_id = job_id


class ResumeValidationError(ResumeMatcherException):
    """
    Exception raised when structured resume validation fails.
    """

    def __init__(
        self,
        resume_id: Optional[str] = None,
        validation_error: Optional[str] = None,
        message: Optional[str] = None,
    ):
        if message:
            # we can use custom message if provided
            pass
        elif validation_error:
            message = f"Resume parsing failed: {validation_error}. Please ensure your resume contains all required information with proper formatting."
        elif resume_id:
            message = f"Resume with ID {resume_id} failed validation during structured parsing."
        else:
            message = "Resume validation failed during structured parsing."
        super().__init__(message)
        self.resume_id = resume_id
        self.validation_error = validation_error


class ResumeParsingError(ResumeMatcherException):
    """
    Exception raised when a resume processing and storing in the database failed.
    """

    def __init__(self, resume_id: Optional[str] = None, message: Optional[str] = None):
        if resume_id and not message:
            message = f"Parsing of resume with ID {resume_id} failed."
        elif not message:
            message = "Parsed resume not found."
        super().__init__(message)
        self.resume_id = resume_id


class JobParsingError(ResumeMatcherException):
    """
    Exception raised when a resume processing and storing in the database failed.
    """

    def __init__(self, job_id: Optional[str] = None, message: Optional[str] = None):
        if job_id and not message:
            message = f"Parsing of job with ID {job_id} failed."
        elif not message:
            message = "Parsed job not found."
        super().__init__(message)
        self.job_id = job_id


class ResumeKeywordExtractionError(ResumeMatcherException):
    """
    Exception raised when keyword extraction from resume failed or no keywords were extracted.
    """

    def __init__(self, resume_id: Optional[str] = None, message: Optional[str] = None):
        if resume_id and not message:
            message = f"Keyword extraction failed for resume with ID {resume_id}. Cannot proceed with resume improvement without extracted keywords."
        elif not message:
            message = "Resume keyword extraction failed. Cannot improve resume without keywords."
        super().__init__(message)
        self.resume_id = resume_id


class JobKeywordExtractionError(ResumeMatcherException):
    """
    Exception raised when keyword extraction from job failed or no keywords were extracted.
    """

    def __init__(self, job_id: Optional[str] = None, message: Optional[str] = None):
        if job_id and not message:
            message = f"Keyword extraction failed for job with ID {job_id}. Cannot proceed with resume improvement without job keywords."
        elif not message:
            message = "Job keyword extraction failed. Cannot improve resume without job requirements."
        super().__init__(message)
        self.job_id = job_id


class AIProcessingError(ResumeMatcherException):
    """
    Raised when LLM/Embedding processing is required but the provider is unavailable
    or returns an error.
    """

    def __init__(self, message: Optional[str] = None):
        super().__init__(message or "AI provider unavailable or failed to process the request.")


# Payment-specific exceptions
class PaymentProcessingError(ResumeMatcherException):
    """Raised when payment processing fails."""
    pass


class UserNotFoundError(ResumeMatcherException):
    """Raised when user is not found during payment processing."""
    pass


class WebhookValidationError(ResumeMatcherException):
    """Raised when webhook signature validation fails."""
    pass
