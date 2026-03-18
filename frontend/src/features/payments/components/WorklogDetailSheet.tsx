import { AlertCircle, Loader2 } from "lucide-react"

import type { WorklogDetail } from "@/features/payments/types/payments.types"
import {
  formatMoney,
  formatUsDate,
  formatUsDateTime,
} from "@/features/payments/utils/payments.formatters"
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"
import {
  Sheet,
  SheetContent,
  SheetDescription,
  SheetHeader,
  SheetTitle,
} from "@/components/ui/sheet"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"

type WorklogDetailSheetProps = {
  open: boolean
  onOpenChange: (open: boolean) => void
  isLoading: boolean
  isError: boolean
  data: WorklogDetail | undefined
}

export function WorklogDetailSheet({
  open,
  onOpenChange,
  isLoading,
  isError,
  data,
}: WorklogDetailSheetProps) {
  return (
    <Sheet open={open} onOpenChange={onOpenChange}>
      <SheetContent className="w-full sm:max-w-2xl">
        <SheetHeader>
          <SheetTitle>Worklog Details</SheetTitle>
          <SheetDescription>Time entries are shown in US date format.</SheetDescription>
        </SheetHeader>

        {isLoading ? (
          <div className="flex items-center gap-2 px-4 text-muted-foreground">
            <Loader2 className="size-4 animate-spin" />
            Loading details...
          </div>
        ) : null}

        {isError ? (
          <div className="px-4">
            <Alert variant="destructive">
              <AlertCircle className="size-4" />
              <AlertTitle>Could not load worklog details</AlertTitle>
              <AlertDescription>
                Please close this panel and try again.
              </AlertDescription>
            </Alert>
          </div>
        ) : null}

        {!isLoading && !isError && data ? (
          <div className="space-y-4 overflow-y-auto px-4 pb-6">
            <div className="rounded-lg border p-3 text-sm">
              <div className="font-medium">{data.task_name}</div>
              <div className="mt-1 text-xs text-muted-foreground">
                Freelancer: {data.freelancer_name || data.freelancer_id}
              </div>
              <div className="text-xs text-muted-foreground">
                Period: {formatUsDate(data.period_start)} to {formatUsDate(data.period_end)}
              </div>
            </div>

            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Started</TableHead>
                  <TableHead>Ended</TableHead>
                  <TableHead>Hours</TableHead>
                  <TableHead>Rate</TableHead>
                  <TableHead className="text-right">Line total</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {data.time_entries.map((entry) => (
                  <TableRow key={entry.id}>
                    <TableCell className="text-xs">{formatUsDateTime(entry.started_at)}</TableCell>
                    <TableCell className="text-xs">{formatUsDateTime(entry.ended_at)}</TableCell>
                    <TableCell>{entry.hours}</TableCell>
                    <TableCell>{formatMoney(Number(entry.hourly_rate || 0))}</TableCell>
                    <TableCell className="text-right">
                      {formatMoney(Number(entry.hours || 0) * Number(entry.hourly_rate || 0))}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
        ) : null}
      </SheetContent>
    </Sheet>
  )
}
