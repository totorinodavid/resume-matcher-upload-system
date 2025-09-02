#!/usr/bin/env node

/**
 * Insert Stripe Price Data into Database
 * This script adds the newly created Stripe prices to the database
 */

const { PrismaClient } = require('@prisma/client');

const prisma = new PrismaClient();

const priceData = [
  {
    stripePriceId: 'price_1S2vWOEPwuWwkzKTTYW2QNMN',
    creditsPerUnit: 100,
    priceInCents: 500,
    currency: 'eur',
    active: true
  },
  {
    stripePriceId: 'price_1S2vWPEPwuWwkzKTPwUwNUWx',
    creditsPerUnit: 500,
    priceInCents: 2000,
    currency: 'eur',
    active: true
  },
  {
    stripePriceId: 'price_1S2vWPEPwuWwkzKTOM5Bywim',
    creditsPerUnit: 1000,
    priceInCents: 3500,
    currency: 'eur',
    active: true
  },
  {
    stripePriceId: 'price_1S2vWPEPwuWwkzKTYN57r165',
    creditsPerUnit: 2500,
    priceInCents: 7500,
    currency: 'eur',
    active: true
  }
];

async function insertPriceData() {
  console.log('📊 Inserting Stripe price data into database...\n');

  try {
    for (const price of priceData) {
      console.log(`💰 Adding price: ${price.creditsPerUnit} credits for €${price.priceInCents/100}...`);
      
      const result = await prisma.price.upsert({
        where: { stripePriceId: price.stripePriceId },
        update: {
          creditsPerUnit: price.creditsPerUnit,
          priceInCents: price.priceInCents,
          currency: price.currency,
          active: price.active
        },
        create: price
      });
      
      console.log(`   ✓ Price ID: ${result.stripePriceId}`);
    }

    console.log('\n🎉 All price data inserted successfully!');
    
    // Verify the data
    console.log('\n📋 Verifying database contents:');
    const allPrices = await prisma.price.findMany({
      orderBy: { creditsPerUnit: 'asc' }
    });

    allPrices.forEach(price => {
      console.log(`   📦 ${price.creditsPerUnit} credits: €${price.priceInCents/100} (${price.stripePriceId})`);
    });

  } catch (error) {
    console.error('❌ Error inserting price data:', error);
    process.exit(1);
  } finally {
    await prisma.$disconnect();
  }
}

insertPriceData().catch(console.error);
