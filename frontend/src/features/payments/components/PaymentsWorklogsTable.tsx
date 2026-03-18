import { AlertCircle, Ban, EllipsisVertical, UserMinus } from "lucide-react"

import type { WorklogRow } from "@/features/payments/types/payments.types"
import {
  formatMoney,
  formatRemittanceStatus,
  formatUsDate,
} from "@/features/payments/utils/payments.formatters"
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Checkbox } from "@/components/ui/checkbox"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"

type PaymentsWorklogsTableProps = {
  rows: WorklogRow[]
  isLoading: boolean
  isError: boolean
  selectedWorklogIds: Set<string>
  excludedWorklogIds: Set<string>
  excludedFreelancerIds: Set<string>
  onSelectWorklog: (worklogId: string) => void
  onToggleExcludedWorklog: (worklogId: string) => void
  onToggleExcludedFreelancer: (freelancerId: string) => void
  onOpenDetails: (worklogId: string) => void
}

export function PaymentsWorklogsTable({
  rows,
  isLoading,
  isError,
  selectedWorklogIds,
  excludedWorklogIds,
  excludedFreelancerIds,
  onSelectWorklog,
  onToggleExcludedWorklog,
  onToggleExcludedFreelancer,
  onOpenDetails,
}: PaymentsWorklogsTableProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-base">Eligible worklogs</CardTitle>
      </CardHeader>
      <CardContent>
        {isLoading ? (
          <div className="flex items-center gap-2 py-10 text-muted-foreground">
            Loading worklogs...
          </div>
        ) : null}

        {isError ? (
          <Alert variant="destructive">
            <AlertCircle className="size-4" />
            <AlertTitle>Could not load worklogs</AlertTitle>
            <AlertDescription>
              Failed to fetch worklogs for this date range. Please try again.
            </AlertDescription>
          </Alert>
        ) : null}

        {!isLoading && !isError && rows.length === 0 ? (
          <div className="rounded-lg border border-dashed p-10 text-center text-sm text-muted-foreground">
            No worklogs match the current filter set.
          </div>
        ) : null}

        {!isLoading && !isError && rows.length > 0 ? (
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead className="w-[90px]">Select</TableHead>
                <TableHead>Task</TableHead>
                <TableHead>Freelancer</TableHead>
                <TableHead>Status</TableHead>
                <TableHead className="text-right">Earned</TableHead>
                <TableHead className="w-[84px] text-right">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {rows.map((row) => {
                const isExcluded =
                  excludedWorklogIds.has(row.id) ||
                  excludedFreelancerIds.has(row.freelancer_id)

                return (
                  <TableRow key={row.id}>
                    <TableCell>
                      <div className="inline-flex rounded-md border border-transparent p-1 transition-colors hover:border-border hover:bg-muted/30">
                        <Checkbox
                          aria-label={`Select worklog ${row.task_name}`}
                          checked={selectedWorklogIds.has(row.id)}
                          onCheckedChange={() => onSelectWorklog(row.id)}
                        />
                      </div>
                    </TableCell>
                    <TableCell className="min-w-[210px] whitespace-normal">
                      <div className="font-medium">{row.task_name}</div>
                      <div className="text-xs text-muted-foreground">
                        {formatUsDate(row.period_start)} to {formatUsDate(row.period_end)}
                      </div>
                    </TableCell>
                    <TableCell className="whitespace-normal">
                      {row.freelancer_name || row.freelancer_id}
                    </TableCell>
                    <TableCell>
                      <Badge variant={isExcluded ? "secondary" : "outline"}>
                        {isExcluded ? "Excluded" : formatRemittanceStatus(row.remittance_status)}
                      </Badge>
                    </TableCell>
                    <TableCell className="text-right font-medium">
                      {formatMoney(Number(row.earned_amount || 0))}
                    </TableCell>
                    <TableCell>
                      <div className="flex justify-end">
                        <DropdownMenu>
                          <DropdownMenuTrigger asChild>
                            <Button
                              type="button"
                              size="icon-sm"
                              variant="ghost"
                              aria-label={`Open actions for ${row.task_name}`}
                            >
                              <EllipsisVertical className="size-4" />
                            </Button>
                          </DropdownMenuTrigger>
                          <DropdownMenuContent align="end">
                            <DropdownMenuItem onClick={() => onOpenDetails(row.id)}>
                              Details
                            </DropdownMenuItem>
                            <DropdownMenuItem onClick={() => onToggleExcludedWorklog(row.id)}>
                              <Ban className="size-4" />
                              {excludedWorklogIds.has(row.id)
                                ? "Undo worklog exclusion"
                                : "Exclude worklog"}
                            </DropdownMenuItem>
                            <DropdownMenuItem
                              onClick={() => onToggleExcludedFreelancer(row.freelancer_id)}
                            >
                              <UserMinus className="size-4" />
                              {excludedFreelancerIds.has(row.freelancer_id)
                                ? "Undo freelancer exclusion"
                                : "Exclude freelancer"}
                            </DropdownMenuItem>
                          </DropdownMenuContent>
                        </DropdownMenu>
                      </div>
                    </TableCell>
                  </TableRow>
                )
              })}
            </TableBody>
          </Table>
        ) : null}
      </CardContent>
    </Card>
  )
}
