"use client";

import React from 'react';
import { useTranslations } from 'next-intl';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import type { Session } from 'next-auth';
import BackgroundContainer from '@/components/common/background-container';
import FileUpload from '@/components/common/file-upload';

export default function Hero({ session }: { session: Session | null }) {
	const t = useTranslations('Hero');
	const pathname = usePathname();
	const parts = pathname.split('/').filter(Boolean);
	const locale = parts[0] || 'en';
	// CTA scrolls to inline upload section on the same page
	const ctaLink = `/${locale}#upload`;

	return (
		<BackgroundContainer className="pt-20">
			<div className="relative mb-4 h-[30vh] w-full ">
				<h1 className="text-center text-8xl font-semibold text-gray-900">
					{t('title')}
				</h1>
			</div>
			<p className="mb-12 --font-space-grotesk text-center text-lg text-gray-700 md:text-xl">
				{t('tagline')}
			</p>
			<Link
				href={ctaLink}
				className="group relative inline-flex h-10 overflow-hidden rounded-full p-[1px] bg-blue-600 hover:bg-blue-700"
			>
				<span className="inline-flex h-full w-full cursor-pointer items-center justify-center rounded-full bg-blue-600 hover:bg-blue-700 px-3 py-1 text-sm font-medium text-white transition-colors">
					{t('cta')}
					<svg
						width="16"
						height="16"
						viewBox="0 0 0.3 0.3"
						fill="#FFF"
						xmlns="http://www.w3.org/2000/svg"
						className="ml-2 transition-transform duration-200 ease-in-out group-hover:translate-x-1" // Hover animation
					>
						<path d="M.166.046a.02.02 0 0 1 .028 0l.09.09a.02.02 0 0 1 0 .028l-.09.09A.02.02 0 0 1 .166.226L.22.17H.03a.02.02 0 0 1 0-.04h.19L.166.074a.02.02 0 0 1 0-.028" />
					</svg>
				</span>
			</Link>

			{/* Inline Upload Section */}
			<section id="upload" className="mt-12">
				<div className="mx-auto w-full max-w-3xl rounded-xl border border-gray-200 bg-white p-4 shadow-sm md:p-6">
					<FileUpload session={session} />
				</div>
			</section>
		</BackgroundContainer>
	);
}
