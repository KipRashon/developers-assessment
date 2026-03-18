import { useMutation, useQuery } from "@tanstack/react-query"

import {
  confirmPaymentBatch,
  getPaymentBatchReview,
} from "@/features/payments/api/payments.api"
import { PAYMENTS_QUERY_KEYS } from "@/features/payments/constants/payments.constants"
import { createIdempotencyKey } from "@/features/payments/utils/payments.formatters"

type UsePaymentBatchReviewArgs = {
  batchId: string
  onConfirmed: (batchId: string) => void
}

export function usePaymentBatchReview({
  batchId,
  onConfirmed,
}: UsePaymentBatchReviewArgs) {
  const reviewQuery = useQuery({
    queryKey: [PAYMENTS_QUERY_KEYS.batchReview, batchId],
    queryFn: () => getPaymentBatchReview(batchId),
  })

  const confirmMutation = useMutation({
    mutationFn: () => confirmPaymentBatch(batchId, createIdempotencyKey()),
    onSuccess: (data) => {
      onConfirmed(data.batch.id)
    },
  })

  return {
    reviewQuery,
    confirmMutation,
  }
}
