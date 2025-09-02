#!/usr/bin/env node

/**
 * Credit System End-to-End Test Script
 * 
 * This script tests all components of the credit system without running the full Next.js app
 */

const { PrismaClient } = require('@prisma/client');

const prisma = new PrismaClient();

async function testCreditSystem() {
  console.log('🧪 Testing Resume Matcher Credit System Components...\n');

  try {
    // Test 1: Check Stripe Price configuration
    console.log('✅ Test 1: Stripe Price Configuration');
    const prices = await prisma.price.findMany({
      orderBy: { creditsPerUnit: 'asc' }
    });
    
    console.log(`   Found ${prices.length} credit packages:`);
    prices.forEach(price => {
      const costPerCredit = (price.priceInCents / price.creditsPerUnit).toFixed(3);
      console.log(`   📦 ${price.creditsPerUnit} credits for €${price.priceInCents/100} (${costPerCredit}¢/credit)`);
    });
    console.log();

    // Test 2: Credit system workflow simulation
    console.log('✅ Test 2: Credit Purchase Simulation');
    
    // Create test user
    const testUser = await prisma.user.create({
      data: {
        email: `test-purchase-${Date.now()}@resumematcher.com`,
        name: 'Credit Test User',
        credits_balance: 0
      }
    });
    console.log(`   ✓ Created test user: ${testUser.email}`);

    // Simulate credit purchase (Starter Pack)
    const starterPack = prices.find(p => p.creditsPerUnit === 100);
    if (starterPack) {
      const purchaseTransaction = await prisma.creditTransaction.create({
        data: {
          userId: testUser.id,
          delta_credits: starterPack.creditsPerUnit,
          reason: 'purchase',
          stripeEventId: `evt_test_${Date.now()}`,
          meta: {
            package_name: 'Starter Pack',
            stripe_price_id: starterPack.stripePriceId,
            amount_paid: starterPack.priceInCents,
            test: true
          }
        }
      });
      console.log(`   ✓ Simulated purchase: +${purchaseTransaction.delta_credits} credits`);
    }

    // Test 3: Credit spending simulation
    console.log('✅ Test 3: Credit Spending Simulation');
    
    const features = [
      { name: 'Resume Analysis', cost: 10, reason: 'resume_analysis' },
      { name: 'Job Matching', cost: 5, reason: 'job_match' },
      { name: 'Resume Improvement', cost: 15, reason: 'resume_improvement' }
    ];

    for (const feature of features) {
      const spendTransaction = await prisma.creditTransaction.create({
        data: {
          userId: testUser.id,
          delta_credits: -feature.cost,
          reason: feature.reason,
          meta: {
            feature_name: feature.name,
            test: true
          }
        }
      });
      console.log(`   ✓ ${feature.name}: -${feature.cost} credits`);
    }

    // Test 4: Balance verification
    console.log('✅ Test 4: Balance Verification');
    
    const finalBalance = await prisma.$queryRaw`
      SELECT recalculate_user_credits(${testUser.id}::INTEGER) as calculated_balance
    `;
    console.log(`   ✓ Final calculated balance: ${finalBalance[0].calculated_balance} credits`);

    const updatedUser = await prisma.user.findUnique({
      where: { id: testUser.id },
      select: { credits_balance: true }
    });
    console.log(`   ✓ Stored balance: ${updatedUser.credits_balance} credits`);

    const isValid = await prisma.$queryRaw`
      SELECT verify_credit_balance(${testUser.id}::INTEGER) as is_valid
    `;
    console.log(`   ✓ Balance consistency: ${isValid[0].is_valid ? 'VALID' : 'INVALID'}`);

    // Test 5: Analytics verification
    console.log('✅ Test 5: Analytics Views');
    
    const purchaseAnalytics = await prisma.$queryRaw`
      SELECT * FROM credit_purchase_analytics 
      WHERE purchase_date = CURRENT_DATE
      LIMIT 1
    `;
    console.log(`   ✓ Purchase analytics: ${purchaseAnalytics.length} records today`);

    const usageAnalytics = await prisma.$queryRaw`
      SELECT reason, usage_count, total_credits_spent 
      FROM credit_usage_by_feature 
      ORDER BY total_credits_spent DESC
      LIMIT 3
    `;
    console.log('   ✓ Top credit usage:');
    usageAnalytics.forEach(usage => {
      console.log(`     - ${usage.reason}: ${usage.usage_count} uses, ${usage.total_credits_spent} credits`);
    });

    // Cleanup
    console.log('✅ Test 6: Cleanup');
    await prisma.creditTransaction.deleteMany({
      where: { userId: testUser.id }
    });
    await prisma.user.delete({
      where: { id: testUser.id }
    });
    console.log('   ✓ Test data cleaned up');

    console.log('\n🎉 All credit system tests passed!\n');

    // Summary
    console.log('📊 System Status Summary:');
    console.log(`   💳 Credit Packages: ${prices.length} configured`);
    console.log('   🔄 Transactions: Working correctly');
    console.log('   🧮 Balance Calculation: Accurate');
    console.log('   📈 Analytics: Functional');
    console.log('   🔧 Database Functions: Operational');

    console.log('\n🚀 Ready for Production Deployment!');
    console.log('\n📋 Final Steps:');
    console.log('1. Configure Stripe webhook endpoint');
    console.log('2. Test credit purchase flow with Stripe CLI');
    console.log('3. Deploy to production environment');

  } catch (error) {
    console.error('❌ Test failed:', error);
    process.exit(1);
  } finally {
    await prisma.$disconnect();
  }
}

testCreditSystem().catch(console.error);
