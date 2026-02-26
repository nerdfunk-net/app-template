import { useQuery } from '@tanstack/react-query'
import { useApi } from '@/hooks/use-api'
import { queryKeys } from '@/lib/query-keys'
import type { JobRun, JobProgressResponse } from '../types'
import { STALE_TIME, PROGRESS_POLL_INTERVAL } from '../utils/constants'
import { isJobActive } from '../utils/job-utils'

interface UseJobProgressQueryOptions {
  enabled?: boolean
}

const DEFAULT_OPTIONS: UseJobProgressQueryOptions = { enabled: true }

/**
 * Fetch progress for a specific job
 * Only enabled for actively running jobs.
 * Auto-stops polling when job completes.
 */
export function useJobProgressQuery(
  job: JobRun | null,
  options: UseJobProgressQueryOptions = DEFAULT_OPTIONS
) {
  const { apiCall } = useApi()
  const { enabled = true } = options

  const shouldPoll = !!(job && enabled && isJobActive(job.status))

  return useQuery({
    queryKey: queryKeys.jobs.progress(job?.id ?? 0),
    queryFn: async () => {
      if (!job) throw new Error('No job provided')

      const response = await apiCall<JobProgressResponse>(
        `job-runs/${job.id}/progress`,
        { method: 'GET' }
      )
      return response
    },
    enabled: shouldPoll,
    staleTime: STALE_TIME.PROGRESS,
    refetchInterval: shouldPoll ? PROGRESS_POLL_INTERVAL : false,
  })
}

/**
 * Hook for fetching progress of ALL running jobs at once
 */
export function useAllJobsProgress(jobs: JobRun[]) {
  const { apiCall } = useApi()

  const runningJobs = jobs.filter(job => isJobActive(job.status))
  const hasRunningJobs = runningJobs.length > 0

  return useQuery({
    queryKey: [...queryKeys.jobs.all, 'all-progress', runningJobs.map(j => j.id)],
    queryFn: async () => {
      const progressPromises = runningJobs.map(async (job) => {
        try {
          const response = await apiCall<JobProgressResponse>(
            `job-runs/${job.id}/progress`,
            { method: 'GET' }
          )
          return { jobId: job.id, progress: response }
        } catch {
          return { jobId: job.id, progress: null }
        }
      })

      const results = await Promise.all(progressPromises)

      const progressMap: Record<number, JobProgressResponse> = {}
      results.forEach(({ jobId, progress }) => {
        if (progress) {
          progressMap[jobId] = progress
        }
      })

      return progressMap
    },
    enabled: hasRunningJobs,
    staleTime: STALE_TIME.PROGRESS,
    refetchInterval: hasRunningJobs ? PROGRESS_POLL_INTERVAL : false,
  })
}
