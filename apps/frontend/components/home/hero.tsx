"use client";

import React from 'react';
import { useTranslations } from 'next-intl';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import type { Session } from 'next-auth';
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { CheckCircle, Upload, Zap, Target, Star, ArrowRight, Users, TrendingUp } from "lucide-react";
import Image from "next/image";

export default function Hero({ session }: { session: Session | null }) {
	const t = useTranslations('Hero');
	const pathname = usePathname();
	const parts = pathname.split('/').filter(Boolean);
	const locale = parts[0] || 'en';
	const ctaLink = session ? `/${locale}/resume` : `/${locale}/login`;

	return (
		<div className="min-h-screen bg-background">
			{/* Header */}
			<header className="border-b border-border bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60 sticky top-0 z-50">
				<div className="container mx-auto px-4 sm:px-6 lg:px-8">
					<div className="flex h-16 items-center justify-between">
						<div className="flex items-center space-x-2">
							<div className="w-8 h-8 bg-primary rounded-lg flex items-center justify-center">
								<span className="font-mono font-bold text-primary-foreground text-sm">RM</span>
							</div>
							<span className="font-mono font-bold text-xl text-foreground">{t('title')}</span>
						</div>
						<nav className="hidden md:flex items-center space-x-8">
							<a href="#features" className="text-muted-foreground hover:text-foreground transition-colors">
								Features
							</a>
							<a href="#how-it-works" className="text-muted-foreground hover:text-foreground transition-colors">
								How it Works
							</a>
							<a href="#testimonials" className="text-muted-foreground hover:text-foreground transition-colors">
								Reviews
							</a>
						</nav>
						<div className="flex items-center space-x-4">
							{!session && (
								<Button variant="ghost" className="hidden sm:inline-flex" asChild>
									<Link href={`/${locale}/login`}>Sign In</Link>
								</Button>
							)}
							<Button className="bg-primary hover:bg-primary/90 text-primary-foreground" asChild>
								<Link href={ctaLink}>Get Started</Link>
							</Button>
						</div>
					</div>
				</div>
			</header>

			{/* Hero Section */}
			<section className="py-20 lg:py-32 bg-gradient-to-br from-background via-card to-background">
				<div className="container mx-auto px-4 sm:px-6 lg:px-8">
					<div className="text-center max-w-4xl mx-auto">
						<Badge className="mb-6 bg-secondary/10 text-secondary border-secondary/20 hover:bg-secondary/20">
							<Zap className="w-3 h-3 mr-1" />
							AI-Powered Resume Optimization
						</Badge>
						<h1 className="font-mono font-bold text-4xl sm:text-5xl lg:text-6xl text-balance mb-6">
							Elevate Your Resume, <span className="text-primary">Ace the ATS</span>
						</h1>
						<p className="text-xl text-muted-foreground text-balance mb-8 max-w-2xl mx-auto leading-relaxed">
							{t('tagline')} Our AI analyzes your resume against ATS systems and gives you actionable insights to land more interviews.
						</p>
						<div className="flex flex-col sm:flex-row gap-4 justify-center items-center mb-12">
							<Button size="lg" className="bg-primary hover:bg-primary/90 text-primary-foreground px-8 py-3 text-lg" asChild>
								<Link href={ctaLink}>
									<Upload className="w-5 h-5 mr-2" />
									Upload Your Resume
								</Link>
							</Button>
							<Button size="lg" variant="outline" className="px-8 py-3 text-lg bg-transparent">
								See Demo
								<ArrowRight className="w-5 h-5 ml-2" />
							</Button>
						</div>

						{/* Stats */}
						<div className="grid grid-cols-1 sm:grid-cols-3 gap-8 max-w-2xl mx-auto">
							<div className="text-center">
								<div className="font-mono font-bold text-3xl text-primary mb-2">94%</div>
								<div className="text-sm text-muted-foreground">ATS Pass Rate</div>
							</div>
							<div className="text-center">
								<div className="font-mono font-bold text-3xl text-primary mb-2">2.5x</div>
								<div className="text-sm text-muted-foreground">More Interviews</div>
							</div>
							<div className="text-center">
								<div className="font-mono font-bold text-3xl text-primary mb-2">50K+</div>
								<div className="text-sm text-muted-foreground">Resumes Optimized</div>
							</div>
						</div>
					</div>
				</div>
			</section>

			{/* How It Works */}
			<section id="how-it-works" className="py-20 bg-muted/30">
				<div className="container mx-auto px-4 sm:px-6 lg:px-8">
					<div className="text-center mb-16">
						<h2 className="font-mono font-bold text-3xl lg:text-4xl text-balance mb-4">
							Get ATS-Ready in <span className="text-primary">3 Simple Steps</span>
						</h2>
						<p className="text-xl text-muted-foreground max-w-2xl mx-auto text-balance">
							Our AI does the heavy lifting so you can focus on landing your dream job
						</p>
					</div>

					<div className="grid md:grid-cols-3 gap-8 max-w-5xl mx-auto">
						<Card className="text-center border-2 hover:border-primary/20 transition-colors">
							<CardHeader>
								<div className="w-16 h-16 bg-primary/10 rounded-full flex items-center justify-center mx-auto mb-4">
									<Upload className="w-8 h-8 text-primary" />
								</div>
								<CardTitle className="font-mono text-xl">Upload Resume</CardTitle>
								<CardDescription>Drop your resume and we'll scan it instantly</CardDescription>
							</CardHeader>
						</Card>

						<Card className="text-center border-2 hover:border-primary/20 transition-colors">
							<CardHeader>
								<div className="w-16 h-16 bg-secondary/10 rounded-full flex items-center justify-center mx-auto mb-4">
									<Target className="w-8 h-8 text-secondary" />
								</div>
								<CardTitle className="font-mono text-xl">AI Analysis</CardTitle>
								<CardDescription>Get your ATS score and detailed feedback</CardDescription>
							</CardHeader>
						</Card>

						<Card className="text-center border-2 hover:border-primary/20 transition-colors">
							<CardHeader>
								<div className="w-16 h-16 bg-primary/10 rounded-full flex items-center justify-center mx-auto mb-4">
									<TrendingUp className="w-8 h-8 text-primary" />
								</div>
								<CardTitle className="font-mono text-xl">Optimize & Win</CardTitle>
								<CardDescription>Apply our suggestions and land more interviews</CardDescription>
							</CardHeader>
						</Card>
					</div>
				</div>
			</section>

			{/* Features */}
			<section id="features" className="py-20">
				<div className="container mx-auto px-4 sm:px-6 lg:px-8">
					<div className="text-center mb-16">
						<h2 className="font-mono font-bold text-3xl lg:text-4xl text-balance mb-4">
							Why Job Seekers Choose <span className="text-primary">Resume Matcher</span>
						</h2>
						<p className="text-xl text-muted-foreground max-w-2xl mx-auto text-balance">
							Built for the modern job seeker who wants results, not fluff
						</p>
					</div>

					<div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
						<Card className="border-2 hover:border-primary/20 transition-all hover:shadow-lg">
							<CardHeader>
								<CheckCircle className="w-10 h-10 text-primary mb-4" />
								<CardTitle className="font-mono">Instant ATS Score</CardTitle>
								<CardDescription>
									Know exactly how ATS-friendly your resume is with our proprietary scoring algorithm
								</CardDescription>
							</CardHeader>
						</Card>

						<Card className="border-2 hover:border-primary/20 transition-all hover:shadow-lg">
							<CardHeader>
								<Zap className="w-10 h-10 text-secondary mb-4" />
								<CardTitle className="font-mono">Smart Suggestions</CardTitle>
								<CardDescription>
									Get personalized recommendations to improve keywords, formatting, and content
								</CardDescription>
							</CardHeader>
						</Card>

						<Card className="border-2 hover:border-primary/20 transition-all hover:shadow-lg">
							<CardHeader>
								<Target className="w-10 h-10 text-primary mb-4" />
								<CardTitle className="font-mono">Job-Specific Optimization</CardTitle>
								<CardDescription>Tailor your resume for specific job postings and industries</CardDescription>
							</CardHeader>
						</Card>

						<Card className="border-2 hover:border-primary/20 transition-all hover:shadow-lg">
							<CardHeader>
								<Users className="w-10 h-10 text-secondary mb-4" />
								<CardTitle className="font-mono">Real-Time Analysis</CardTitle>
								<CardDescription>Get instant feedback as you make changes to your resume</CardDescription>
							</CardHeader>
						</Card>

						<Card className="border-2 hover:border-primary/20 transition-all hover:shadow-lg">
							<CardHeader>
								<TrendingUp className="w-10 h-10 text-primary mb-4" />
								<CardTitle className="font-mono">Progress Tracking</CardTitle>
								<CardDescription>Monitor your improvement over time and see your success rate increase</CardDescription>
							</CardHeader>
						</Card>

						<Card className="border-2 hover:border-primary/20 transition-all hover:shadow-lg">
							<CardHeader>
								<Star className="w-10 h-10 text-secondary mb-4" />
								<CardTitle className="font-mono">Industry Insights</CardTitle>
								<CardDescription>Access proven strategies optimized for your field</CardDescription>
							</CardHeader>
						</Card>
					</div>
				</div>
			</section>

			{/* Testimonials */}
			<section id="testimonials" className="py-20 bg-muted/30">
				<div className="container mx-auto px-4 sm:px-6 lg:px-8">
					<div className="text-center mb-16">
						<h2 className="font-mono font-bold text-3xl lg:text-4xl text-balance mb-4">
							Real Results from <span className="text-primary">Real People</span>
						</h2>
						<p className="text-xl text-muted-foreground max-w-2xl mx-auto text-balance">
							Join thousands of professionals who've leveled up their careers
						</p>
					</div>

					<div className="grid md:grid-cols-3 gap-8 max-w-6xl mx-auto">
						<Card className="border-2">
							<CardHeader>
								<div className="flex items-center space-x-1 mb-4">
									{[...Array(5)].map((_, i) => (
										<Star key={i} className="w-4 h-4 fill-secondary text-secondary" />
									))}
								</div>
								<CardDescription className="text-base leading-relaxed">
									"Went from 0 interviews to 5 in two weeks! The ATS optimization suggestions were game-changing."
								</CardDescription>
							</CardHeader>
							<CardContent>
								<div className="flex items-center space-x-3">
									<div className="w-10 h-10 bg-primary/10 rounded-full flex items-center justify-center">
										<span className="font-mono font-semibold text-primary">A</span>
									</div>
									<div>
										<div className="font-semibold">Alex Chen</div>
										<div className="text-sm text-muted-foreground">Software Engineer</div>
									</div>
								</div>
							</CardContent>
						</Card>

						<Card className="border-2">
							<CardHeader>
								<div className="flex items-center space-x-1 mb-4">
									{[...Array(5)].map((_, i) => (
										<Star key={i} className="w-4 h-4 fill-secondary text-secondary" />
									))}
								</div>
								<CardDescription className="text-base leading-relaxed">
									"Finally understood why my resume wasn't getting through. The keyword suggestions were spot on!"
								</CardDescription>
							</CardHeader>
							<CardContent>
								<div className="flex items-center space-x-3">
									<div className="w-10 h-10 bg-secondary/10 rounded-full flex items-center justify-center">
										<span className="font-mono font-semibold text-secondary">M</span>
									</div>
									<div>
										<div className="font-semibold">Maya Patel</div>
										<div className="text-sm text-muted-foreground">Marketing Coordinator</div>
									</div>
								</div>
							</CardContent>
						</Card>

						<Card className="border-2">
							<CardHeader>
								<div className="flex items-center space-x-1 mb-4">
									{[...Array(5)].map((_, i) => (
										<Star key={i} className="w-4 h-4 fill-secondary text-secondary" />
									))}
								</div>
								<CardDescription className="text-base leading-relaxed">
									"Landed my dream job at a Fortune 500! The job-specific optimization feature is incredible."
								</CardDescription>
							</CardHeader>
							<CardContent>
								<div className="flex items-center space-x-3">
									<div className="w-10 h-10 bg-primary/10 rounded-full flex items-center justify-center">
										<span className="font-mono font-semibold text-primary">J</span>
									</div>
									<div>
										<div className="font-semibold">Jordan Smith</div>
										<div className="text-sm text-muted-foreground">Data Analyst</div>
									</div>
								</div>
							</CardContent>
						</Card>
					</div>
				</div>
			</section>

			{/* CTA Section */}
			<section className="py-20 bg-primary text-primary-foreground">
				<div className="container mx-auto px-4 sm:px-6 lg:px-8 text-center">
					<h2 className="font-mono font-bold text-3xl lg:text-4xl text-balance mb-6">Ready to Beat the ATS Game?</h2>
					<p className="text-xl text-primary-foreground/90 max-w-2xl mx-auto text-balance mb-8">
						Join thousands of job seekers who've already optimized their resumes and landed their dream jobs
					</p>
					<div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
						<Button
							size="lg"
							variant="secondary"
							className="px-8 py-3 text-lg bg-secondary hover:bg-secondary/90 text-secondary-foreground"
							asChild
						>
							<Link href={ctaLink}>
								<Upload className="w-5 h-5 mr-2" />
								Start Free Analysis
							</Link>
						</Button>
						<Button
							size="lg"
							variant="outline"
							className="px-8 py-3 text-lg border-primary-foreground/20 text-primary-foreground hover:bg-primary-foreground/10 bg-transparent"
						>
							Watch Demo
							<ArrowRight className="w-5 h-5 ml-2" />
						</Button>
					</div>
					<p className="text-sm text-primary-foreground/70 mt-6">
						No credit card required • Get results in under 60 seconds
					</p>
				</div>
			</section>

			{/* Footer */}
			<footer className="py-12 border-t border-border">
				<div className="container mx-auto px-4 sm:px-6 lg:px-8">
					<div className="grid md:grid-cols-4 gap-8">
						<div className="space-y-4">
							<div className="flex items-center space-x-2">
								<div className="w-6 h-6 bg-primary rounded-lg flex items-center justify-center">
									<span className="font-mono font-bold text-primary-foreground text-xs">RM</span>
								</div>
								<span className="font-mono font-bold text-lg">{t('title')}</span>
							</div>
							<p className="text-muted-foreground text-sm leading-relaxed">
								Empowering job seekers to ace the market with AI-powered resume optimization.
							</p>
						</div>

						<div>
							<h4 className="font-mono font-semibold mb-4">Product</h4>
							<ul className="space-y-2 text-sm text-muted-foreground">
								<li>
									<a href="#features" className="hover:text-foreground transition-colors">
										Features
									</a>
								</li>
								<li>
									<a href="#how-it-works" className="hover:text-foreground transition-colors">
										How It Works
									</a>
								</li>
								<li>
									<a href={`/${locale}/resume`} className="hover:text-foreground transition-colors">
										Upload Resume
									</a>
								</li>
								<li>
									<a href={`/${locale}/match`} className="hover:text-foreground transition-colors">
										Job Matching
									</a>
								</li>
							</ul>
						</div>

						<div>
							<h4 className="font-mono font-semibold mb-4">Resources</h4>
							<ul className="space-y-2 text-sm text-muted-foreground">
								<li>
									<a href="#" className="hover:text-foreground transition-colors">
										Career Tips
									</a>
								</li>
								<li>
									<a href="#" className="hover:text-foreground transition-colors">
										ATS Guide
									</a>
								</li>
								<li>
									<a href="#" className="hover:text-foreground transition-colors">
										Resume Templates
									</a>
								</li>
								<li>
									<a href="#" className="hover:text-foreground transition-colors">
										Help Center
									</a>
								</li>
							</ul>
						</div>

						<div>
							<h4 className="font-mono font-semibold mb-4">Company</h4>
							<ul className="space-y-2 text-sm text-muted-foreground">
								<li>
									<a href="#" className="hover:text-foreground transition-colors">
										About
									</a>
								</li>
								<li>
									<a href="#" className="hover:text-foreground transition-colors">
										Privacy
									</a>
								</li>
								<li>
									<a href="#" className="hover:text-foreground transition-colors">
										Terms
									</a>
								</li>
								<li>
									<a href="#" className="hover:text-foreground transition-colors">
										Contact
									</a>
								</li>
							</ul>
						</div>
					</div>

					<div className="border-t border-border mt-8 pt-8 flex flex-col sm:flex-row justify-between items-center">
						<p className="text-sm text-muted-foreground">© 2024 Resume Matcher. All rights reserved.</p>
						<div className="flex items-center space-x-4 mt-4 sm:mt-0">
							<a href="#" className="text-muted-foreground hover:text-foreground transition-colors">
								<span className="sr-only">GitHub</span>
								<svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
									<path fillRule="evenodd" d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.531 1.032 1.531 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z" clipRule="evenodd" />
								</svg>
							</a>
							<a href="#" className="text-muted-foreground hover:text-foreground transition-colors">
								<span className="sr-only">Twitter</span>
								<svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
									<path d="M8.29 20.251c7.547 0 11.675-6.253 11.675-11.675 0-.178 0-.355-.012-.53A8.348 8.348 0 0022 5.92a8.19 8.19 0 01-2.357.646 4.118 4.118 0 001.804-2.27 8.224 8.224 0 01-2.605.996 4.107 4.107 0 00-6.993 3.743 11.65 11.65 0 01-8.457-4.287 4.108 4.108 0 003.834 2.85A8.233 8.233 0 012 18.407a11.616 11.616 0 006.29 1.84" />
								</svg>
							</a>
						</div>
					</div>
				</div>
			</footer>
		</div>
	);
}
