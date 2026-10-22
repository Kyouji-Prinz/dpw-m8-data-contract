import argparse
import sys
import pandas as pd
import great_expectations as gx
import great_expectations.expectations as gxe


def build_gx_pipeline():
    context = gx.get_context(mode="ephemeral")

    # 1. Menyiapkan Data Source & Data Asset untuk Pandas DataFrame
    data_source = context.data_sources.add_pandas("orders_datasource")
    data_asset = data_source.add_dataframe_asset(name="orders_asset")
    batch_definition = data_asset.add_batch_definition_whole_dataframe("orders_batch_def")

    # 2. Merancang Expectation Suite sesuai Kontrak Data
    suite = gx.ExpectationSuite(name="orders_data_contract_suite")

    # Rule 1: order_id tidak boleh null
    suite.add_expectation(gxe.ExpectColumnValuesToNotBeNull(column="order_id"))

    # Rule 2: customer_id harus positif (> 0)
    suite.add_expectation(gxe.ExpectColumnValuesToBeBetween(column="customer_id", min_value=1))

    # Rule 3: amount harus non-negatif (>= 0.0)
    suite.add_expectation(gxe.ExpectColumnValuesToBeBetween(column="amount", min_value=0.0))

    # Rule 4: status harus masuk dalam set allowed values
    suite.add_expectation(
        gxe.ExpectColumnValuesToBeInSet(
            column="status",
            value_set=["PAID", "PENDING", "CANCELLED"]
        )
    )

    # Rule 5: transaction_date tidak boleh null
    suite.add_expectation(gxe.ExpectColumnValuesToNotBeNull(column="transaction_date"))

    context.suites.add(suite)

    # 3. Menghubungkan Data & Suite ke dalam Validation Definition
    validation_definition = gx.ValidationDefinition(
        name="orders_validation_def",
        data=batch_definition,
        suite=suite,
    )
    context.validation_definitions.add(validation_definition)

    return validation_definition


def run_gx_validation(csv_path):
    print("=" * 65)
    print(f"GREAT EXPECTATIONS (GX CORE 1.x) VALIDATION: {csv_path}")
    print("=" * 65)

    df = pd.read_csv(csv_path)
    val_def = build_gx_pipeline()

    # Eksekusi validasi batch
    result = val_def.run(batch_parameters={"dataframe": df})

    print(f"Status Evaluasi Keseluruhan : {'PASS (VALID)' if result.success else 'FAIL (INVALID)'}")
    print("\nDetail Hasil Tiap Expectation:")

    for res in result.results:
        exp_type = res.expectation_config.type
        exp_col = res.expectation_config.kwargs.get("column", "table")
        status = "PASSED" if res.success else "FAILED"
        print(f" - [{status}] {exp_type} pada kolom '{exp_col}'")
        if not res.success:
            details = res.result
            unexpected_count = details.get("unexpected_count", 0)
            unexpected_values = details.get("partial_unexpected_list", [])
            print(f"    * Jumlah data cacat : {unexpected_count}")
            print(f"    * Sampel nilai cacat: {unexpected_values}")

    print("=" * 65)
    return result.success


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Great Expectations Data Contract Validator")
    parser.add_argument("--data", default="../data/orders_valid.csv", help="Path dataset CSV")
    args = parser.parse_args()

    success = run_gx_validation(args.data)
    if not success:
        sys.exit(1)
