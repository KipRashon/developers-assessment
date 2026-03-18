import type { FilterTab, RemittanceStatusFilter } from "@/features/payments/types/payments.types"

export const PAYMENTS_DEFAULT_START_DATE = "2024-01-01"
export const PAYMENTS_DEFAULT_END_DATE = "2026-12-31"
export const PAYMENTS_DEFAULT_CURRENCY = "USD"

export const PAYMENTS_EXCLUSION_REASON = "Excluded during payment batch review"

export const PAYMENTS_STATUS_OPTIONS: { label: string; value: RemittanceStatusFilter }[] = [
  { label: "All", value: "all" },
  { label: "Unremitted", value: "UNREMITTED" },
  { label: "Remitted", value: "REMITTED" },
]

export const PAYMENTS_FILTER_TABS: { value: FilterTab; label: string }[] = [
  { value: "date", label: "Date Range" },
  { value: "status", label: "Status" },
  { value: "freelancer", label: "Freelancer" },
]

export const PAYMENTS_QUERY_KEYS = {
  worklogs: "payments-worklogs",
  freelancerFilters: "payments-freelancer-filters",
  worklogDetail: "payments-worklog-detail",
  batchReview: "payments-batch-review",
  batchSummary: "payments-batch-summary",
} as const
