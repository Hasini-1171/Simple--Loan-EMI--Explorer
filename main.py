
import uuid
from pathlib import Path
from loan_service import (
    CATEGORIES,
    create_loan,
    generate_summary,
    search_loans,
    filter_by_category
)

from storage import (
    save_loans,
    load_loans,
    import_csv
)


def line():
    print("=" * 65)


def header(title):
    print("\n")
    line()
    print(title.center(65))
    line()


def get_float(prompt, minimum, maximum):
    while True:
        try:
            value = float(input(prompt))

            if minimum <= value <= maximum:
                return value

            print(f"Enter a value between {minimum} and {maximum}.")

        except ValueError:
            print("Please enter a valid number.")


def get_integer(prompt, minimum, maximum):
    while True:
        try:
            value = int(input(prompt))

            if minimum <= value <= maximum:
                return value

            print(f"Enter a number between {minimum} and {maximum}.")

        except ValueError:
            print("Please enter a whole number.")


def add_loan(loans):
    header("NEW LOAN APPLICATION")

    name = input("Customer name: ").strip()

    print("\nLoan categories:")
    for index, category in enumerate(CATEGORIES, 1):
        print(f"{index}. {category}")

    category = CATEGORIES[
        get_integer("Choose category: ", 1, len(CATEGORIES)) - 1
    ]

    principal = get_float("Loan amount (Rs.): ", 0.01, 1_000_000_000)
    rate = get_float("Annual interest rate (%): ", 0, 100)
    months = get_integer("Tenure in months: ", 1, 600)

    loan = create_loan(
        "LN-" + uuid.uuid4().hex[:10].upper(),
        name,
        category,
        principal,
        rate,
        months
    )

    print("\nLOAN CALCULATION RESULT")
    line()

    print(f"Loan ID          : {loan.loan_id}")
    print(f"Customer         : {loan.customer_name}")
    print(f"Loan amount      : Rs. {loan.principal:,.2f}")
    print(f"Monthly EMI      : Rs. {loan.monthly_emi:,.2f}")
    print(f"Total interest   : Rs. {loan.total_interest:,.2f}")
    print(f"Total repayment  : Rs. {loan.total_payment:,.2f}")

    answer = input("\nSave this record? (y/n): ").lower().strip()

    if answer == "y":
        loans.append(loan)

        try:
            save_loans(loans)
            print("Loan record saved successfully.")
        except (OSError, ValueError, TypeError) as error:
            loans.pop()
            print(f"Unable to save record: {error}")


def view_loans(loans):
    header("ALL LOAN RECORDS")

    if not loans:
        print("No records found.")
        return

    for loan in loans:
        print(
            f"\n{loan.loan_id} | {loan.customer_name} | "
            f"{loan.category}"
        )
        print(f"Principal : Rs. {loan.principal:,.2f}")
        print(f"Monthly EMI: Rs. {loan.monthly_emi:,.2f}")
        print(f"Interest  : Rs. {loan.total_interest:,.2f}")


def search_menu(loans):
    header("SEARCH LOAN RECORDS")

    print("1. Search by name or ID")
    print("2. Filter by category")

    choice = input("Choose option: ").strip()

    if choice == "1":
        keyword = input("Enter customer name or loan ID: ")
        results = search_loans(loans, keyword)

    elif choice == "2":
        for i, category in enumerate(CATEGORIES, 1):
            print(f"{i}. {category}")

        category = CATEGORIES[
            get_integer("Choose category: ", 1, len(CATEGORIES)) - 1
        ]

        results = filter_by_category(loans, category)

    else:
        print("Invalid option.")
        return

    if results:
        view_loans(results)
    else:
        print("No matching records found.")


def show_summary(loans):
    header("EXECUTIVE FINANCIAL SUMMARY")

    summary = generate_summary(loans)

    if summary["total_records"] == 0:
        print("No financial data available.")
        return

    print(f"Total loan records : {summary['total_records']}")
    print(f"Total principal    : Rs. {summary['total_principal']:,.2f}")
    print(f"Total interest     : Rs. {summary['total_interest']:,.2f}")
    print(f"Total repayment    : Rs. {summary['total_payment']:,.2f}")
    print(f"Average EMI        : Rs. {summary['average_emi']:,.2f}")

    high_interest = sum(
        loan.annual_rate >= 15 for loan in loans
    )

    print(f"High-rate loans    : {high_interest}")


