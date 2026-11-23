

import pytest

from loan_service import (
    calculate_emi,
    create_loan,
    generate_summary,
    search_loans,
    filter_by_category
)


def test_zero_interest_emi():
    result = calculate_emi(120000, 0, 12)

    assert result["monthly_emi"] == 10000
    assert result["total_payment"] == 120000
    assert result["total_interest"] == 0


def test_standard_emi():
    result = calculate_emi(100000, 12, 12)

    assert result["monthly_emi"] == 8884.87
    assert result["total_payment"] > 100000
    assert result["total_interest"] > 0


def test_invalid_principal():
    with pytest.raises(ValueError):
        calculate_emi(-10000, 10, 12)


def test_zero_principal():
    with pytest.raises(ValueError):
        calculate_emi(0, 10, 12)


def test_invalid_interest_rate():
    with pytest.raises(ValueError):
        calculate_emi(100000, 150, 12)


def test_invalid_tenure():
    with pytest.raises(ValueError):
        calculate_emi(100000, 10, 0)


def test_non_integer_tenure():
    with pytest.raises(ValueError):
        calculate_emi(100000, 10, 12.5)


def test_invalid_customer_name():
    with pytest.raises(ValueError):
        create_loan(
            "LN001", " ", "Education",
            100000, 10, 12
        )


def test_invalid_category():
    with pytest.raises(ValueError):
        create_loan(
            "LN001", "Rahul", "Invalid",
            100000, 10, 12
        )


def sample_loans():
    return [
        create_loan(
            "LN001", "Rahul", "Education",
            100000, 10, 12
        ),
        create_loan(
            "LN002", "Priya", "Home",
            500000, 8, 60
        ),
        create_loan(
            "LN003", "Arun", "Education",
            200000, 9, 24
        )
    ]


def test_search_by_customer():
    results = search_loans(sample_loans(), "rahul")

    assert len(results) == 1
    assert results[0].customer_name == "Rahul"


def test_search_by_loan_id():
    results = search_loans(sample_loans(), "LN002")

    assert len(results) == 1
    assert results[0].customer_name == "Priya"


def test_category_filter():
    results = filter_by_category(
        sample_loans(), "Education"
    )

    assert len(results) == 2


def test_financial_summary():
    loans = sample_loans()
    summary = generate_summary(loans)

    assert summary["total_records"] == 3
    assert summary["total_principal"] == 800000
    assert summary["total_interest"] > 0
    assert summary["average_emi"] > 0


def test_empty_summary():
    summary = generate_summary([])

    assert summary["total_records"] == 0
    assert summary["total_principal"] == 0
    assert summary["average_emi"] == 0

