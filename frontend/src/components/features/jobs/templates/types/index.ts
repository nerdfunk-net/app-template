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

export interface GitRepository {
  id: string | number
  name: string
  url?: string
}

export interface CommandTemplate {
  id: string | number
  name: string
  description?: string
  commands?: string
}

export interface CustomField {
  id: string | number
  name: string
  key: string
  type?: { value: string; label: string }
}

