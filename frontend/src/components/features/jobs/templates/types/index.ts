export interface JobTemplate {
  id: number
  name: string
  job_type: string
  description?: string
  inventory_source: "all" | "inventory"
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
  id: number
  name: string
  url: string
  branch: string
  category: string
}

export interface CommandTemplate {
  id: number
  name: string
  category: string
}

export interface CustomField {
  id: string
  name?: string
  key: string
  label: string
  type: {
    value: string
    label: string
  }
}
