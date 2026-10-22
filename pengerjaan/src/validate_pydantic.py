import sys
from datetime import datetime
from pydantic import ValidationError
from contract import OrderContract


def run_experiment_4():
    print("=" * 60)
    print("PERCOBAAN 4: Validasi Satu Record Valid")
    print("=" * 60)
    valid_order = {
        "order_id": "ORD-001",
        "customer_id": 101,
        "amount": 250000.0,
        "status": "PAID",
        "transaction_date": datetime(2026, 9, 20, 8, 0),
        "payment_date": datetime(2026, 9, 20, 8, 15),
    }

    try:
        order = OrderContract.model_validate(valid_order)
        print("STATUS: VALID")
        print("Data Terverifikasi:", order)
    except ValidationError as exc:
        print("STATUS: INVALID")
        print(exc)


def run_experiment_5():
    print("\n" + "=" * 60)
    print("PERCOBAAN 5: Menguji Data Invalid (customer_id negatif: -101)")
    print("=" * 60)
    invalid_order = {
        "order_id": "ORD-001",
        "customer_id": -101,  # melanggar gt=0
        "amount": 250000.0,
        "status": "PAID",
        "transaction_date": datetime(2026, 9, 20, 8, 0),
        "payment_date": datetime(2026, 9, 20, 8, 15),
    }

    try:
        order = OrderContract.model_validate(invalid_order)
        print("STATUS: VALID")
        print(order)
    except ValidationError as exc:
        print("STATUS: INVALID")
        print(exc)


def run_experiment_6():
    print("\n" + "=" * 60)
    print("PERCOBAAN 6: Menguji Business Rule (status=PAID, payment_date=None)")
    print("=" * 60)
    invalid_order = {
        "order_id": "ORD-999",
        "customer_id": 999,
        "amount": 100000.0,
        "status": "PAID",
        "transaction_date": datetime(2026, 9, 20, 10, 0),
        "payment_date": None,  # melanggar business rule model_validator
    }

    try:
        order = OrderContract.model_validate(invalid_order)
        print("STATUS: VALID")
        print(order)
    except ValidationError as exc:
        print("STATUS: INVALID")
        print(exc)


def run_experiment_7():
    print("\n" + "=" * 60)
    print("PERCOBAAN 7: Menguji Extra Field (extra='forbid')")
    print("=" * 60)
    invalid_order = {
        "order_id": "ORD-888",
        "customer_id": 888,
        "amount": 100000.0,
        "status": "PENDING",
        "transaction_date": datetime(2026, 9, 20, 10, 0),
        "payment_date": None,
        "unexpected_field": "ABC",  # extra field
    }

    try:
        order = OrderContract.model_validate(invalid_order)
        print("STATUS: VALID")
        print(order)
    except ValidationError as exc:
        print("STATUS: INVALID")
        print(exc)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "exp4_only":
        run_experiment_4()
    else:
        run_experiment_4()
        run_experiment_5()
        run_experiment_6()
        run_experiment_7()
