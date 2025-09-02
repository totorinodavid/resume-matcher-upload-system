#!/usr/bin/env node

/**
 * Resume Matcher Credit System Setup Script
 * 
 * This script sets up Stripe products and prices for the credit system.
 * Run this after installing the Stripe CLI and configuring your API keys.
 * 
 * Usage:
 * node scripts/setup-stripe.js
 * 
 * Environment Variables Required:
 * - STRIPE_SECRET_KEY: Your Stripe secret key
 */

// Load environment variables
require('dotenv').config();

// Initialize Stripe with current API version and best practices
const stripe = require('stripe')(process.env.STRIPE_SECRET_KEY, {
  apiVersion: '2024-06-20',
  typescript: false,
  maxNetworkRetries: 3,
  timeout: 80000
});

// Credit packages optimized for Resume Matcher use cases
// Based on typical usage: Resume Analysis (10 credits), Job Matching (5 credits), Resume Improvement (15 credits)
const CREDIT_PACKAGES = [
  {
    id: 'starter',
    name: 'Starter Pack',
    description: 'Perfect for trying Resume Matcher - analyze 10 resumes',
    credits: 100,
    priceInCents: 500, // €5.00 - 5 cents per credit
    currency: 'eur',
    metadata: {
      package_type: 'starter',
      credits_per_euro: '20',
      typical_usage: '10 resume analyses',
      cost_efficiency: 'standard'
    }
  },
  {
    id: 'pro',
    name: 'Pro Pack',
    description: 'Great for job seekers - analyze 50 resumes with improvements',
    credits: 500,
    priceInCents: 2000, // €20.00 - 4 cents per credit (20% discount)
    currency: 'eur',
    metadata: {
      package_type: 'professional',
      credits_per_euro: '25',
      typical_usage: '33 complete resume optimizations',
      discount: '20% vs starter',
      cost_efficiency: 'good'
    }
  },
  {
    id: 'business',
    name: 'Business Pack',
    description: 'Ideal for professionals and HR - analyze 100+ resumes',
    credits: 1000,
    priceInCents: 3500, // €35.00 - 3.5 cents per credit (30% discount)
    currency: 'eur',
    metadata: {
      package_type: 'business',
      credits_per_euro: '28.57',
      typical_usage: '100 resume analyses or 66 complete optimizations',
      discount: '30% vs starter',
      cost_efficiency: 'better'
    }
  },
  {
    id: 'enterprise',
    name: 'Enterprise Pack',
    description: 'For teams and agencies - unlimited possibilities',
    credits: 2500,
    priceInCents: 7500, // €75.00 - 3 cents per credit (40% discount)
    currency: 'eur',
    metadata: {
      package_type: 'enterprise',
      credits_per_euro: '33.33',
      typical_usage: '250 resume analyses or 166 complete optimizations',
      discount: '40% vs starter',
      cost_efficiency: 'best'
    }
  }
];

