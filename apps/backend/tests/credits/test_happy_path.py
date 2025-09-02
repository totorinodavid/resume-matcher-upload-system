"""
Happy path tests for the credits system.

Tests successful credit purchase flows with proper balance updates
and transaction recording.
"""

import pytest
import pytest_asyncio
from sqlalchemy import text
from uuid import uuid4

from tests.conftest import (
    insert_user, insert_payment, apply_credit_purchase,
    get_user_balance, count_credit_transactions
)


@pytest_asyncio.fixture
def unique_intent_id():
    """Generate unique payment intent ID for each test."""
    return f"pi_test_{uuid4().hex[:16]}"


class TestHappyPath:
    """Test successful credit purchase scenarios."""

    @pytest_asyncio.async_test
    async def test_successful_credit_purchase(self, db_conn, unique_intent_id):
        """
        Test: User purchases credits successfully.
        
        Arrange: User with 0 balance, PAID payment for 100 credits
        Act: Apply credit purchase 
        Assert: User balance = 100, one transaction recorded
        """
        # Arrange
        user_id = await insert_user(db_conn, start_balance=0)
        payment_id = await insert_payment(
            db_conn, 
            user_id=user_id,
            intent_id=unique_intent_id,
            amount_cents=500,  # €5.00
            expected_credits=100,
            status="PAID"
        )
        
        # Act
        tx_id, new_balance = await apply_credit_purchase(
            db_conn, user_id, payment_id, delta_credits=100
        )
        
        # Assert
        assert new_balance == 100
        assert await get_user_balance(db_conn, user_id) == 100
        assert await count_credit_transactions(db_conn, user_id=user_id) == 1
        assert await count_credit_transactions(db_conn, payment_id=payment_id) == 1
        
        # Verify transaction details
        result = await db_conn.execute(
            text("""
                SELECT delta_credits, reason, user_id, payment_id
                FROM credit_transactions 
                WHERE id = :tx_id
            """),
            {"tx_id": tx_id}
        )
        tx_row = result.fetchone()
        assert tx_row[0] == 100  # delta_credits
        assert tx_row[1] == "PURCHASE"  # reason
        assert tx_row[2] == user_id
        assert tx_row[3] == payment_id

    @pytest_asyncio.async_test
    async def test_multiple_purchases_accumulate(self, db_conn):
        """
        Test: Multiple purchases accumulate correctly.
        
        Arrange: User starts with 50 credits
        Act: Two separate purchases of 100 and 200 credits
        Assert: Final balance = 350, two transactions recorded
        """
        # Arrange
        user_id = await insert_user(db_conn, start_balance=50)
        
        # Act - First purchase
        payment1_id = await insert_payment(
            db_conn, user_id=user_id, 
            intent_id=f"pi_test_first_{uuid4().hex[:8]}",
            expected_credits=100
        )
        tx1_id, balance_after_first = await apply_credit_purchase(
            db_conn, user_id, payment1_id, delta_credits=100
        )
        
        # Act - Second purchase
        payment2_id = await insert_payment(
            db_conn, user_id=user_id,
            intent_id=f"pi_test_second_{uuid4().hex[:8]}",
            expected_credits=200
        )
        tx2_id, balance_after_second = await apply_credit_purchase(
            db_conn, user_id, payment2_id, delta_credits=200
        )
        
        # Assert
        assert balance_after_first == 150  # 50 + 100
        assert balance_after_second == 350  # 150 + 200
        assert await get_user_balance(db_conn, user_id) == 350
        assert await count_credit_transactions(db_conn, user_id=user_id) == 2
        
        # Verify both transactions exist with correct details
        result = await db_conn.execute(
            text("""
                SELECT delta_credits, payment_id 
                FROM credit_transactions 
                WHERE user_id = :user_id 
                ORDER BY created_at
            """),
            {"user_id": user_id}
        )
        transactions = result.fetchall()
        assert len(transactions) == 2
        assert transactions[0][0] == 100  # First purchase
        assert transactions[0][1] == payment1_id
        assert transactions[1][0] == 200  # Second purchase
        assert transactions[1][1] == payment2_id

    @pytest_asyncio.async_test
    async def test_foreign_key_relationships(self, db_conn, unique_intent_id):
        """
        Test: Verify proper foreign key relationships work.
        
        Arrange: User and payment
        Act: Create credit transaction
        Assert: JOIN across all tables returns correct data
        """
        # Arrange
        user_email = f"test-fk-{uuid4()}@example.com"
        user_id = await insert_user(db_conn, email=user_email, start_balance=25)
        payment_id = await insert_payment(
            db_conn, 
            user_id=user_id,
            intent_id=unique_intent_id,
            amount_cents=1000,  # €10.00
            expected_credits=250
        )
        
        # Act
        tx_id, new_balance = await apply_credit_purchase(
            db_conn, user_id, payment_id, delta_credits=250
        )
        
        # Assert - JOIN across all tables
        result = await db_conn.execute(
            text("""
                SELECT 
                    u.email, u.credits_balance,
                    p.amount_total_cents, p.expected_credits, p.status,
                    ct.delta_credits, ct.reason
                FROM users u
                JOIN credit_transactions ct ON u.id = ct.user_id
                JOIN payments p ON ct.payment_id = p.id
                WHERE u.id = :user_id AND ct.id = :tx_id
            """),
            {"user_id": user_id, "tx_id": tx_id}
        )
        
        row = result.fetchone()
        assert row is not None
        assert row[0] == user_email  # u.email
        assert row[1] == 275  # u.credits_balance (25 + 250)
        assert row[2] == 1000  # p.amount_total_cents
        assert row[3] == 250  # p.expected_credits
        assert row[4] == "PAID"  # p.status
        assert row[5] == 250  # ct.delta_credits
        assert row[6] == "PURCHASE"  # ct.reason

    @pytest_asyncio.async_test
    async def test_insert_returning_validation(self, db_conn, unique_intent_id):
        """
        Test: Validate INSERT RETURNING and UPDATE RETURNING work correctly.
        
        Arrange: Fresh user and payment data
        Act: Insert operations with RETURNING clauses
        Assert: RETURNING values match expected results
        """
        # Test user insertion with RETURNING
        user_id_expected = str(uuid4())
        result = await db_conn.execute(
            text("""
                INSERT INTO users (id, email, name, credits_balance)
                VALUES (:user_id, :email, :name, :balance)
                RETURNING id, credits_balance
            """),
            {
                "user_id": user_id_expected,
                "email": f"returning-test-{uuid4()}@example.com",
                "name": "RETURNING Test User",
                "balance": 42
            }
        )
        user_row = result.fetchone()
        assert user_row[0] == user_id_expected  # RETURNING id
        assert user_row[1] == 42  # RETURNING credits_balance
        
        # Test payment insertion with RETURNING
        payment_id_expected = str(uuid4())
        result = await db_conn.execute(
            text("""
                INSERT INTO payments (
                    id, user_id, provider, provider_payment_intent_id,
                    amount_total_cents, currency, expected_credits, 
                    status, raw_provider_data
                )
                VALUES (
                    :payment_id, :user_id, 'stripe', :intent_id,
                    750, 'EUR', 150, 'PAID', '{}'::jsonb
                )
                RETURNING id, expected_credits, status
            """),
            {
                "payment_id": payment_id_expected,
                "user_id": user_id_expected,
                "intent_id": unique_intent_id
            }
        )
        payment_row = result.fetchone()
        assert payment_row[0] == payment_id_expected  # RETURNING id
        assert payment_row[1] == 150  # RETURNING expected_credits
        assert payment_row[2] == "PAID"  # RETURNING status
        
        # Test UPDATE with RETURNING (balance change)
        result = await db_conn.execute(
            text("""
                UPDATE users 
                SET credits_balance = credits_balance + 150
                WHERE id = :user_id
                RETURNING credits_balance
            """),
            {"user_id": user_id_expected}
        )
        new_balance = result.scalar_one()
        assert new_balance == 192  # 42 + 150

    @pytest_asyncio.async_test
    async def test_currency_and_amount_consistency(self, db_conn, unique_intent_id):
        """
        Test: Verify currency and amount constraints work.
        
        Arrange: Payment with specific currency and amount
        Act: Insert payment and verify constraints
        Assert: Data matches expected values, amounts >= 0
        """
        # Arrange
        user_id = await insert_user(db_conn, start_balance=0)
        
        # Act - Insert payment with specific amounts
        payment_id = await insert_payment(
            db_conn,
            user_id=user_id,
            intent_id=unique_intent_id,
            amount_cents=2500,  # €25.00
            expected_credits=500,
            currency="EUR"
        )
        
        # Assert - Verify payment data
        result = await db_conn.execute(
            text("""
                SELECT amount_total_cents, currency, expected_credits
                FROM payments
                WHERE id = :payment_id
            """),
            {"payment_id": payment_id}
        )
        
        row = result.fetchone()
        assert row[0] == 2500  # amount_total_cents
        assert row[1] == "EUR"  # currency
        assert row[2] == 500  # expected_credits
        assert row[0] >= 0  # amount must be non-negative

    @pytest_asyncio.async_test
    async def test_rowcount_verification(self, db_conn, unique_intent_id):
        """
        Test: Verify UPDATE operations affect exactly one row.
        
        Arrange: Single user with known balance
        Act: Update balance and check rowcount
        Assert: Exactly one row affected
        """
        # Arrange
        user_id = await insert_user(db_conn, start_balance=100)
        
        # Act - Update balance with rowcount check
        result = await db_conn.execute(
            text("""
                UPDATE users 
                SET credits_balance = credits_balance + 50
                WHERE id = :user_id
            """),
            {"user_id": user_id}
        )
        
        # Assert
        assert result.rowcount == 1  # Exactly one row updated
        
        # Verify the update actually happened
        final_balance = await get_user_balance(db_conn, user_id)
        assert final_balance == 150
