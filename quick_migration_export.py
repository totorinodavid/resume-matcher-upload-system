#!/usr/bin/env python3
"""
Quick Migration Export
"""

import asyncio
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from sqlalchemy import text

sys.path.append(os.getcwd())
sys.path.append(os.path.join(os.getcwd(), 'apps', 'backend'))

async def quick_export():
    migration_dir = Path('migration_data')
    migration_dir.mkdir(exist_ok=True)
    
    from app.core.database import get_async_session_local
    session_factory = get_async_session_local()
    
    async with session_factory() as session:
        # Users with credits
        users_result = await session.execute(text('SELECT id, email, name, credits_balance FROM users WHERE credits_balance > 0'))
        users_data = [dict(row._mapping) for row in users_result]
        
        # All payments
        payments_result = await session.execute(text('SELECT id, user_id, provider_payment_intent_id, amount_total_cents, expected_credits, status, created_at FROM payments'))
        payments_data = [dict(row._mapping) for row in payments_result]
        
        # All transactions
        transactions_result = await session.execute(text('SELECT id, user_id, delta_credits, reason, payment_id, admin_action_id, meta, created_at FROM credit_transactions'))
        transactions_data = [dict(row._mapping) for row in transactions_result]
        
        # Stats
        stats_result = await session.execute(text('SELECT COUNT(*) as total_users, SUM(COALESCE(credits_balance, 0)) as total_credits FROM users'))
        stats = dict(stats_result.first()._mapping)
        
        # Save exports
        with open(migration_dir / 'users_export.json', 'w') as f:
            json.dump(users_data, f, indent=2, default=str)
        
        with open(migration_dir / 'payments_export.json', 'w') as f:
            json.dump(payments_data, f, indent=2, default=str)
            
        with open(migration_dir / 'transactions_export.json', 'w') as f:
            json.dump(transactions_data, f, indent=2, default=str)
        
        summary = {
            'export_timestamp': datetime.now().isoformat(),
            'users_exported': len(users_data),
            'payments_exported': len(payments_data),
            'transactions_exported': len(transactions_data),
            'total_users': stats['total_users'],
            'total_credits': stats['total_credits']
        }
        
        with open(migration_dir / 'export_summary.json', 'w') as f:
            json.dump(summary, f, indent=2, default=str)
        
        print(f'✅ Migration data exported:')
        print(f'   - Users with credits: {len(users_data)}')
        print(f'   - Total payments: {len(payments_data)}')
        print(f'   - Total transactions: {len(transactions_data)}')
        print(f'   - Total credits: {stats["total_credits"]}')
        print(f'   - Saved to: {migration_dir}')
        
        return summary

if __name__ == "__main__":
    asyncio.run(quick_export())
