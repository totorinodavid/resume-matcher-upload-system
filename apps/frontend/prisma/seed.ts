import { PrismaClient } from '@prisma/client'
import { CREDIT_PACKAGES } from '../lib/utils/credits'

const prisma = new PrismaClient()

async function main() {
  console.log('🌱 Seeding Resume Matcher Credit System...')

  // Seed Price data from our credit packages
  for (const pkg of CREDIT_PACKAGES) {
    await prisma.price.upsert({
      where: { stripePriceId: pkg.stripePriceId },
      update: {
        creditsPerUnit: pkg.credits,
        priceInCents: pkg.priceInCents,
        active: true,
      },
      create: {
        stripePriceId: pkg.stripePriceId,
        creditsPerUnit: pkg.credits,
        priceInCents: pkg.priceInCents,
        currency: 'eur',
        active: true,
      },
    })
    
    console.log(`✅ Seeded price: ${pkg.name} (${pkg.credits} credits, €${pkg.priceInCents / 100})`)
  }

  console.log('🎉 Seeding completed!')
}

main()
  .then(async () => {
    await prisma.$disconnect()
  })
  .catch(async (e) => {
    console.error('❌ Seeding failed:', e)
    await prisma.$disconnect()
    process.exit(1)
  })
