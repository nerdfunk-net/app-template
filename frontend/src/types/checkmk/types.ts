/**
 * Shared type definitions for CheckMK integration
 * Centralized location for all CheckMK-related interfaces
 */

/**
 * CheckMK host representation
 * Used across components, hooks, and utilities
 */
export interface CheckMKHost {
  host_name: string
  folder: string
  attributes: Record<string, unknown>
  effective_attributes?: Record<string, unknown> | null
  labels?: Record<string, string>
}

/**
 * Filter options for host inventory
 * Used to filter hosts by folders and labels
 */
export interface FilterOptions {
  folders: Set<string>
  labels: Set<string>
}

/**
 * Status message for user feedback
 * Used in modals and components to show operation results
 */
export interface StatusMessage {
  type: 'success' | 'error' | 'info'
  text: string
}

/**
 * CheckMK configuration for attribute/tag mappings
 * Maps CheckMK attributes and tags to Device fields
 */
export interface CheckMKConfig {
  attr2htg?: Record<string, string>
  cf2htg?: Record<string, string>
  tags2htg?: Record<string, string>
}

/**
 * Device metadata for device properties
 * Contains reference data from local DB
 */
export interface DeviceMetadata {
  locations: Array<{ id: string; name: string }>
  roles: Array<{ id: string; name: string }>
  statuses: Array<{ id: string; name: string }>
  deviceTypes: Array<{ id: string; name: string }>
  platforms: Array<{ id: string; name: string }>
  customFields: Array<{ id: string; name: string; key: string }>
}

/**
 * Property mapping for CheckMK to Device field conversion
 * Represents a single field mapping with metadata
 */
export interface PropertyMapping {
  deviceField: string
  value: unknown
  isCore?: boolean
}
