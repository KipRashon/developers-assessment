import type {
  FreelancerOption,
  WorklogRow,
} from "@/features/payments/types/payments.types"

const UNKNOWN_FREELANCER_NAME = "Unknown freelancer"

function normalizeFreelancerName(name: string | null | undefined) {
  const normalized = name?.trim()
  if (!normalized) {
    return UNKNOWN_FREELANCER_NAME
  }
  return normalized
}

export function getFilteredWorklogs(rows: WorklogRow[], freelancerFilter: string) {
  if (freelancerFilter === "all") {
    return rows
  }
  return rows.filter((row) => row.freelancer_id === freelancerFilter)
}

export function getUniqueFreelancers(rows: WorklogRow[]): FreelancerOption[] {
  const byId = new Map<string, string>()
  rows.forEach((row) => {
    byId.set(row.freelancer_id, normalizeFreelancerName(row.freelancer_name))
  })

  return Array.from(byId.entries())
    .map(([id, name]) => ({ id, name }))
    .sort((a, b) =>
      normalizeFreelancerName(a.name).localeCompare(normalizeFreelancerName(b.name))
    )
}

export function getIncludedWorklogs(
  rows: WorklogRow[],
  selectedWorklogIds: Set<string>,
  excludedWorklogIds: Set<string>,
  excludedFreelancerIds: Set<string>,
) {
  return rows.filter((row) => {
    if (!selectedWorklogIds.has(row.id)) {
      return false
    }
    if (excludedWorklogIds.has(row.id)) {
      return false
    }
    if (excludedFreelancerIds.has(row.freelancer_id)) {
      return false
    }
    return true
  })
}

export function getPayableTotal(rows: WorklogRow[]) {
  return rows.reduce((acc, row) => acc + Number(row.earned_amount || 0), 0)
}

export function buildFinalExcludedWorklogIds(
  rows: WorklogRow[],
  selectedWorklogIds: Set<string>,
  excludedWorklogIds: Set<string>,
  excludedFreelancerIds: Set<string>,
) {
  const finalExcluded = new Set<string>()
  rows.forEach((row) => {
    if (!selectedWorklogIds.has(row.id)) {
      finalExcluded.add(row.id)
    }
    if (excludedWorklogIds.has(row.id)) {
      finalExcluded.add(row.id)
    }
    if (excludedFreelancerIds.has(row.freelancer_id)) {
      finalExcluded.add(row.id)
    }
  })
  return Array.from(finalExcluded)
}
