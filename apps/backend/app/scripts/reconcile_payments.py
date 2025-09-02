#!/usr/bin/env python3
"""
Production reconciliation script for daily payment sync
Run as: python -m app.scripts.reconcile_payments
"""

import asyncio
import logging
import os
import sys
from datetime import datetime

# Add the app directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from app.core.database import SessionLocal
from app.services.reconciliation import ReconciliationService


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('/tmp/reconciliation.log')
    ]
)
logger = logging.getLogger(__name__)


async def main():
    """Main reconciliation process."""
    logger.info("Starting payment reconciliation process")
    start_time = datetime.now()
    
    try:
        reconciliation_service = ReconciliationService()
        
        async with SessionLocal() as session:
            # Run reconciliation with limit to avoid timeout
            stats = await reconciliation_service.reconcile_payments(
                session=session,
                limit=500  # Process max 500 payments per run
            )
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            logger.info(f"Reconciliation completed successfully in {duration:.2f}s")
            logger.info(f"Stats: {stats}")
            
            # Exit with success code
            sys.exit(0)
            
    except Exception as e:
        logger.error(f"Reconciliation failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
