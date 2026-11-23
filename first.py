
from dataclasses import dataclass
from math import isfinite


MAX_LOAN_AMOUNT = 1_000_000_000
MAX_INTEREST_RATE = 100
MAX_TENURE = 600

CATEGORIES = (
    "Education", "Home", "Personal",
    "Vehicle", "Business", "Other"
)


@dataclass
class Loan:
    loan_id: str
    customer_name: str
    category: str
    principal: float
    annual_rate: float
    tenure_months: int
    monthly_emi: float
    total_payment: float
    total_interest: float


def calculate_emi(principal, annual_rate, months):
    """Calculate EMI, total repayment and total interest."""

    if not isfinite(principal) or not isfinite(annual_rate):
        raise ValueError("Values must be finite numbers.")

    if not 0 < principal <= MAX_LOAN_AMOUNT:
        raise ValueError("Invalid loan amount.")

    if not 0 <= annual_rate <= MAX_INTEREST_RATE:
        raise ValueError("Invalid interest rate.")

    if not isinstance(months, int) or isinstance(months, bool):
        raise ValueError("Tenure must be a whole number.")

    if not 1 <= months <= MAX_TENURE:
        raise ValueError("Invalid loan tenure.")

    monthly_rate = annual_rate / 1200

    if monthly_rate == 0:
        emi = principal / months
    else:
        factor = (1 + monthly_rate) ** months
        emi = principal * monthly_rate * factor / (factor - 1)

    total_payment = emi * months
    total_interest = total_payment - principal

    return {
        "monthly_emi": round(emi, 2),
        "total_payment": round(total_payment, 2),
        "total_interest": round(total_interest, 2)
    }


def validate_customer(name):
    if not isinstance(name, str) or not name.strip():
        raise ValueError("Customer name cannot be empty.")

    if len(name.strip()) > 80:
        raise ValueError("Customer name is too long.")

    return name.strip()


def create_loan(
    loan_id,
    customer_name,
    category,
    principal,
    annual_rate,
    tenure_months
):
    """Create a validated loan object."""

    name = validate_customer(customer_name)

    if category not in CATEGORIES:
        raise ValueError("Invalid loan category.")

    result = calculate_emi(
        principal,
        annual_rate,
        tenure_months
    )

    return Loan(
        loan_id=str(loan_id),
        customer_name=name,
        category=category,
        principal=float(principal),
        annual_rate=float(annual_rate),
        tenure_months=tenure_months,
        monthly_emi=result["monthly_emi"],
        total_payment=result["total_payment"],
        total_interest=result["total_interest"]
    )


def generate_summary(loans):
    """Generate executive financial statistics."""

    if not loans:
        return {
            "total_records": 0,
            "total_principal": 0,
            "total_interest": 0,
            "total_payment": 0,
            "average_emi": 0
        }

    count = len(loans)

    return {
        "total_records": count,
        "total_principal": round(
            sum(x.principal for x in loans), 2
        ),
        "total_interest": round(
            sum(x.total_interest for x in loans), 2
        ),
        "total_payment": round(
            sum(x.total_payment for x in loans), 2
        ),
        "average_emi": round(
            sum(x.monthly_emi for x in loans) / count, 2
        )
    }


def search_loans(loans, keyword):
    """Search by customer name or loan ID."""

    keyword = keyword.strip().casefold()

    if not keyword:
        return []

    return [
        loan for loan in loans
        if keyword in loan.customer_name.casefold()
        or keyword in loan.loan_id.casefold()
    ]


def filter_by_category(loans, category):
    return [
        loan for loan in loans
        if loan.category == category
    ]
