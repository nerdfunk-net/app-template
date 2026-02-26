export interface JobTemplate {
  id: number
  name: string
  job_type: string
  description?: string
  is_global: boolean
  user_id?: number
  created_by?: string
  created_at: string
  updated_at: string
}

export interface JobType {
  value: string
  label: string
  description: string
}

