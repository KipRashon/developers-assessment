import { useQuery } from "@tanstack/react-query"

import { getPaymentBatchSummary } from "@/features/payments/api/payments.api"
import { PAYMENTS_QUERY_KEYS } from "@/features/payments/constants/payments.constants"

export function usePaymentBatchSummary(batchId: string) {
  return useQuery({
    queryKey: [PAYMENTS_QUERY_KEYS.batchSummary, batchId],
    queryFn: () => getPaymentBatchSummary(batchId),
  })
}
