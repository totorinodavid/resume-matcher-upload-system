import { ReactNode } from 'react'

export const metadata = {
  title: 'Resume Matcher Upload API',
  description: 'Upload system for Resume Matcher platform'
}

export default function RootLayout({
  children,
}: {
  children: ReactNode
}) {
  return (
    <html lang="en">
      <body>
        <main>{children}</main>
      </body>
    </html>
  )
}
