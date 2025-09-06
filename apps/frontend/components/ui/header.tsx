import Link from 'next/link';
import { NeoGlassCard } from '@/components/ui/glass';

const Header = () => {
	return (
		<header className="sticky top-0 left-0 z-50 w-full">
			<NeoGlassCard 
				variant="frost"
				depth="flat"
				animation="none"
				glare
				className="w-full backdrop-blur-md py-2"
			>
				<div className="container mx-auto flex h-14 items-center justify-between px-6">
					{/* Logo */}
					<Link href="/" className="text-xl font-bold text-white group">
						<span className="bg-gradient-to-r from-white to-blue-200 bg-clip-text text-transparent">
							Resume Matcher
						</span>
						<span className="ml-1 opacity-0 group-hover:opacity-100 transition-opacity duration-300 text-blue-300">AI</span>
					</Link>

					{/* Navigation */}
					<nav className="flex items-center space-x-6">
						<Link href="/overview" className="text-sm text-white/80 hover:text-white transition-colors duration-200">
							Overview
						</Link>
						<Link href="/sign-up" className="text-sm text-white/80 hover:text-white transition-colors duration-200">
							Sign up
						</Link>
						<Link href="/blog" className="text-sm text-white/80 hover:text-white transition-colors duration-200">
							Blog
						</Link>
						<Link
							href="/buy"
							className="relative overflow-hidden rounded-md bg-gradient-to-r from-blue-500 to-purple-500 px-4 py-2 text-sm font-medium text-white transition-all duration-300 hover:shadow-lg hover:shadow-blue-500/25 hover:scale-105"
						>
							<span className="relative z-10">Get Premium</span>
							<span className="absolute inset-0 bg-white/20 blur-sm transform translate-y-full group-hover:translate-y-0 transition-transform duration-300"></span>
						</Link>
					</nav>
				</div>
			</NeoGlassCard>
		</header>
	);
};

export default Header;
