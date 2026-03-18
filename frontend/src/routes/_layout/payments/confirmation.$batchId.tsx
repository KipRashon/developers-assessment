import { Link, createFileRoute } from "@tanstack/react-router"
import { BadgeCheck, CircleDollarSign, Loader2, ReceiptText } from "lucide-react"

import { usePaymentBatchSummary } from "@/features/payments/hooks/usePaymentBatchSummary"
import { formatMoney } from "@/features/payments/utils/payments.formatters"
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"
import { Badge } from "@/components/ui/badge"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

export const Route = createFileRoute("/_layout/payments/confirmation/$batchId")({
  component: PaymentsConfirmationPage,
})

function PaymentsConfirmationPage() {
  const { batchId } = Route.useParams()
  const summaryQuery = usePaymentBatchSummary(batchId)

  if (summaryQuery.isLoading) {
    return (
      <div className="flex items-center gap-2 py-8 text-muted-foreground">
        <Loader2 className="size-4 animate-spin" />
        Loading confirmation status...
      </div>
    )
  }

  if (summaryQuery.isError || !summaryQuery.data) {
    return (
      <Alert variant="destructive">
        <AlertTitle>Could not load confirmation status</AlertTitle>
        <AlertDescription>
          The batch may still be processing. Return to payments and try opening it
          again.
        </AlertDescription>
      </Alert>
    )
  }

  const summary = summaryQuery.data

  return (
    <div className="flex flex-col gap-6">
      <div className="rounded-2xl border bg-[linear-gradient(145deg,var(--color-card),color-mix(in_srgb,var(--color-primary)_7%,var(--color-card)))] p-6">
        <h1 className="text-2xl font-semibold tracking-tight">Confirmation</h1>
        <p className="mt-2 text-sm text-muted-foreground">
          Payment batch result and audit metadata.
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-base">
            <BadgeCheck className="size-4 text-primary" />
            Batch status
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4 text-sm">
          <div className="grid gap-3 sm:grid-cols-2">
            <div className="rounded-lg border p-3">
              <div className="text-muted-foreground">Batch id</div>
              <div className="font-mono text-xs">{summary.id}</div>
            </div>
            <div className="rounded-lg border p-3">
              <div className="text-muted-foreground">Status</div>
              <div>
                <Badge variant="secondary">{summary.status}</Badge>
              </div>
            </div>
          </div>

          <div className="grid gap-3 sm:grid-cols-3">
            <div className="rounded-lg border p-3">
              <div className="flex items-center gap-2 text-muted-foreground">
                <CircleDollarSign className="size-4" />
                Net total
              </div>
              <div className="font-semibold">
                {formatMoney(Number(summary.net_total || 0))}
              </div>
            </div>
            <div className="rounded-lg border p-3">
              <div className="text-muted-foreground">Included worklogs</div>
              <div className="font-semibold">{summary.included_count}</div>
            </div>
            <div className="rounded-lg border p-3">
              <div className="text-muted-foreground">Excluded worklogs</div>
              <div className="font-semibold">{summary.excluded_count}</div>
            </div>
          </div>

          <div className="rounded-lg border border-dashed p-3 text-xs text-muted-foreground">
            Confirmed at: {summary.confirmed_at || "Not confirmed"}
          </div>

          {summary.error_message ? (
            <Alert variant="destructive">
              <AlertTitle>Batch error</AlertTitle>
              <AlertDescription>{summary.error_message}</AlertDescription>
            </Alert>
          ) : null}

          <div className="flex flex-wrap gap-2">
            <Link
              to="/payments"
              className="inline-flex items-center gap-2 rounded-md border px-3 py-2 text-sm font-medium"
            >
              <ReceiptText className="size-4" />
              Back to worklogs
            </Link>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
