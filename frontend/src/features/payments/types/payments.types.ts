export type FilterTab = "date" | "status" | "freelancer"

export type RemittanceStatusFilter = "all" | "UNREMITTED" | "REMITTED"

export type WorklogRow = {
  id: string
  task_name: string
  freelancer_id: string
  freelancer_name?: string | null
  period_start: string
  period_end: string
  remittance_status: string
  earned_amount: number
}

export type FreelancerOption = {
  id: string
  name: string
}

export type FreelancersResponse = {
  data: FreelancerOption[]
  count: number
}

export type WorklogsResponse = {
  data: WorklogRow[]
  count: number
}

export type WorklogTimeEntry = {
  id: string
  started_at: string
  ended_at: string
  hours: number
  hourly_rate: number
  is_excluded: boolean
}

export type WorklogDetail = {
  id: string
  task_name: string
  freelancer_id: string
  freelancer_name?: string | null
  period_start: string
  period_end: string
  remittance_status: string
  earned_amount: number
  time_entries: WorklogTimeEntry[]
}

export type PaymentBatchSummary = {
  id: string
  period_start: string
  period_end: string
  status: string
  currency: string
  included_count: number
  excluded_count: number
  gross_total: number
  net_total: number
  created_at: string
  updated_at: string
  confirmed_at: string | null
  error_message: string | null
}

export type PaymentBatchLine = {
  id: string
  worklog_id: string
  freelancer_id: string
  freelancer_name?: string | null
  inclusion_status: string
  exclusion_reason: string | null
  amount_snapshot: number
  total_minutes_snapshot: number
  remittance_id?: string | null
}

export type PaymentBatchReviewResponse = {
  batch: PaymentBatchSummary
  included_worklogs: PaymentBatchLine[]
  excluded_worklogs: PaymentBatchLine[]
}

export type PaymentBatchConfirmResponse = {
  batch: PaymentBatchSummary
  remittance_ids: string[]
}

export type PaymentBatchCreatePayload = {
  period_start: string
  period_end: string
  currency: string
}

export type PaymentBatchExclusionsPayload = {
  excluded_worklog_ids: string[]
  excluded_freelancer_ids: string[]
  reason: string
}
