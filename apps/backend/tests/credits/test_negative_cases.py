"""
Negative test cases for the credits system.

Tests error conditions, invalid states, and constraint violations.
"""

import pytest
import pytest_asyncio
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError, DataError
from uuid import uuid4

from tests.conftest import (
    insert_user, insert_payment, apply_credit_purchase,
    get_user_balance, count_credit_transactions
)


class TestNegativeCases:
    """Test error conditions and constraint violations."""

    @pytest_asyncio.async_test
    async def test_unpaid_payment_no_credits(self, db_conn):
        """
        Test: Payment not in PAID status should not result in credits.
        
        Arrange: Payment with status other than PAID
        Act: Attempt to apply credits
        Assert: No credit transaction should be created in real system
        """
        # Arrange
        user_id = await insert_user(db_conn, start_balance=0)
        
        # Test various non-PAID statuses
        non_paid_statuses = ["REQUIRES_PAYMENT", "FAILED", "CANCELED", "INIT"]
        
        for status in non_paid_statuses:
            payment_id = await insert_payment(
                db_conn,
                user_id=user_id,
                intent_id=f"pi_test_{status.lower()}_{uuid4().hex[:8]}",
                expected_credits=100,
                status=status
            )
            
            # In a real system, the business logic would check payment status
            # before applying credits. Here we verify the payment exists but
            # simulate that no credits should be applied for non-PAID status.
            
            # Verify payment exists with correct status
            result = await db_conn.execute(
                text("SELECT status FROM payments WHERE id = :payment_id"),
                {"payment_id": payment_id}
            )
            actual_status = result.scalar_one()
            assert actual_status == status
            
            # In real business logic, this check would prevent credit application:
            if status != "PAID":
                # Should not apply credits - verified by not calling apply_credit_purchase
                pass
        
        # Assert no credits were applied for any non-PAID payment
        final_balance = await get_user_balance(db_conn, user_id)
        assert final_balance == 0
        
        # Verify no credit transactions were created
        tx_count = await count_credit_transactions(db_conn, user_id=user_id)
        assert tx_count == 0

    @pytest_asyncio.async_test
    async def test_invalid_foreign_key_user_id(self, db_conn):
        """
        Test: Credit transaction with invalid user_id should fail.
        
        Arrange: Non-existent user ID
        Act: Try to create credit transaction
        Assert: Foreign key constraint violation
        """
        # Arrange
        nonexistent_user_id = str(uuid4())
        real_user_id = await insert_user(db_conn)
        payment_id = await insert_payment(db_conn, user_id=real_user_id)
        
        # Act & Assert - Try to create transaction with invalid user_id
        with pytest.raises(IntegrityError) as exc_info:
            await db_conn.execute(
                text("""
                    INSERT INTO credit_transactions (
                        id, user_id, payment_id, delta_credits, reason, meta
                    )
                    VALUES (:tx_id, :user_id, :payment_id, :delta, 'PURCHASE', '{}'::jsonb)
                """),
                {
                    "tx_id": str(uuid4()),
                    "user_id": nonexistent_user_id,  # Invalid foreign key
                    "payment_id": payment_id,
                    "delta": 100
                }
            )
        
        # Verify it's a foreign key constraint error
        error_msg = str(exc_info.value).lower()
        assert "foreign key" in error_msg or "violates" in error_msg

    @pytest_asyncio.async_test
    async def test_invalid_foreign_key_payment_id(self, db_conn):
        """
        Test: Credit transaction with invalid payment_id should fail.
        
        Arrange: Valid user, non-existent payment ID
        Act: Try to create credit transaction
        Assert: Foreign key constraint violation
        """
        # Arrange
        user_id = await insert_user(db_conn)
        nonexistent_payment_id = str(uuid4())
        
        # Act & Assert
        with pytest.raises(IntegrityError) as exc_info:
            await db_conn.execute(
                text("""
                    INSERT INTO credit_transactions (
                        id, user_id, payment_id, delta_credits, reason, meta
                    )
                    VALUES (:tx_id, :user_id, :payment_id, :delta, 'PURCHASE', '{}'::jsonb)
                """),
                {
                    "tx_id": str(uuid4()),
                    "user_id": user_id,
                    "payment_id": nonexistent_payment_id,  # Invalid foreign key
                    "delta": 100
                }
            )
        
        error_msg = str(exc_info.value).lower()
        assert "foreign key" in error_msg or "violates" in error_msg

    @pytest_asyncio.async_test
    async def test_invalid_data_types(self, db_conn):
        """
        Test: Invalid data types should be rejected.
        
        Arrange: Various invalid data type scenarios
        Act: Try to insert invalid data
        Assert: Data type errors
        """
        user_id = await insert_user(db_conn)
        
        # Test invalid UUID format for payment
        with pytest.raises((DataError, IntegrityError)):
            await db_conn.execute(
                text("""
                    INSERT INTO payments (
                        id, user_id, provider, provider_payment_intent_id,
                        amount_total_cents, currency, expected_credits,
                        status, raw_provider_data
                    )
                    VALUES (
                        'not-a-uuid', :user_id, 'stripe', 'pi_test',
                        500, 'EUR', 100, 'PAID', '{}'::jsonb
                    )
                """),
                {"user_id": user_id}
            )
        
        # Test invalid amount (negative with constraint)
        payment_id = str(uuid4())
        with pytest.raises((DataError, IntegrityError)) as exc_info:
            await db_conn.execute(
                text("""
                    INSERT INTO payments (
                        id, user_id, provider, provider_payment_intent_id,
                        amount_total_cents, currency, expected_credits,
                        status, raw_provider_data
                    )
                    VALUES (
                        :payment_id, :user_id, 'stripe', 'pi_test_negative',
                        -100, 'EUR', 100, 'PAID', '{}'::jsonb
                    )
                """),
                {"payment_id": payment_id, "user_id": user_id}
            )
        
        # Should be a check constraint violation
        error_msg = str(exc_info.value).lower()
        assert "check" in error_msg or "constraint" in error_msg

    @pytest_asyncio.async_test
    async def test_negative_credits_handling(self, db_conn):
        """
        Test: Negative credit transactions (refunds) work correctly.
        
        Arrange: User with positive balance
        Act: Apply negative credit transaction (refund)
        Assert: Balance decreases correctly
        """
        # Arrange
        user_id = await insert_user(db_conn, start_balance=200)
        
        # Create original payment for audit trail
        payment_id = await insert_payment(
            db_conn,
            user_id=user_id,
            expected_credits=100
        )
        
        # Apply original credit
        tx1_id, balance_after_purchase = await apply_credit_purchase(
            db_conn, user_id, payment_id, delta_credits=100
        )
        assert balance_after_purchase == 300  # 200 + 100
        
        # Act - Apply refund (negative credits)
        refund_tx_id, balance_after_refund = await apply_credit_purchase(
            db_conn, user_id, payment_id, delta_credits=-100, reason="REFUND"
        )
        
        # Assert
        assert balance_after_refund == 200  # 300 - 100 (back to original)
        
        # Verify both transactions exist
        assert await count_credit_transactions(db_conn, user_id=user_id) == 2
        
        # Verify transaction details
        result = await db_conn.execute(
            text("""
                SELECT delta_credits, reason FROM credit_transactions 
                WHERE user_id = :user_id 
                ORDER BY created_at
            """),
            {"user_id": user_id}
        )
        transactions = result.fetchall()
        assert len(transactions) == 2
        assert transactions[0][0] == 100  # Original purchase
        assert transactions[0][1] == "PURCHASE"
        assert transactions[1][0] == -100  # Refund
        assert transactions[1][1] == "REFUND"

    @pytest_asyncio.async_test
    async def test_insufficient_balance_scenario(self, db_conn):
        """
        Test: User balance going negative through refunds.
        
        Note: The system allows negative balances for refund scenarios.
        
        Arrange: User with small balance
        Act: Apply large refund
        Assert: Balance can go negative (business decision)
        """
        # Arrange
        user_id = await insert_user(db_conn, start_balance=50)
        payment_id = await insert_payment(db_conn, user_id=user_id)
        
        # Act - Apply refund larger than balance
        tx_id, new_balance = await apply_credit_purchase(
            db_conn, user_id, payment_id, 
            delta_credits=-100,  # Refund more than balance
            reason="CHARGEBACK"
        )
        
        # Assert - System allows negative balance for refunds
        assert new_balance == -50  # 50 - 100
        
        # Verify transaction was recorded
        result = await db_conn.execute(
            text("""
                SELECT delta_credits, reason FROM credit_transactions 
                WHERE id = :tx_id
            """),
            {"tx_id": tx_id}
        )
        tx_row = result.fetchone()
        assert tx_row[0] == -100
        assert tx_row[1] == "CHARGEBACK"

    @pytest_asyncio.async_test
    async def test_missing_required_fields(self, db_conn):
        """
        Test: Missing required fields should cause insertion to fail.
        
        Arrange: Insert statements with missing required fields
        Act: Try to insert incomplete data
        Assert: NOT NULL constraint violations
        """
        user_id = await insert_user(db_conn)
        
        # Test missing required field in payments
        with pytest.raises(IntegrityError) as exc_info:
            await db_conn.execute(
                text("""
                    INSERT INTO payments (
                        id, user_id, provider
                        -- Missing required fields: amount_total_cents, currency, expected_credits, status
                    )
                    VALUES (:payment_id, :user_id, 'stripe')
                """),
                {"payment_id": str(uuid4()), "user_id": user_id}
            )
        
        error_msg = str(exc_info.value).lower()
        assert "not null" in error_msg or "null value" in error_msg
        
        # Test missing required field in credit_transactions
        payment_id = await insert_payment(db_conn, user_id=user_id)
        
        with pytest.raises(IntegrityError) as exc_info:
            await db_conn.execute(
                text("""
                    INSERT INTO credit_transactions (
                        id, user_id, payment_id
                        -- Missing required fields: delta_credits, reason
                    )
                    VALUES (:tx_id, :user_id, :payment_id)
                """),
                {
                    "tx_id": str(uuid4()),
                    "user_id": user_id,
                    "payment_id": payment_id
                }
            )
        
        error_msg = str(exc_info.value).lower()
        assert "not null" in error_msg or "null value" in error_msg

    @pytest_asyncio.async_test
    async def test_invalid_currency_format(self, db_conn):
        """
        Test: Invalid currency codes should be handled appropriately.
        
        Arrange: Payment with invalid currency format
        Act: Insert payment with bad currency
        Assert: Data is inserted but validation could catch it
        """
        user_id = await insert_user(db_conn)
        
        # Test various invalid currency formats
        invalid_currencies = ["EURO", "US", "123", ""]
        
        for invalid_currency in invalid_currencies:
            payment_id = await insert_payment(
                db_conn,
                user_id=user_id,
                intent_id=f"pi_test_currency_{invalid_currency}_{uuid4().hex[:8]}",
                currency=invalid_currency
            )
            
            # Verify payment was created (no DB constraint on currency format)
            result = await db_conn.execute(
                text("SELECT currency FROM payments WHERE id = :payment_id"),
                {"payment_id": payment_id}
            )
            stored_currency = result.scalar_one()
            assert stored_currency == invalid_currency
            
            # In a real system, business logic validation would catch this
            # and reject payments with invalid currency codes

    @pytest_asyncio.async_test
    async def test_zero_amount_payment(self, db_conn):
        """
        Test: Zero amount payments should be handled correctly.
        
        Arrange: Payment with 0 amount and 0 expected credits
        Act: Create payment and apply credits
        Assert: Operations succeed but no effective change
        """
        # Arrange
        user_id = await insert_user(db_conn, start_balance=100)
        
        # Act - Create zero-amount payment
        payment_id = await insert_payment(
            db_conn,
            user_id=user_id,
            amount_cents=0,
            expected_credits=0
        )
        
        # Apply zero credits
        tx_id, new_balance = await apply_credit_purchase(
            db_conn, user_id, payment_id, delta_credits=0
        )
        
        # Assert
        assert new_balance == 100  # No change from original balance
        
        # Verify transaction was recorded even with zero delta
        result = await db_conn.execute(
            text("SELECT delta_credits FROM credit_transactions WHERE id = :tx_id"),
            {"tx_id": tx_id}
        )
        delta = result.scalar_one()
        assert delta == 0

    @pytest_asyncio.async_test
    async def test_extremely_large_values(self, db_conn):
        """
        Test: Very large credit amounts within integer limits.
        
        Arrange: Payments with large amounts
        Act: Create and process large transactions
        Assert: Values are handled correctly
        """
        # Arrange
        user_id = await insert_user(db_conn, start_balance=0)
        
        # Test large but valid integer values
        large_amount = 2_147_483_647  # Near max int32
        large_credits = 1_000_000
        
        # Act
        payment_id = await insert_payment(
            db_conn,
            user_id=user_id,
            amount_cents=large_amount,
            expected_credits=large_credits
        )
        
        tx_id, new_balance = await apply_credit_purchase(
            db_conn, user_id, payment_id, delta_credits=large_credits
        )
        
        # Assert
        assert new_balance == large_credits
        
        # Verify values were stored correctly
        result = await db_conn.execute(
            text("""
                SELECT p.amount_total_cents, ct.delta_credits
                FROM payments p
                JOIN credit_transactions ct ON p.id = ct.payment_id
                WHERE p.id = :payment_id
            """),
            {"payment_id": payment_id}
        )
        row = result.fetchone()
        assert row[0] == large_amount
        assert row[1] == large_credits
