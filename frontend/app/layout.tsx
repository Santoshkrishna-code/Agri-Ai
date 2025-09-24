import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
    title: 'Agri-AI | Rice & Wheat Disease Detection',
    description: 'AI-powered crop disease detection using advanced computer vision. Upload images of rice or wheat crops to detect diseases with instant analysis and confidence scores.',
    keywords: 'agriculture, AI, disease detection, rice, wheat, computer vision, crop analysis',
    authors: [{ name: 'Agri-AI Team' }],
    viewport: 'width=device-width, initial-scale=1',
}

export default function RootLayout({
    children,
}: {
    children: React.ReactNode
}) {
    return (
        <html lang="en">
            <body className="antialiased">
                {children}
            </body>
        </html>
    )
}