import { AlertCircle, CheckCircle2, CircleDollarSign, Loader2 } from "lucide-react"

import { formatMoney } from "@/features/payments/utils/payments.formatters"
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

type PaymentsSummaryPanelProps = {
  payableTotal: number
  selectedCount: number
  excludedWorklogCount: number
  excludedFreelancerCount: number
  includedCount: number
  excludedWorklogIds: Set<string>
  excludedFreelancerIds: Set<string>
  getFreelancerName: (freelancerId: string) => string
  canReview: boolean
  isSubmitting: boolean
  hasSubmitError: boolean
  onClearExclusions: () => void
  onReviewSelection: () => void
}

export function PaymentsSummaryPanel({
  payableTotal,
  selectedCount,
  excludedWorklogCount,
  excludedFreelancerCount,
  includedCount,
  excludedWorklogIds,
  excludedFreelancerIds,
  getFreelancerName,
  canReview,
  isSubmitting,
  hasSubmitError,
  onClearExclusions,
  onReviewSelection,
}: PaymentsSummaryPanelProps) {
  return (
    <Card className="h-fit lg:sticky lg:top-24">
      <CardHeader>
        <CardTitle className="text-base">Review summary</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="payments-kpi rounded-xl border p-4">
          <div className="text-sm text-muted-foreground">Payable total</div>
          <div className="mt-1 flex items-center gap-2 text-xl font-semibold">
            <CircleDollarSign className="size-5 text-primary" />
            {formatMoney(payableTotal)}
          </div>
        </div>

        <div className="grid gap-3 text-sm">
          <div className="flex items-center justify-between">
            <span>Selected worklogs</span>
            <span className="font-semibold">{selectedCount}</span>
          </div>
          <div className="flex items-center justify-between">
            <span>Excluded worklogs</span>
            <span className="font-semibold">{excludedWorklogCount}</span>
          </div>
          <div className="flex items-center justify-between">
            <span>Excluded freelancers</span>
            <span className="font-semibold">{excludedFreelancerCount}</span>
          </div>
          <div className="flex items-center justify-between">
            <span>Included in batch</span>
            <span className="font-semibold">{includedCount}</span>
          </div>
        </div>

        {excludedWorklogCount + excludedFreelancerCount > 0 ? (
          <div className="space-y-2 rounded-lg border border-dashed p-3 text-xs">
            <div className="font-medium">Active exclusions</div>
            <div className="flex flex-wrap gap-2">
              {Array.from(excludedWorklogIds).map((worklogId) => (
                <Badge key={worklogId} variant="secondary">
                  WL {worklogId}
                </Badge>
              ))}
              {Array.from(excludedFreelancerIds).map((freelancerId) => (
                <Badge key={freelancerId} variant="secondary">
                  {getFreelancerName(freelancerId)}
                </Badge>
              ))}
            </div>
          </div>
        ) : null}

        {hasSubmitError ? (
          <Alert variant="destructive">
            <AlertCircle className="size-4" />
            <AlertTitle>Batch setup failed</AlertTitle>
            <AlertDescription>
              Could not create review batch. Please retry.
            </AlertDescription>
          </Alert>
        ) : null}

        <div className="flex flex-col gap-2">
          <Button
            type="button"
            variant="outline"
            className="w-full"
            onClick={onClearExclusions}
          >
            Clear exclusions
          </Button>
          <Button
            type="button"
            className="w-full"
            onClick={onReviewSelection}
            disabled={!canReview || isSubmitting}
          >
            {isSubmitting ? (
              <Loader2 className="mr-1 size-4 animate-spin" />
            ) : (
              <CheckCircle2 className="mr-1 size-4" />
            )}
            Review selection
          </Button>
        </div>
      </CardContent>
    </Card>
  )
}
