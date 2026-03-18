import { CalendarRange } from "lucide-react"
import flatpickr from "flatpickr"
import "flatpickr/dist/flatpickr.min.css"
import type { Instance as FlatpickrInstance } from "flatpickr/dist/types/instance"
import type { ChangeEvent } from "react"
import { useEffect, useMemo, useRef, useState } from "react"

import {
  PAYMENTS_STATUS_OPTIONS,
} from "@/features/payments/constants/payments.constants"
import type {
  FilterTab,
  FreelancerOption,
  RemittanceStatusFilter,
} from "@/features/payments/types/payments.types"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs"

type PaymentsFiltersProps = {
  activeFilterTab: FilterTab
  setActiveFilterTab: (value: FilterTab) => void
  startDate: string
  endDate: string
  setStartDate: (value: string) => void
  setEndDate: (value: string) => void
  remittanceStatus: RemittanceStatusFilter
  setRemittanceStatus: (value: RemittanceStatusFilter) => void
  freelancerFilter: string
  setFreelancerFilter: (value: string) => void
  freelancers: FreelancerOption[]
}

export function PaymentsFilters({
  activeFilterTab,
  setActiveFilterTab,
  startDate,
  endDate,
  setStartDate,
  setEndDate,
  remittanceStatus,
  setRemittanceStatus,
  freelancerFilter,
  setFreelancerFilter,
  freelancers,
}: PaymentsFiltersProps) {
  const getFreelancerLabel = (name: string | null | undefined) => {
    const normalized = name?.trim()
    if (!normalized) {
      return "Unknown freelancer"
    }
    return normalized
  }

  const [freelancerSearch, setFreelancerSearch] = useState("")
  const startDateInputRef = useRef<HTMLInputElement | null>(null)
  const endDateInputRef = useRef<HTMLInputElement | null>(null)
  const startDatePickerRef = useRef<FlatpickrInstance | null>(null)
  const endDatePickerRef = useRef<FlatpickrInstance | null>(null)

  useEffect(() => {
    if (startDateInputRef.current) {
      startDatePickerRef.current = flatpickr(startDateInputRef.current, {
        dateFormat: "Y-m-d",
        clickOpens: true,
        allowInput: true,
        defaultDate: startDate,
        maxDate: endDate || undefined,
        onChange: (_, dateStr) => setStartDate(dateStr),
      })
    }

    if (endDateInputRef.current) {
      endDatePickerRef.current = flatpickr(endDateInputRef.current, {
        dateFormat: "Y-m-d",
        clickOpens: true,
        allowInput: true,
        defaultDate: endDate,
        minDate: startDate || undefined,
        onChange: (_, dateStr) => setEndDate(dateStr),
      })
    }

    return () => {
      startDatePickerRef.current?.destroy()
      endDatePickerRef.current?.destroy()
    }
  }, [setEndDate, setStartDate])

  useEffect(() => {
    startDatePickerRef.current?.setDate(startDate, false)
    endDatePickerRef.current?.set("minDate", startDate || undefined)
  }, [startDate])

  useEffect(() => {
    endDatePickerRef.current?.setDate(endDate, false)
    startDatePickerRef.current?.set("maxDate", endDate || undefined)
  }, [endDate])

  const visibleFreelancers = useMemo(() => {
    const query = freelancerSearch.trim().toLowerCase()
    if (!query) {
      return freelancers
    }
    const filtered = freelancers.filter((freelancer) =>
      getFreelancerLabel(freelancer.name).toLowerCase().includes(query)
    )
    if (freelancerFilter === "all") {
      return filtered
    }
    const selectedFreelancer = freelancers.find(
      (freelancer) => freelancer.id === freelancerFilter
    )
    if (!selectedFreelancer) {
      return filtered
    }
    if (filtered.some((freelancer) => freelancer.id === selectedFreelancer.id)) {
      return filtered
    }
    return [selectedFreelancer, ...filtered]
  }, [freelancerSearch, freelancerFilter, freelancers])

  return (
    <>
      <Tabs value={activeFilterTab} onValueChange={(value) => setActiveFilterTab(value as FilterTab)}>
        <TabsList>
          <TabsTrigger value="date" aria-label="Filter by date range" className="text-xs">
            <CalendarRange className="mr-1.5 size-3.5" />
            Date Range
          </TabsTrigger>
          <TabsTrigger value="status" aria-label="Filter by remittance status" className="text-xs">
            Status
          </TabsTrigger>
          <TabsTrigger value="freelancer" aria-label="Filter by freelancer" className="text-xs">
            Freelancer
          </TabsTrigger>
        </TabsList>
      </Tabs>

      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="text-base">Filters</CardTitle>
        </CardHeader>
        <CardContent className="pt-0">
          <div className={activeFilterTab === "date" ? "grid gap-3 md:grid-cols-2" : "hidden"}>
            <label className="space-y-1.5 text-xs">
              <span className="text-muted-foreground">Start date</span>
              <Input
                ref={startDateInputRef}
                aria-label="Start date"
                type="text"
                className="h-8 px-2.5 text-xs"
                value={startDate}
                onChange={(event: ChangeEvent<HTMLInputElement>) =>
                  setStartDate(event.target.value)
                }
              />
            </label>
            <label className="space-y-1.5 text-xs">
              <span className="text-muted-foreground">End date</span>
              <Input
                ref={endDateInputRef}
                aria-label="End date"
                type="text"
                className="h-8 px-2.5 text-xs"
                value={endDate}
                onChange={(event: ChangeEvent<HTMLInputElement>) =>
                  setEndDate(event.target.value)
                }
              />
            </label>
          </div>

          {activeFilterTab === "status" ? (
            <div className="flex flex-wrap gap-2">
              {PAYMENTS_STATUS_OPTIONS.map((status) => (
                <Button
                  key={status.value}
                  type="button"
                  variant={remittanceStatus === status.value ? "default" : "outline"}
                  onClick={() => setRemittanceStatus(status.value)}
                  aria-label={`Set status filter to ${status.label}`}
                >
                  {status.label}
                </Button>
              ))}
            </div>
          ) : null}

          {activeFilterTab === "freelancer" ? (
            <div className="space-y-3">
              <label className="space-y-2 text-sm">
                <span>Search freelancer</span>
                <Select value={freelancerFilter} onValueChange={setFreelancerFilter}>
                  <SelectTrigger className="w-full" aria-label="Filter by freelancer">
                    <SelectValue placeholder="All freelancers" />
                  </SelectTrigger>
                  <SelectContent>
                    <div className="p-1">
                      <Input
                        aria-label="Search freelancers"
                        value={freelancerSearch}
                        onChange={(event: ChangeEvent<HTMLInputElement>) =>
                          setFreelancerSearch(event.target.value)
                        }
                        onKeyDown={(event) => event.stopPropagation()}
                        placeholder="Type a freelancer name"
                        className="h-8"
                      />
                    </div>
                    <SelectItem value="all">All freelancers</SelectItem>
                    {visibleFreelancers.length > 0 ? (
                      visibleFreelancers.map((freelancer) => (
                        <SelectItem key={freelancer.id} value={freelancer.id}>
                          {getFreelancerLabel(freelancer.name)}
                        </SelectItem>
                      ))
                    ) : (
                      <div className="text-muted-foreground px-2 py-1.5 text-sm">
                        No freelancers found
                      </div>
                    )}
                  </SelectContent>
                </Select>
              </label>
            </div>
          ) : null}
        </CardContent>
      </Card>
    </>
  )
}