def generate_chart(loans):
    header("FINANCIAL VISUALIZATION")

    if not loans:
        print("No records available.")
        return

    try:
        import matplotlib.pyplot as plt

        report_dir = Path(__file__).resolve().parent / "reports"
        report_dir.mkdir(exist_ok=True)

        names = [loan.customer_name for loan in loans]
        emis = [loan.monthly_emi for loan in loans]
        amounts = [loan.principal for loan in loans]

        fig, axes = plt.subplots(1, 2, figsize=(12, 5))

        axes[0].bar(names, emis)
        axes[0].set_title("Monthly EMI Comparison")
        axes[0].set_ylabel("EMI (Rs.)")
        axes[0].tick_params(axis="x", rotation=45)

        axes[1].bar(names, amounts)
        axes[1].set_title("Loan Amount Comparison")
        axes[1].set_ylabel("Principal (Rs.)")
        axes[1].tick_params(axis="x", rotation=45)

        fig.tight_layout()

        path = report_dir / "loan_analytics.png"
        fig.savefig(path, dpi=180)
        plt.show()
        plt.close(fig)

        print(f"Chart saved at: {path}")

    except ImportError:
        print("Matplotlib is missing. Install requirements first.")

    except OSError as error:
        print(f"Unable to save chart: {error}")


def export_report(loans):
    header("EXPORT FINANCIAL REPORT")

    if not loans:
        print("No records available.")
        return

    report_dir = Path(__file__).resolve().parent / "reports"
    report_dir.mkdir(exist_ok=True)

    path = report_dir / "financial_report.txt"
    summary = generate_summary(loans)

    try:
        with path.open("w", encoding="utf-8") as file:
            file.write("SIMPLE LOAN EMI EXPLORER\n")
            file.write("=" * 50 + "\n")
            file.write(f"Total records: {summary['total_records']}\n")
            file.write(f"Principal: Rs. {summary['total_principal']:,.2f}\n")
            file.write(f"Interest: Rs. {summary['total_interest']:,.2f}\n")
            file.write(f"Repayment: Rs. {summary['total_payment']:,.2f}\n")

            file.write("\nINDIVIDUAL LOAN DETAILS\n")

            for loan in loans:
                file.write(
                    f"\n{loan.loan_id} - {loan.customer_name}\n"
                    f"Principal: Rs. {loan.principal:,.2f}\n"
                    f"EMI: Rs. {loan.monthly_emi:,.2f}\n"
                    f"Interest: Rs. {loan.total_interest:,.2f}\n"
                )

        print(f"Report exported: {path}")

    except OSError as error:
        print(f"Report export failed: {error}")


def bulk_import(loans):
    header("BULK CSV IMPORT")

    path = input("Enter CSV file path: ").strip().strip('"')

    try:
        imported, errors = import_csv(path, loans)

        updated = loans + imported

        save_loans(updated)
        loans.extend(imported)

        print(f"Successfully imported: {len(imported)}")
        print(f"Rejected records: {len(errors)}")

        if errors:
            report_dir = Path(__file__).resolve().parent / "reports"
            report_dir.mkdir(exist_ok=True)

            error_path = report_dir / "import_errors.txt"
            error_path.write_text(
                "\n".join(errors),
                encoding="utf-8"
            )

            print(f"Error details saved: {error_path}")

    except (OSError, ValueError) as error:
        print(f"Import failed: {error}")


def main():
    loans = load_loans()

    while True:
        header("SIMPLE LOAN EMI EXPLORER")

        options = [
            "Calculate New Loan EMI",
            "View All Loan Records",
            "Search and Filter Loans",
            "Executive Financial Summary",
            "Generate Financial Charts",
            "Export Financial Report",
            "Bulk CSV Import",
            "Exit"
        ]

        for index, option in enumerate(options, 1):
            print(f"{index}. {option}")

        choice = input("\nSelect option (1-8): ").strip()

        try:
            if choice == "1":
                add_loan(loans)

            elif choice == "2":
                view_loans(loans)

            elif choice == "3":
                search_menu(loans)

            elif choice == "4":
                show_summary(loans)

            elif choice == "5":
                generate_chart(loans)

            elif choice == "6":
                export_report(loans)

            elif choice == "7":
                bulk_import(loans)

            elif choice == "8":
                save_loans(loans)
                print("Thank you for using Simple Loan EMI Explorer!")
                break

            else:
                print("Invalid option. Choose 1 to 8.")

        except (ValueError, OSError) as error:
            print(f"Operation failed: {error}")

        input("\nPress Enter to continue...")


if __name__ == "__main__":
    main()
