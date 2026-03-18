import { Loader2 } from "lucide-react"

import { Button } from "@/components/ui/button"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"

type ConfirmBatchDialogProps = {
  open: boolean
  onOpenChange: (open: boolean) => void
  isConfirming: boolean
  onConfirm: () => void
}

export function ConfirmBatchDialog({
  open,
  onOpenChange,
  isConfirming,
  onConfirm,
}: ConfirmBatchDialogProps) {
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Confirm payment batch</DialogTitle>
          <DialogDescription>
            This finalizes the payment batch and records remittances.
          </DialogDescription>
        </DialogHeader>
        <DialogFooter>
          <Button
            type="button"
            variant="outline"
            disabled={isConfirming}
            onClick={() => onOpenChange(false)}
          >
            Cancel
          </Button>
          <Button type="button" disabled={isConfirming} onClick={onConfirm}>
            {isConfirming ? <Loader2 className="mr-1 size-4 animate-spin" /> : null}
            Confirm now
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