async function setupStripeProducts() {
  console.log('🚀 Setting up Resume Matcher Credit System in Stripe...\n');

  if (!process.env.STRIPE_SECRET_KEY) {
    console.error('❌ Error: STRIPE_SECRET_KEY environment variable is required');
    console.log('Please set your Stripe secret key:');
    console.log('export STRIPE_SECRET_KEY=sk_test_...');
    process.exit(1);
  }

  // Validate API key format
  const secretKey = process.env.STRIPE_SECRET_KEY;
  if (!secretKey.startsWith('sk_test_') && !secretKey.startsWith('sk_live_')) {
    console.error('❌ Error: Invalid Stripe secret key format');
    console.log('Expected format: sk_test_... or sk_live_...');
    process.exit(1);
  }

  const isLiveMode = secretKey.startsWith('sk_live_');
  if (isLiveMode) {
    console.log('⚠️  WARNING: You are using a LIVE mode key!');
    console.log('   This will create real products and prices in your live Stripe account.');
    console.log('   Press Ctrl+C to cancel, or wait 5 seconds to continue...\n');
    await new Promise(resolve => setTimeout(resolve, 5000));
  }

  const results = [];

  try {
    // Test API connection with account retrieval
    console.log('🔗 Testing Stripe API connection...');
    const account = await stripe.accounts.retrieve();
    console.log(`✅ Connected to Stripe account: ${account.email || account.id}`);
    console.log(`   Mode: ${isLiveMode ? 'LIVE' : 'TEST'}`);
    console.log(`   Country: ${account.country || 'Unknown'}\n`);

    // Create main product for Resume Matcher Credits
    console.log('📦 Creating main product...');
    const product = await stripe.products.create({
      name: 'Resume Matcher Credits',
      description: 'Credits for Resume Matcher premium features including ATS analysis, job matching, and resume improvements.',
      metadata: {
        type: 'credits',
        system: 'resume-matcher',
        version: '1.0',
        created_by: 'setup-script',
        supported_features: 'resume_analysis,job_matching,resume_improvement'
      },
      // Mark as active for immediate use
      active: true,
      // Add feature-specific metadata for better organization
      unit_label: 'credit'
    });
    console.log(`✅ Product created: ${product.id}`);

    // Create prices for each package with comprehensive metadata
    for (const pkg of CREDIT_PACKAGES) {
      console.log(`💰 Creating price for ${pkg.name}...`);
      
      const price = await stripe.prices.create({
        product: product.id,
        unit_amount: pkg.priceInCents,
        currency: pkg.currency,
        metadata: {
          // Core package information
          package_id: pkg.id,
          credits: pkg.credits.toString(),
          cost_per_credit: (pkg.priceInCents / pkg.credits).toFixed(4),
          description: pkg.description,
          
          // Billing and usage metadata
          ...pkg.metadata,
          
          // Technical metadata for webhook processing
          webhook_data: JSON.stringify({
            credits: pkg.credits,
            package_type: pkg.id
          })
        },
        // Ensure immediate availability
        active: true,
        // Add tax behavior (most EU businesses need this)
        tax_behavior: 'exclusive'
      });

      results.push({
        package: pkg,
        priceId: price.id,
        productId: product.id
      });

      console.log(`✅ Price created: ${price.id}`);
      console.log(`   ${pkg.credits} credits for €${(pkg.priceInCents/100).toFixed(2)} (${(pkg.priceInCents/pkg.credits).toFixed(2)}¢/credit)`);
    }

    // Display results and comprehensive setup instructions
    console.log('\n🎉 Stripe setup completed successfully!\n');
    
    console.log('📋 Add these environment variables to your .env.local:');
    console.log('=' .repeat(70));
    console.log(`NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=${secretKey.replace('sk_', 'pk_')}`);
    console.log(`STRIPE_SECRET_KEY=${secretKey}`);
    console.log(`STRIPE_PRODUCT_ID=${results[0].productId}`);
    results.forEach((result, index) => {
      const varNames = ['STARTER', 'PRO', 'BUSINESS', 'ENTERPRISE'];
      console.log(`NEXT_PUBLIC_STRIPE_PRICE_${varNames[index]}=${result.priceId}`);
    });
    console.log('=' .repeat(70));

    console.log('\n📝 Update your Prisma database with these SQL commands:');
    console.log('=' .repeat(70));
    results.forEach(result => {
      console.log(`INSERT INTO "Price" (stripe_price_id, credits_per_unit, price_in_cents, currency, active)`);
      console.log(`VALUES ('${result.priceId}', ${result.package.credits}, ${result.package.priceInCents}, '${result.package.currency}', true)`);
      console.log(`ON CONFLICT (stripe_price_id) DO UPDATE SET`);
      console.log(`  credits_per_unit = ${result.package.credits},`);
      console.log(`  price_in_cents = ${result.package.priceInCents},`);
      console.log(`  active = true;\n`);
    });
    console.log('=' .repeat(70));

    console.log('\n🔗 Next steps:');
    console.log('1. Add the environment variables above to your .env.local file');
    console.log('2. Update your database with the SQL commands above');
    console.log('3. Set up webhook endpoint in Stripe Dashboard:');
    console.log(`   - URL: https://your-domain.com/api/stripe/webhook`);
    console.log(`   - Events: checkout.session.completed, checkout.session.async_payment_succeeded`);
    console.log(`   - Events: payment_intent.succeeded, charge.dispute.created`);
    console.log('4. Add your webhook secret to STRIPE_WEBHOOK_SECRET environment variable');
    console.log('5. Test the integration in development mode');

    console.log('\n🧪 Test locally with Stripe CLI:');
    console.log('stripe listen --forward-to localhost:3000/api/stripe/webhook');
    console.log('stripe trigger checkout.session.completed');

    console.log('\n📊 Credit Package Summary:');
    console.log('=' .repeat(70));
    results.forEach(result => {
      const pkg = result.package;
      const costPerCredit = pkg.priceInCents / pkg.credits;
      console.log(`${pkg.name}:`);
      console.log(`  💰 €${(pkg.priceInCents/100).toFixed(2)} for ${pkg.credits} credits`);
      console.log(`  📈 ${costPerCredit.toFixed(2)}¢ per credit`);
      console.log(`  📋 ${pkg.metadata.typical_usage}`);
      console.log(`  🏷️  Stripe Price ID: ${result.priceId}\n`);
    });

  } catch (error) {
    console.error('❌ Error setting up Stripe:', error.message);
    
    if (error.code === 'authentication_required') {
      console.log('\nPlease check your STRIPE_SECRET_KEY is correct and has the right permissions.');
    } else if (error.type === 'StripeAPIError') {
      console.log(`\nStripe API Error: ${error.message}`);
      console.log(`Error Code: ${error.code}`);
    }
    
    process.exit(1);
  }
}

// Run the setup
setupStripeProducts().catch(console.error);
