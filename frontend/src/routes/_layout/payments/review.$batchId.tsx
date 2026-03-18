import { createFileRoute, useNavigate } from "@tanstack/react-router"
import { AlertTriangle, CheckCircle2, ClipboardList, Loader2 } from "lucide-react"
import { useState } from "react"

import { ConfirmBatchDialog } from "@/features/payments/components/ConfirmBatchDialog"
import { usePaymentBatchReview } from "@/features/payments/hooks/usePaymentBatchReview"
import { formatMoney, formatUsDate } from "@/features/payments/utils/payments.formatters"
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

export const Route = createFileRoute("/_layout/payments/review/$batchId")({
  component: PaymentsReviewPage,
})

function PaymentsReviewPage() {
  const navigate = useNavigate()
  const { batchId } = Route.useParams()
  const [isConfirmOpen, setIsConfirmOpen] = useState(false)

  const { reviewQuery, confirmMutation } = usePaymentBatchReview({
    batchId,
    onConfirmed: (confirmedBatchId) => {
      navigate({
        to: "/payments/confirmation/$batchId",
        params: { batchId: confirmedBatchId },
      })
    },
  })

  if (reviewQuery.isLoading) {
    return (
      <div className="flex items-center gap-2 py-8 text-muted-foreground">
        <Loader2 className="size-4 animate-spin" />
        Loading payment review...
      </div>
    )
  }

  if (reviewQuery.isError || !reviewQuery.data) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Could not load batch review</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground">
            Please return to payments and create a new review batch.
          </p>
          <Button className="mt-4" onClick={() => navigate({ to: "/payments" })}>
            Back to worklogs
          </Button>
        </CardContent>
      </Card>
    )
  }

  const batch = reviewQuery.data.batch

  return (
    <div className="flex flex-col gap-6">
      <div className="rounded-2xl border bg-[linear-gradient(145deg,var(--color-card),color-mix(in_srgb,var(--color-primary)_7%,var(--color-card)))] p-6">
        <h1 className="text-2xl font-semibold tracking-tight">Batch Review</h1>
        <p className="mt-2 text-sm text-muted-foreground">
          Validate included and excluded records before confirming payment.
        </p>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-base">
              <ClipboardList className="size-4" />
              Included worklogs
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            {reviewQuery.data.included_worklogs.length === 0 ? (
              <p className="text-sm text-muted-foreground">No included worklogs.</p>
            ) : (
              reviewQuery.data.included_worklogs.map((line) => (
                <div key={line.id} className="rounded-lg border p-3">
                  <div className="font-mono text-xs">Worklog: {line.worklog_id}</div>
                  <div className="mt-1 text-xs text-muted-foreground">
                    Freelancer: {line.freelancer_name || line.freelancer_id}
                  </div>
                  <div className="mt-1 text-sm font-semibold">
                    {formatMoney(Number(line.amount_snapshot || 0))}
                  </div>
                </div>
              ))
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-base">
              <AlertTriangle className="size-4" />
              Exclusions and totals
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="rounded-xl border bg-muted/20 p-4">
              <div className="text-sm text-muted-foreground">Net payable</div>
              <div className="text-2xl font-semibold">
                {formatMoney(Number(batch.net_total || 0))}
              </div>
            </div>

            <div className="space-y-2 text-sm">
              <div className="flex items-center justify-between">
                <span>Included worklogs</span>
                <span className="font-semibold">{batch.included_count}</span>
              </div>
              <div className="flex items-center justify-between">
                <span>Excluded worklogs</span>
                <span className="font-semibold">{batch.excluded_count}</span>
              </div>
              <div className="flex items-center justify-between">
                <span>Batch period</span>
                <span className="font-semibold">
                  {formatUsDate(batch.period_start)} to {formatUsDate(batch.period_end)}
                </span>
              </div>
            </div>

            {reviewQuery.data.excluded_worklogs.length === 0 ? (
              <div className="rounded-lg border border-dashed p-3 text-sm text-muted-foreground">
                No exclusions in this batch.
              </div>
            ) : (
              <div className="space-y-2">
                {reviewQuery.data.excluded_worklogs.map((line) => (
                  <div key={line.id} className="rounded-lg border p-3">
                    <div className="flex items-center justify-between gap-2">
                      <div className="text-xs text-muted-foreground">
                        Worklog: {line.worklog_id}
                      </div>
                      <Badge variant="secondary">{line.inclusion_status}</Badge>
                    </div>
                    <div className="mt-1 text-sm">
                      Freelancer: {line.freelancer_name || line.freelancer_id}
                    </div>
                    <div className="mt-1 text-xs text-muted-foreground">
                      Reason: {line.exclusion_reason || "Excluded during review"}
                    </div>
                  </div>
                ))}
              </div>
            )}

            {confirmMutation.isError ? (
              <Alert variant="destructive">
                <AlertTriangle className="size-4" />
                <AlertTitle>Confirmation failed</AlertTitle>
                <AlertDescription>
                  The payment batch could not be confirmed. Please retry.
                </AlertDescription>
              </Alert>
            ) : null}

            <div className="flex gap-2">
              <Button variant="outline" onClick={() => navigate({ to: "/payments" })}>
                Back
              </Button>
              <Button onClick={() => setIsConfirmOpen(true)}>
                <CheckCircle2 className="mr-1 size-4" />
                Confirm payment batch
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>

      <ConfirmBatchDialog
        open={isConfirmOpen}
        onOpenChange={setIsConfirmOpen}
        isConfirming={confirmMutation.isPending}
        onConfirm={() => confirmMutation.mutate()}
      />
    </div>
  )
}
