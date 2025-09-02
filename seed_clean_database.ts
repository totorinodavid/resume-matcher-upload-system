import { PrismaClient } from '@prisma/client'

const prisma = new PrismaClient()

async function seedDatabase() {
  console.log('🌱 Seeding Resume Matcher Next.js Database...')
  console.log('='.repeat(50))
  
  try {
    // Clear existing data
    console.log('🧹 Clearing existing data...')
    await prisma.webhookEvent.deleteMany()
    await prisma.jobAnalysis.deleteMany()
    await prisma.resume.deleteMany()
    await prisma.creditTransaction.deleteMany()
    await prisma.price.deleteMany()
    await prisma.user.deleteMany()
    
    // Create pricing tiers
    console.log('💰 Creating pricing tiers...')
    
    const prices = await prisma.price.createMany({
      data: [
        {
          stripePriceId: 'price_starter_100', // Replace with real Stripe price IDs
          name: 'Starter',
          creditsPerUnit: 100,
          priceInCents: 500, // €5.00
          currency: 'eur',
          active: true,
          isPopular: false,
        },
        {
          stripePriceId: 'price_pro_500', // Replace with real Stripe price IDs
          name: 'Pro',
          creditsPerUnit: 500,
          priceInCents: 2000, // €20.00
          currency: 'eur',
          active: true,
          isPopular: true, // Most popular
        },
        {
          stripePriceId: 'price_premium_1000', // Replace with real Stripe price IDs
          name: 'Premium',
          creditsPerUnit: 1000,
          priceInCents: 3500, // €35.00 (30% discount from 5000)
          currency: 'eur',
          active: true,
          isPopular: false,
          discount: 30, // 30% off
        }
      ]
    })
    
    console.log(`✅ Created ${prices.count} pricing tiers`)
    
    // Create demo user (optional)
    console.log('👤 Creating demo user...')
    
    const demoUser = await prisma.user.create({
      data: {
        email: 'demo@resumematcher.ai',
        name: 'Demo User', 
        credits: 50, // Welcome bonus
        welcomeBonusGiven: true,
      }
    })
    
    // Give demo user welcome bonus transaction
    await prisma.creditTransaction.create({
      data: {
        userId: demoUser.id,
        delta: 50,
        reason: 'welcome_bonus',
        metadata: {
          note: 'Welcome to Resume Matcher! Enjoy 50 free credits.',
          automated: true,
        }
      }
    })
    
    console.log(`✅ Created demo user: ${demoUser.email} with 50 credits`)
    
    // Verify setup
    const totalUsers = await prisma.user.count()
    const totalPrices = await prisma.price.count()
    const totalCredits = await prisma.user.aggregate({
      _sum: { credits: true }
    })
    
    console.log('')
    console.log('📊 Database Summary:')
    console.log(`- Users: ${totalUsers}`)
    console.log(`- Active Prices: ${totalPrices}`)
    console.log(`- Total Credits in System: ${totalCredits._sum.credits}`)
    console.log('')
    
    // Display pricing info
    const allPrices = await prisma.price.findMany({
      where: { active: true },
      orderBy: { priceInCents: 'asc' }
    })
    
    console.log('💸 Available Credit Packages:')
    allPrices.forEach(price => {
      const priceEur = (price.priceInCents / 100).toFixed(2)
      const popular = price.isPopular ? ' 🔥 POPULAR' : ''
      const discount = price.discount ? ` (${price.discount}% OFF)` : ''
      console.log(`- ${price.name}: €${priceEur} → ${price.creditsPerUnit} credits${discount}${popular}`)
    })
    
    console.log('')
    console.log('🎉 Database seeded successfully!')
    console.log('🚀 Ready to start Next.js Resume Matcher!')
    
  } catch (error) {
    console.error('❌ Seeding failed:', error)
    throw error
  } finally {
    await prisma.$disconnect()
  }
}

// Credit costs reference
const CREDIT_COSTS = {
  RESUME_ANALYSIS: 10,      // Full resume analysis
  JOB_MATCH: 5,             // Job description matching
  SKILL_EXTRACTION: 3,      // Extract skills from text
  ATS_OPTIMIZATION: 8,      // ATS compatibility check
  COVER_LETTER_GEN: 12,     // Generate cover letter
}

console.log('💡 Credit Usage Reference:')
Object.entries(CREDIT_COSTS).forEach(([action, cost]) => {
  console.log(`- ${action.replace(/_/g, ' ')}: ${cost} credits`)
})
console.log('')

// Execute seeding
if (require.main === module) {
  seedDatabase()
    .then(() => {
      console.log('✨ Seeding complete!')
      process.exit(0)
    })
    .catch((error) => {
      console.error('💥 Seeding failed:', error)
      process.exit(1)
    })
}

export { seedDatabase, CREDIT_COSTS }
