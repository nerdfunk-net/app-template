import type { JobTemplate, JobType, GitRepository, CommandTemplate, CustomField } from '../types'

// React best practice: Extract default objects to prevent re-render loops
export const EMPTY_TEMPLATES: JobTemplate[] = []
export const EMPTY_TYPES: JobType[] = []
export const EMPTY_REPOS: GitRepository[] = []
// EMPTY_INVENTORIES removed - inventory feature no longer exists
export const EMPTY_CMD_TEMPLATES: CommandTemplate[] = []
export const EMPTY_CUSTOM_FIELDS: CustomField[] = []

export const JOB_TYPE_LABELS: Record<string, string> = {
  example: 'Example',
} as const

export const JOB_TYPE_COLORS: Record<string, string> = {
  example: 'bg-slate-500',
} as const

export const DEFAULT_TEMPLATE: Partial<JobTemplate> = {
  inventory_source: 'all',
  is_global: false,
} as const

export const STALE_TIME = {
  TEMPLATES: 30 * 1000,          // 30 seconds - moderately dynamic
  JOB_TYPES: 5 * 60 * 1000,      // 5 minutes - rarely changes
  CONFIG_REPOS: 2 * 60 * 1000,   // 2 minutes - occasionally changes
  INVENTORIES: 30 * 1000,        // 30 seconds - moderately dynamic
  CMD_TEMPLATES: 2 * 60 * 1000,  // 2 minutes - occasionally changes
  CUSTOM_FIELDS: 5 * 60 * 1000,  // 5 minutes - rarely changes
} as const
