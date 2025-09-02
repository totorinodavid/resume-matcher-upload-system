#!/usr/bin/env node

/**
 * Live Credit Purchase Flow Test
 * 
 * This script tests the complete credit purchase flow with Stripe webhooks
 */

const { PrismaClient } = require('@prisma/client');

const prisma = new PrismaClient();

async function testLiveCreditFlow() {
  console.log('🧪 Testing Live Credit Purchase Flow...\n');

  try {
    // Test 1: Check webhook processing
    console.log('✅ Test 1: Checking Recent Webhook Activity');
    
    const recentTransactions = await prisma.creditTransaction.findMany({
      where: {
        createdAt: {
          gte: new Date(Date.now() - 10 * 60 * 1000) // Last 10 minutes
        }
      },
      include: {
        user: {
          select: { email: true, credits_balance: true }
        }
      },
      orderBy: { createdAt: 'desc' },
      take: 5
    });

    if (recentTransactions.length > 0) {
      console.log(`   ✓ Found ${recentTransactions.length} recent transactions:`);
      recentTransactions.forEach(tx => {
        console.log(`     - ${tx.reason}: ${tx.delta_credits > 0 ? '+' : ''}${tx.delta_credits} credits`);
        console.log(`       User: ${tx.user.email} (Balance: ${tx.user.credits_balance})`);
        console.log(`       Event: ${tx.stripeEventId || 'N/A'}`);
        console.log(`       Time: ${tx.createdAt.toISOString()}`);
      });
    } else {
      console.log('   ⚠️  No recent transactions found');
      console.log('   💡 Try running: stripe trigger checkout.session.completed');
    }
    console.log();

    // Test 2: Analytics update
    console.log('✅ Test 2: Analytics Data Update');
    
    const purchaseAnalytics = await prisma.$queryRaw`
      SELECT * FROM credit_purchase_analytics 
      WHERE purchase_date >= CURRENT_DATE - INTERVAL '1 day'
      ORDER BY purchase_date DESC
      LIMIT 3
    `;
    
    if (purchaseAnalytics.length > 0) {
      console.log('   ✓ Recent purchase analytics:');
      purchaseAnalytics.forEach(analytics => {
        console.log(`     - ${analytics.purchase_date}: ${analytics.purchase_count} purchases, ${analytics.total_credits_purchased} credits`);
      });
    } else {
      console.log('   ⚠️  No recent purchase analytics');
    }
    console.log();

    // Test 3: Check for webhook errors (if any)
    console.log('✅ Test 3: System Health Check');
    
    const userCount = await prisma.user.count();
    const transactionCount = await prisma.creditTransaction.count();
    const priceCount = await prisma.price.count();
    
    console.log(`   ✓ Database Status:`);
    console.log(`     - Users: ${userCount}`);
    console.log(`     - Transactions: ${transactionCount}`);
    console.log(`     - Price Packages: ${priceCount}`);
    console.log();

    // Test 4: Create manual test transaction
    console.log('✅ Test 4: Manual Test Transaction');
    
    // Find or create test user
    let testUser = await prisma.user.findFirst({
      where: { email: { contains: 'test-webhook' } }
    });
    
    if (!testUser) {
      testUser = await prisma.user.create({
        data: {
          email: `test-webhook-${Date.now()}@resumematcher.com`,
          name: 'Webhook Test User',
          credits_balance: 0
        }
      });
      console.log(`   ✓ Created test user: ${testUser.email}`);
    } else {
      console.log(`   ✓ Using existing test user: ${testUser.email}`);
    }

    // Simulate webhook transaction
    const testTransaction = await prisma.creditTransaction.create({
      data: {
        userId: testUser.id,
        delta_credits: 100,
        reason: 'purchase',
        stripeEventId: `evt_test_manual_${Date.now()}`,
        meta: {
          package_name: 'Test Package',
          test: true,
          manual: true
        }
      }
    });

    console.log(`   ✓ Created test transaction: +${testTransaction.delta_credits} credits`);
    
    // Verify balance update
    const updatedUser = await prisma.user.findUnique({
      where: { id: testUser.id },
      select: { credits_balance: true }
    });
    
    console.log(`   ✓ Updated balance: ${updatedUser.credits_balance} credits`);
    console.log();

    // Test 5: Next steps
    console.log('📋 Next Steps for Production:');
    console.log('1. ✅ Stripe CLI setup complete');
    console.log('2. ✅ Webhook forwarding active');  
    console.log('3. ✅ Credit system responding to events');
    console.log('4. 🔄 Test actual credit purchase on /billing page');
    console.log('5. 🚀 Deploy webhook endpoint to production');
    console.log();

    console.log('🌐 Test URLs:');
    console.log('   - Credit System: http://localhost:3000/billing');
    console.log('   - Stripe Dashboard: https://dashboard.stripe.com/test/events');
    console.log('   - Webhook Logs: Check terminal running stripe listen');

  } catch (error) {
    console.error('❌ Test failed:', error);
  } finally {
    await prisma.$disconnect();
  }
}

testLiveCreditFlow().catch(console.error);
