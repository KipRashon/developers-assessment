import { useMutation, useQuery } from "@tanstack/react-query"
import { useEffect, useMemo, useState } from "react"

import {
  PAYMENTS_DEFAULT_CURRENCY,
  PAYMENTS_DEFAULT_END_DATE,
  PAYMENTS_DEFAULT_START_DATE,
  PAYMENTS_EXCLUSION_REASON,
  PAYMENTS_QUERY_KEYS,
} from "@/features/payments/constants/payments.constants"
import {
  createPaymentBatch,
  getWorklogFreelancers,
  getWorklogDetail,
  getWorklogs,
  updatePaymentBatchExclusions,
} from "@/features/payments/api/payments.api"
import type {
  FilterTab,
  RemittanceStatusFilter,
} from "@/features/payments/types/payments.types"
import {
  buildFinalExcludedWorklogIds,
  getIncludedWorklogs,
  getPayableTotal,
} from "@/features/payments/utils/payments.selectors"

type UsePaymentsWorklogsArgs = {
  onReviewReady: (batchId: string) => void
}

export function usePaymentsWorklogs({ onReviewReady }: UsePaymentsWorklogsArgs) {
  const [startDate, setStartDate] = useState(PAYMENTS_DEFAULT_START_DATE)
  const [endDate, setEndDate] = useState(PAYMENTS_DEFAULT_END_DATE)
  const [remittanceStatus, setRemittanceStatus] =
    useState<RemittanceStatusFilter>("UNREMITTED")
  const [freelancerFilter, setFreelancerFilter] = useState("all")
  const [activeFilterTab, setActiveFilterTab] = useState<FilterTab>("date")

  const [selectedWorklogIds, setSelectedWorklogIds] = useState<Set<string>>(
    () => new Set(),
  )
  const [excludedWorklogIds, setExcludedWorklogIds] = useState<Set<string>>(
    () => new Set(),
  )
  const [excludedFreelancerIds, setExcludedFreelancerIds] = useState<Set<string>>(
    () => new Set(),
  )
  const [selectedWorklogId, setSelectedWorklogId] = useState<string | null>(null)

  const worklogsQuery = useQuery({
    queryKey: [
      PAYMENTS_QUERY_KEYS.worklogs,
      startDate,
      endDate,
      remittanceStatus,
      freelancerFilter,
    ],
    queryFn: () =>
      getWorklogs(
        startDate,
        endDate,
        remittanceStatus,
        freelancerFilter === "all" ? undefined : freelancerFilter,
      ),
  })

  const freelancersQuery = useQuery({
    queryKey: [
      PAYMENTS_QUERY_KEYS.freelancerFilters,
      startDate,
      endDate,
      remittanceStatus,
    ],
    queryFn: () => getWorklogFreelancers(startDate, endDate, remittanceStatus),
  })

  const detailQuery = useQuery({
    queryKey: [PAYMENTS_QUERY_KEYS.worklogDetail, selectedWorklogId],
    enabled: Boolean(selectedWorklogId),
    queryFn: () => getWorklogDetail(selectedWorklogId || ""),
  })

  const allRows = worklogsQuery.data?.data || []

  const filteredRows = allRows

  const freelancers = freelancersQuery.data?.data || []

  useEffect(() => {
    if (freelancerFilter === "all") {
      return
    }
    if (freelancers.some((freelancer) => freelancer.id === freelancerFilter)) {
      return
    }
    setFreelancerFilter("all")
  }, [freelancerFilter, freelancers])

  const freelancerNames = useMemo(() => {
    const names = new Map<string, string>()
    freelancers.forEach((freelancer) => {
      names.set(freelancer.id, freelancer.name || "Unknown freelancer")
    })
    allRows.forEach((row) => {
      names.set(
        row.freelancer_id,
        row.freelancer_name?.trim() || names.get(row.freelancer_id) || "Unknown freelancer",
      )
    })
    return names
  }, [allRows, freelancers])

  const getFreelancerName = (freelancerId: string) =>
    freelancerNames.get(freelancerId) || "Unknown freelancer"

  const includedRows = useMemo(
    () =>
      getIncludedWorklogs(
        allRows,
        selectedWorklogIds,
        excludedWorklogIds,
        excludedFreelancerIds,
      ),
    [allRows, selectedWorklogIds, excludedWorklogIds, excludedFreelancerIds],
  )

  const payableTotal = useMemo(() => getPayableTotal(includedRows), [includedRows])

  const reviewMutation = useMutation({
    mutationFn: async () => {
      const createdBatch = await createPaymentBatch({
        period_start: startDate,
        period_end: endDate,
        currency: PAYMENTS_DEFAULT_CURRENCY,
      })

      const excludedIds = buildFinalExcludedWorklogIds(
        allRows,
        selectedWorklogIds,
        excludedWorklogIds,
        excludedFreelancerIds,
      )

      await updatePaymentBatchExclusions(createdBatch.id, {
        excluded_worklog_ids: excludedIds,
        excluded_freelancer_ids: Array.from(excludedFreelancerIds),
        reason: PAYMENTS_EXCLUSION_REASON,
      })

      return createdBatch.id
    },
    onSuccess: (batchId) => {
      onReviewReady(batchId)
    },
  })

  const toggleWorklogSelection = (worklogId: string) => {
    setSelectedWorklogIds((current) => {
      const next = new Set(current)
      if (next.has(worklogId)) {
        next.delete(worklogId)
      } else {
        next.add(worklogId)
      }
      return next
    })
  }

  const toggleExcludedWorklog = (worklogId: string) => {
    setExcludedWorklogIds((current) => {
      const next = new Set(current)
      if (next.has(worklogId)) {
        next.delete(worklogId)
      } else {
        next.add(worklogId)
      }
      return next
    })
  }

  const toggleExcludedFreelancer = (freelancerId: string) => {
    setExcludedFreelancerIds((current) => {
      const next = new Set(current)
      if (next.has(freelancerId)) {
        next.delete(freelancerId)
      } else {
        next.add(freelancerId)
      }
      return next
    })
  }

  const clearExclusions = () => {
    setExcludedWorklogIds(new Set())
    setExcludedFreelancerIds(new Set())
  }

  return {
    startDate,
    endDate,
    remittanceStatus,
    freelancerFilter,
    activeFilterTab,
    selectedWorklogIds,
    excludedWorklogIds,
    excludedFreelancerIds,
    selectedWorklogId,
    allRows,
    filteredRows,
    freelancers,
    includedRows,
    getFreelancerName,
    payableTotal,
    worklogsQuery,
    freelancersQuery,
    detailQuery,
    reviewMutation,
    setStartDate,
    setEndDate,
    setRemittanceStatus,
    setFreelancerFilter,
    setActiveFilterTab,
    setSelectedWorklogId,
    toggleWorklogSelection,
    toggleExcludedWorklog,
    toggleExcludedFreelancer,
    clearExclusions,
  }
}
