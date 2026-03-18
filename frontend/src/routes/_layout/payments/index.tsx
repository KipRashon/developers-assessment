import { createFileRoute, useNavigate } from "@tanstack/react-router"

import { PaymentsFilters } from "@/features/payments/components/PaymentsFilters"
import { PaymentsSummaryPanel } from "@/features/payments/components/PaymentsSummaryPanel"
import { PaymentsWorklogsTable } from "@/features/payments/components/PaymentsWorklogsTable"
import { WorklogDetailSheet } from "@/features/payments/components/WorklogDetailSheet"
import { usePaymentsWorklogs } from "@/features/payments/hooks/usePaymentsWorklogs"

export const Route = createFileRoute("/_layout/payments/")({
  component: PaymentsWorklogsPage,
})

function PaymentsWorklogsPage() {
  const navigate = useNavigate()
  const payments = usePaymentsWorklogs({
    onReviewReady: (batchId) => {
      navigate({
        to: "/payments/review/$batchId",
        params: { batchId },
      })
    },
  })

  return (
    <div className="flex flex-col gap-6">
      <div className="rounded-2xl border bg-[linear-gradient(145deg,var(--color-card),color-mix(in_srgb,var(--color-primary)_7%,var(--color-card)))] p-4 md:p-5">
        <h1 className="text-xl font-semibold tracking-tight md:text-2xl">
          Payments Worklogs
        </h1>
      </div>

      <PaymentsFilters
        activeFilterTab={payments.activeFilterTab}
        setActiveFilterTab={payments.setActiveFilterTab}
        startDate={payments.startDate}
        endDate={payments.endDate}
        setStartDate={payments.setStartDate}
        setEndDate={payments.setEndDate}
        remittanceStatus={payments.remittanceStatus}
        setRemittanceStatus={payments.setRemittanceStatus}
        freelancerFilter={payments.freelancerFilter}
        setFreelancerFilter={payments.setFreelancerFilter}
        freelancers={payments.freelancers}
      />

      <div className="grid items-start gap-6 lg:grid-cols-[minmax(0,1fr)_320px]">
        <div className="order-1 lg:order-2 lg:min-w-0">
          <PaymentsSummaryPanel
            payableTotal={payments.payableTotal}
            selectedCount={payments.selectedWorklogIds.size}
            excludedWorklogCount={payments.excludedWorklogIds.size}
            excludedFreelancerCount={payments.excludedFreelancerIds.size}
            includedCount={payments.includedRows.length}
            excludedWorklogIds={payments.excludedWorklogIds}
            excludedFreelancerIds={payments.excludedFreelancerIds}
            getFreelancerName={payments.getFreelancerName}
            canReview={payments.includedRows.length > 0}
            isSubmitting={payments.reviewMutation.isPending}
            hasSubmitError={payments.reviewMutation.isError}
            onClearExclusions={payments.clearExclusions}
            onReviewSelection={() => payments.reviewMutation.mutate()}
          />
        </div>

        <div className="order-2 min-w-0 lg:order-1">
          <PaymentsWorklogsTable
            rows={payments.filteredRows}
            isLoading={payments.worklogsQuery.isLoading}
            isError={payments.worklogsQuery.isError}
            selectedWorklogIds={payments.selectedWorklogIds}
            excludedWorklogIds={payments.excludedWorklogIds}
            excludedFreelancerIds={payments.excludedFreelancerIds}
            onSelectWorklog={payments.toggleWorklogSelection}
            onToggleExcludedWorklog={payments.toggleExcludedWorklog}
            onToggleExcludedFreelancer={payments.toggleExcludedFreelancer}
            onOpenDetails={payments.setSelectedWorklogId}
          />
        </div>
      </div>

      <WorklogDetailSheet
        open={Boolean(payments.selectedWorklogId)}
        onOpenChange={(open) => {
          if (!open) {
            payments.setSelectedWorklogId(null)
          }
        }}
        isLoading={payments.detailQuery.isLoading}
        isError={payments.detailQuery.isError}
        data={payments.detailQuery.data}
      />
    </div>
  )
}
