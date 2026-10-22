import argparse
import csv
import os
from datetime import datetime
from pydantic import ValidationError

from contract import OrderContract


def parse_datetime(value):
    if value is None or value == "":
        return None
    return datetime.fromisoformat(value)


def load_orders(path):
    with open(path, newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        rows = []
        for row in reader:
            parsed_row = {
                "order_id": row["order_id"],
                "customer_id": int(row["customer_id"]) if row.get("customer_id") and row["customer_id"].lstrip("-").isdigit() else row.get("customer_id"),
                "amount": float(row["amount"]) if row.get("amount") and row["amount"].replace(".", "", 1).lstrip("-").isdigit() else row.get("amount"),
                "status": row["status"],
                "transaction_date": parse_datetime(row.get("transaction_date")),
                "payment_date": parse_datetime(row.get("payment_date")),
            }
            # Capture any extra fields present in CSV
            for key, val in row.items():
                if key not in parsed_row:
                    parsed_row[key] = val
            rows.append(parsed_row)
        return rows


def validate_batch(rows):
    errors = []
    valid_orders = []

    for row_number, row in enumerate(rows, start=2):
        try:
            order = OrderContract.model_validate(row)
            valid_orders.append(order)
        except ValidationError as exc:
            errors.append(
                {
                    "row": row_number,
                    "order_id": row.get("order_id"),
                    "errors": exc.errors(),
                }
            )

    return valid_orders, errors


def save_to_warehouse(orders, output_path):
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    with open(output_path, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(
            [
                "order_id",
                "customer_id",
                "amount",
                "status",
                "transaction_date",
                "payment_date",
            ]
        )
        for order in orders:
            writer.writerow(
                [
                    order.order_id,
                    order.customer_id,
                    order.amount,
                    order.status,
                    order.transaction_date.isoformat(),
                    order.payment_date.isoformat() if order.payment_date else "",
                ]
            )


def run_pipeline(input_path, warehouse_path="../data/warehouse_orders.csv", fail_fast=True):
    print(f"\n[PIPELINE START] Membaca dataset: {input_path}")
    rows = load_orders(input_path)
    valid_orders, errors = validate_batch(rows)

    print(f"Jumlah record : {len(rows)}")
    print(f"Valid         : {len(valid_orders)}")
    print(f"Invalid       : {len(errors)}")

    if errors:
        print("\n" + "!" * 50)
        print("FAIL-FAST: BATCH DITOLAK KARENA MEMILIKI DATA CACAT!")
        print("!" * 50)
        print("Detail Pelanggaran Data Contract:")
        for err in errors:
            print(f" -> Baris {err['row']} (order_id={err['order_id']}):")
            for sub_err in err["errors"]:
                loc = ".".join(str(l) for l in sub_err.get("loc", []))
                msg = sub_err.get("msg", "")
                err_type = sub_err.get("type", "")
                print(f"    - Lokasi: '{loc}' | Error: {msg} ({err_type})")

        if fail_fast:
            print("\n[QUALITY GATE REJECT] Proses dihentikan sebelum menyentuh Data Warehouse.")
            return False, valid_orders, errors

    print("\n" + "=" * 50)
    print("BATCH VALID: Semua record memenuhi spesifikasi Data Contract.")
    save_to_warehouse(valid_orders, warehouse_path)
    print(f"SUCCESS: {len(valid_orders)} record berhasil dimuat ke Data Warehouse ({warehouse_path}).")
    print("=" * 50)
    return True, valid_orders, errors


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Automated Data Contract Batch Validator")
    parser.add_argument("--data", default="../data/orders_valid.csv", help="Path ke file dataset CSV")
    parser.add_argument("--warehouse", default="../data/warehouse_orders.csv", help="Path file Data Warehouse target")
    parser.add_argument("--no-fail-fast", action="store_true", help="Nonaktifkan exit code saat gagal")

    args = parser.parse_args()

    success, valids, errs = run_pipeline(
        input_path=args.data,
        warehouse_path=args.warehouse,
        fail_fast=True
    )

    if not success and not args.no_fail_fast:
        raise SystemExit(1)
