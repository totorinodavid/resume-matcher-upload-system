#!/usr/bin/env node

/**
 * Insert Stripe Price Data Script
 * 
 * This script inserts the created Stripe price IDs into the database.
 */

require('dotenv').config();
const { PrismaClient } = require('@prisma/client');

const prisma = new PrismaClient();

async function insertStripePrices() {
  console.log('💾 Inserting Stripe price data into database...\n');

  try {
    const priceData = [
      {
        stripePriceId: 'price_1S2v9EEPwuWwkzKTWctV6b8H',
        creditsPerUnit: 100,
        priceInCents: 500,
        currency: 'eur',
        active: true,
        name: 'Starter Pack',
        description: '10 resume analyses or 20 job matches'
      },
      {
        stripePriceId: 'price_1S2v9EEPwuWwkzKTozEzxD1f',
        creditsPerUnit: 500,
        priceInCents: 2000,
        currency: 'eur',
        active: true,
        name: 'Pro Pack',
        description: '50 resume analyses + improvements'
      },
      {
        stripePriceId: 'price_1S2v9FEPwuWwkzKTygApOQqp',
        creditsPerUnit: 1200,
        priceInCents: 3500,
        currency: 'eur',
        active: true,
        name: 'Premium Pack',
        description: 'Everything included with 20% bonus'
      }
    ];

    for (const price of priceData) {
      const result = await prisma.price.upsert({
        where: { stripePriceId: price.stripePriceId },
        update: {
          creditsPerUnit: price.creditsPerUnit,
          priceInCents: price.priceInCents,
          currency: price.currency,
          active: price.active,
          name: price.name,
          description: price.description
        },
        create: price
      });

      console.log(`✅ ${price.name}: ${price.creditsPerUnit} credits for €${(price.priceInCents / 100).toFixed(2)}`);
    }

    console.log('\n🎉 All Stripe price data inserted successfully!');
    
    // Verify the data
    const allPrices = await prisma.price.findMany({
      orderBy: { priceInCents: 'asc' }
    });
    
    console.log('\n📋 Current price packages in database:');
    allPrices.forEach(price => {
      console.log(`   ${price.name}: ${price.creditsPerUnit} credits for €${(price.priceInCents / 100).toFixed(2)} (${price.stripePriceId})`);
    });

  } catch (error) {
    console.error('❌ Error inserting price data:', error);
    process.exit(1);
  } finally {
    await prisma.$disconnect();
  }
}

// Run the insertion
insertStripePrices().catch(console.error);
