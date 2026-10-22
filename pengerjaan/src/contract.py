from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class OrderContract(BaseModel):
    model_config = ConfigDict(
        strict=True,
        extra="forbid",
    )

    order_id: str = Field(min_length=1)
    customer_id: int = Field(gt=0)
    amount: float = Field(ge=0)
    status: Literal["PAID", "PENDING", "CANCELLED"]
    transaction_date: datetime
    payment_date: datetime | None = None

    @model_validator(mode="after")
    def paid_requires_payment_date(self):
        if self.status == "PAID" and self.payment_date is None:
            raise ValueError(
                "payment_date wajib diisi jika status=PAID"
            )
        return self


if __name__ == "__main__":
    print("=" * 65)
    print("[INFO] File 'contract.py' adalah modul definisi skema (OrderContract).")
    print("[OK] Skema Pydantic berhasil dimuat tanpa error!")
    print("=" * 65)
    print("Untuk melihat hasil pengujian dan error validasi, jalankan:")
    print(" -> python validate_pydantic.py  (Validasi record: Percobaan 4 - 7)")
    print(" -> python validate_batch.py     (Validasi batch & Fail-Fast: Percobaan 8 - 12)")
    print(" -> python validate_gx.py        (Validasi Great Expectations: Percobaan 14)")
    print("=" * 65)

