const currencyFormatter = new Intl.NumberFormat("en-US", {
  style: "currency",
  currency: "USD",
  minimumFractionDigits: 2,
  maximumFractionDigits: 2,
})

const usDateFormatter = new Intl.DateTimeFormat("en-US", {
  dateStyle: "medium",
})

const usDateTimeFormatter = new Intl.DateTimeFormat("en-US", {
  dateStyle: "medium",
  timeStyle: "short",
})

export function formatMoney(amount: number) {
  return currencyFormatter.format(amount)
}

export function formatRemittanceStatus(status: string) {
  if (status === "REMITTED") {
    return "Remitted"
  }
  if (status === "UNREMITTED") {
    return "Unremitted"
  }
  return status
}

export function formatUsDate(value: string) {
  const dateOnlyMatch = value.match(/^(\d{4})-(\d{2})-(\d{2})$/)
  if (dateOnlyMatch) {
    const year = Number(dateOnlyMatch[1])
    const month = Number(dateOnlyMatch[2])
    const day = Number(dateOnlyMatch[3])
    return usDateFormatter.format(new Date(year, month - 1, day))
  }

  const parsedDate = new Date(value)
  if (Number.isNaN(parsedDate.getTime())) {
    return value
  }
  return usDateFormatter.format(parsedDate)
}

export function formatUsDateTime(value: string) {
  const parsedDate = new Date(value)
  if (Number.isNaN(parsedDate.getTime())) {
    return value
  }
  return usDateTimeFormatter.format(parsedDate)
}

export function createIdempotencyKey() {
  if (typeof crypto !== "undefined" && typeof crypto.randomUUID === "function") {
    return crypto.randomUUID()
  }
  return `${Date.now()}-payment-confirm`
}
