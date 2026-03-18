import { Outlet, createFileRoute } from "@tanstack/react-router"

export const Route = createFileRoute("/_layout/payments")({
  component: PaymentsLayout,
  head: () => ({
    meta: [
      {
        title: "Payments - FastAPI Cloud",
      },
    ],
  }),
})

function PaymentsLayout() {
  return <Outlet />
}
