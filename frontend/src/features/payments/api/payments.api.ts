import { AxiosError } from "axios"

import { apiClient } from "@/lib/api/client"
import type {
  FreelancersResponse,
  PaymentBatchConfirmResponse,
  PaymentBatchCreatePayload,
  PaymentBatchExclusionsPayload,
  PaymentBatchReviewResponse,
  PaymentBatchSummary,
  RemittanceStatusFilter,
  WorklogDetail,
  WorklogsResponse,
} from "@/features/payments/types/payments.types"

function toApiError(error: unknown, fallbackMessage: string): Error {
  if (error instanceof AxiosError) {
    const detail = (error.response?.data as { detail?: string } | undefined)?.detail
    return new Error(detail || fallbackMessage)
  }
  if (error instanceof Error) {
    return error
  }
  return new Error(fallbackMessage)
}

export async function getWorklogs(
  startDate: string,
  endDate: string,
  remittanceStatus: RemittanceStatusFilter,
  freelancerId?: string,
): Promise<WorklogsResponse> {
  try {
    const params: Record<string, string> = {
      start_date: startDate,
      end_date: endDate,
    }
    if (remittanceStatus !== "all") {
      params.remittanceStatus = remittanceStatus
    }
    if (freelancerId && freelancerId !== "all") {
      params.freelancerId = freelancerId
    }
    const response = await apiClient.get<WorklogsResponse>("/api/v1/worklogs/", {
      params,
    })
    return response.data
  } catch (error) {
    throw toApiError(error, "Failed to load worklogs")
  }
}

export async function getWorklogFreelancers(
  startDate: string,
  endDate: string,
  remittanceStatus: RemittanceStatusFilter,
): Promise<FreelancersResponse> {
  try {
    const params: Record<string, string> = {
      start_date: startDate,
      end_date: endDate,
    }
    if (remittanceStatus !== "all") {
      params.remittanceStatus = remittanceStatus
    }
    const response = await apiClient.get<FreelancersResponse>(
      "/api/v1/worklogs/freelancers",
      {
        params,
      },
    )
    return response.data
  } catch (error) {
    throw toApiError(error, "Failed to load freelancers")
  }
}

export async function getWorklogDetail(worklogId: string): Promise<WorklogDetail> {
  try {
    const response = await apiClient.get<WorklogDetail>(`/api/v1/worklogs/${worklogId}`)
    return response.data
  } catch (error) {
    throw toApiError(error, "Failed to load worklog details")
  }
}

export async function createPaymentBatch(
  payload: PaymentBatchCreatePayload,
): Promise<PaymentBatchSummary> {
  try {
    const response = await apiClient.post<PaymentBatchSummary>(
      "/api/v1/payment-batches/",
      payload,
    )
    return response.data
  } catch (error) {
    throw toApiError(error, "Failed to create payment batch")
  }
}

export async function updatePaymentBatchExclusions(
  batchId: string,
  payload: PaymentBatchExclusionsPayload,
): Promise<PaymentBatchSummary> {
  try {
    const response = await apiClient.put<PaymentBatchSummary>(
      `/api/v1/payment-batches/${batchId}/exclusions`,
      payload,
    )
    return response.data
  } catch (error) {
    throw toApiError(error, "Failed to apply exclusions")
  }
}

export async function getPaymentBatchReview(
  batchId: string,
): Promise<PaymentBatchReviewResponse> {
  try {
    const response = await apiClient.get<PaymentBatchReviewResponse>(
      `/api/v1/payment-batches/${batchId}/review`,
    )
    return response.data
  } catch (error) {
    throw toApiError(error, "Failed to load payment batch review")
  }
}

export async function confirmPaymentBatch(
  batchId: string,
  idempotencyKey: string,
): Promise<PaymentBatchConfirmResponse> {
  try {
    const response = await apiClient.post<PaymentBatchConfirmResponse>(
      `/api/v1/payment-batches/${batchId}/confirm`,
      undefined,
      {
        headers: {
          "Idempotency-Key": idempotencyKey,
        },
      },
    )
    return response.data
  } catch (error) {
    throw toApiError(error, "Failed to confirm payment batch")
  }
}

export async function getPaymentBatchSummary(
  batchId: string,
): Promise<PaymentBatchSummary> {
  try {
    const response = await apiClient.get<PaymentBatchSummary>(
      `/api/v1/payment-batches/${batchId}`,
    )
    return response.data
  } catch (error) {
    throw toApiError(error, "Failed to load confirmation status")
  }
}
