export type DeviceSource = 'inventory' | 'checkmk' | 'both'
export type SystemFilter = 'all' | 'both' | 'inventory' | 'checkmk'

export interface DiffDevice {
  name: string
  source: DeviceSource
  inventory_id?: string
  ip_address?: string
  role?: string
  location?: string
  status?: string
  device_type?: string
  checkmk_folder?: string
  checkmk_alias?: string
  checkmk_ip?: string
  checkmk_diff_status?: string
}

export interface DiffTaskResult {
  all_devices: DiffDevice[]
  inventory_only: DiffDevice[]
  checkmk_only: DiffDevice[]
  total_inventory: number
  total_checkmk: number
  total_both: number
}
