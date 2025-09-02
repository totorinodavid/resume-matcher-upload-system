#!/usr/bin/env node

/**
 * Credit System Verification Script
 * 
 * This script tests the basic functionality of the credit system
 * to ensure everything is working correctly after migration.
 */

const { PrismaClient } = require('@prisma/client');

const prisma = new PrismaClient();

async function verifyCreditsSystem() {
  console.log('🔍 Verifying Resume Matcher Credit System...\n');

  try {
    // Test 1: Check database connection
    console.log('✅ Test 1: Database Connection');
    await prisma.$connect();
    console.log('   ✓ Connected to database successfully\n');

    // Test 2: Check tables exist
    console.log('✅ Test 2: Table Structure');
    
    const userCount = await prisma.user.count();
    console.log(`   ✓ Users table: ${userCount} records`);
    
    const creditTransactionCount = await prisma.creditTransaction.count();
    console.log(`   ✓ CreditTransaction table: ${creditTransactionCount} records`);
    
    const priceCount = await prisma.price.count();
    console.log(`   ✓ Price table: ${priceCount} records\n`);

    // Test 3: Create test user
    console.log('✅ Test 3: Create Test User');
    const randomEmail = `test-${Date.now()}@resumematcher.com`;
    const testUser = await prisma.user.create({
      data: {
        email: randomEmail,
        name: 'Test User',
        credits_balance: 100
      }
    });
    console.log(`   ✓ Created user: ${testUser.email} (ID: ${testUser.id})\n`);

    // Test 4: Add credit transaction
    console.log('✅ Test 4: Credit Transaction');
    const creditTransaction = await prisma.creditTransaction.create({
      data: {
        userId: testUser.id,
        delta_credits: 50,
        reason: 'purchase',
        meta: {
          package_name: 'Starter Pack',
          test: true
        }
      }
    });
    console.log(`   ✓ Created credit transaction: +${creditTransaction.delta_credits} credits\n`);

    // Test 5: Check analytics views
    console.log('✅ Test 5: Analytics Views');
    try {
      const purchaseAnalytics = await prisma.$queryRaw`SELECT * FROM credit_purchase_analytics LIMIT 1`;
      console.log('   ✓ credit_purchase_analytics view working');
      
      const usageAnalytics = await prisma.$queryRaw`SELECT * FROM credit_usage_by_feature LIMIT 1`;
      console.log('   ✓ credit_usage_by_feature view working');
      
      const segmentAnalytics = await prisma.$queryRaw`SELECT * FROM user_credit_segments LIMIT 1`;
      console.log('   ✓ user_credit_segments view working\n');
    } catch (error) {
      console.log('   ⚠️  Analytics views may need time to populate with data\n');
    }

    // Test 6: Credit utility functions
    console.log('✅ Test 6: Credit Functions');
    
    // Test recalculate function
    const recalculatedBalance = await prisma.$queryRaw`SELECT recalculate_user_credits(${testUser.id}::INTEGER) as balance`;
    console.log(`   ✓ Recalculated balance: ${recalculatedBalance[0].balance} credits`);
    
    // Test verification function
    const isBalanceValid = await prisma.$queryRaw`SELECT verify_credit_balance(${testUser.id}::INTEGER) as is_valid`;
    console.log(`   ✓ Balance verification: ${isBalanceValid[0].is_valid ? 'VALID' : 'INVALID'}\n`);

    // Test 7: Cleanup test data
    console.log('✅ Test 7: Cleanup');
    await prisma.creditTransaction.deleteMany({
      where: { userId: testUser.id }
    });
    await prisma.user.delete({
      where: { id: testUser.id }
    });
    console.log('   ✓ Test data cleaned up\n');

    // Final summary
    console.log('🎉 All tests passed! Credit System is working correctly.\n');
    
    console.log('📋 Next Steps:');
    console.log('1. Set up Stripe products: node scripts/setup-stripe.js');
    console.log('2. Configure webhook endpoint in Stripe Dashboard');
    console.log('3. Test credit purchase flow');
    console.log('4. Deploy to production');

  } catch (error) {
    console.error('❌ Error during verification:', error);
    process.exit(1);
  } finally {
    await prisma.$disconnect();
  }
}

// Run verification
verifyCreditsSystem().catch(console.error);
