/**
 * Job Result Types
 *
 * This file contains TypeScript interfaces for job results in the Jobs feature.
 */

// Base job run interface
export interface JobRun {
  id: number
  job_schedule_id: number | null
  job_template_id: number | null
  celery_task_id: string | null
  job_name: string
  job_type: string
  status: string
  triggered_by: string
  queued_at: string
  started_at: string | null
  completed_at: string | null
  duration_seconds: number | null
  error_message: string | null
  result: Record<string, unknown> | null
  target_devices: string[] | null
  executed_by: string | null
  schedule_name: string | null
  template_name: string | null
}

export interface PaginatedResponse {
  items: JobRun[]
  total: number
  page: number
  page_size: number
  total_pages: number
}

// ============================================================================
// Generic Job Result (fallback for all job types)
// ============================================================================

export interface GenericJobResult {
  success: boolean
  message?: string
  error?: string
  // Index signature for compatibility with Record<string, unknown>
  [key: string]: unknown
}

// ============================================================================
// Utility Functions
// ============================================================================

/**
 * Format bytes to human readable string (e.g., "1.5 KB")
 */
export function formatBytes(bytes: number): string {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i]
}
