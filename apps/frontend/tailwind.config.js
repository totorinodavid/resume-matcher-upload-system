/** @type {import('tailwindcss').Config} */
module.exports = {
    content: [
        "./app/**/*.{js,ts,jsx,tsx,mdx}",
        "./components/**/*.{js,ts,jsx,tsx,mdx}",
    ],
    theme: {
        extend: {
            backgroundImage: {
                'gradient-radial': 'radial-gradient(var(--tw-gradient-stops))',
            },
            animation: {
                'gradient': 'gradient 8s linear infinite',
                'glow': 'glow 2s ease-in-out infinite alternate',
                'shimmer': 'shimmer 5s infinite',
                'pulse-glass': 'pulse-glass 3s ease-in-out infinite',
                'float': 'float 6s ease-in-out infinite',
                'refract': 'refract 5s ease infinite',
                'color-shift': 'color-shift 10s linear infinite',
            },
            keyframes: {
                'gradient': {
                    to: { 'background-position': '200% center' },
                },
                'glow': {
                    '0%': { 
                        boxShadow: '0 0 20px rgba(139, 92, 246, 0.3)',
                        transform: 'scale(1)',
                    },
                    '100%': { 
                        boxShadow: '0 0 30px rgba(139, 92, 246, 0.5), 0 0 40px rgba(59, 130, 246, 0.3)',
                        transform: 'scale(1.02)',
                    },
                },
                'shimmer': {
                    '0%': { transform: 'translateX(-100%)' },
                    '100%': { transform: 'translateX(100%)' },
                },
                'pulse-glass': {
                    '0%': { backdropFilter: 'blur(10px)', backgroundColor: 'rgba(255, 255, 255, 0.1)' },
                    '50%': { backdropFilter: 'blur(15px)', backgroundColor: 'rgba(255, 255, 255, 0.15)' },
                    '100%': { backdropFilter: 'blur(10px)', backgroundColor: 'rgba(255, 255, 255, 0.1)' },
                },
                'float': {
                    '0%': { transform: 'translateY(0px)' },
                    '50%': { transform: 'translateY(-10px)' },
                    '100%': { transform: 'translateY(0px)' },
                },
                'refract': {
                    '0%': { backdropFilter: 'blur(10px) hue-rotate(0deg)' },
                    '50%': { backdropFilter: 'blur(12px) hue-rotate(15deg)' },
                    '100%': { backdropFilter: 'blur(10px) hue-rotate(0deg)' },
                },
                'color-shift': {
                    '0%': { borderColor: 'rgba(255, 255, 255, 0.2)' },
                    '33%': { borderColor: 'rgba(125, 211, 252, 0.2)' },
                    '66%': { borderColor: 'rgba(167, 139, 250, 0.2)' },
                    '100%': { borderColor: 'rgba(255, 255, 255, 0.2)' },
                }
            },
            fontFamily: {
                sans: ['"Geist Sans"', 'sans-serif'],
                mono: ['"Space Grotesk"', 'monospace'],
            },
            backdropBlur: {
                xs: '2px',
                sm: '4px',
                md: '8px',
                lg: '12px',
                xl: '16px',
            },
            backgroundColor: {
                'glass': 'rgba(255, 255, 255, 0.1)',
                'glass-dark': 'rgba(0, 0, 0, 0.2)',
                'glass-light': 'rgba(255, 255, 255, 0.15)',
                'glass-lighter': 'rgba(255, 255, 255, 0.25)',
                'glass-darker': 'rgba(0, 0, 0, 0.3)',
                'glass-blue': 'rgba(59, 130, 246, 0.15)',
                'glass-purple': 'rgba(139, 92, 246, 0.15)',
                'glass-neo': 'rgba(255, 255, 255, 0.15)',
                'glass-frost': 'rgba(255, 255, 255, 0.12)',
                'glass-smoke': 'rgba(15, 23, 42, 0.15)',
                'glass-gradient': 'linear-gradient(135deg, rgba(255, 255, 255, 0.1), rgba(255, 255, 255, 0.05))',
                'glass-gradient-dark': 'linear-gradient(135deg, rgba(0, 0, 0, 0.1), rgba(0, 0, 0, 0.2))',
            },
            borderColor: {
                'glass': 'rgba(255, 255, 255, 0.2)',
                'glass-dark': 'rgba(255, 255, 255, 0.1)',
                'glass-light': 'rgba(255, 255, 255, 0.3)',
                'glass-blue': 'rgba(59, 130, 246, 0.3)',
                'glass-purple': 'rgba(139, 92, 246, 0.3)',
            },
            boxShadow: {
                'glass': '0 4px 30px rgba(0, 0, 0, 0.1)',
                'glass-strong': '0 8px 32px rgba(0, 0, 0, 0.2)',
                'glass-inner': 'inset 0 0 10px rgba(255, 255, 255, 0.15)',
                'glass-blue': '0 4px 20px rgba(59, 130, 246, 0.3)',
                'glass-purple': '0 4px 20px rgba(139, 92, 246, 0.3)',
                'glass-double': '0 8px 32px rgba(0, 0, 0, 0.1), inset 0 1px 0 rgba(255, 255, 255, 0.5), inset 0 -1px 0 rgba(255, 255, 255, 0.1)',
                'glass-highlight': '0 8px 32px rgba(0, 0, 0, 0.1), inset 0 0 20px 10px rgba(255, 255, 255, 0.12)',
                'glass-neo': '0 8px 32px rgba(0, 0, 0, 0.2), inset 0 0 0 1px rgba(255, 255, 255, 0.2), inset 0 2px 2px rgba(255, 255, 255, 0.2)',
            },
        },
    },
    plugins: [],
}