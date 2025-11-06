import type { Config } from 'tailwindcss'
import typography from '@tailwindcss/typography'

const config = {
  content: ['./src/**/*.{astro,html,js,jsx,md,mdx,svelte,ts,tsx,vue}'],
  theme: {
    extend: {
      // Nerfies color palette
      colors: {
        nerfies: {
          primary: '#3273dc', // hsl(204, 86%, 53%)
          'primary-hover': '#2366d1',
          teal: '#00d1b2',
          gray: {
            50: '#f5f5f5',
            100: '#eeeeee',
            200: '#e0e0e0',
            300: '#bdbdbd',
            400: '#9e9e9e',
            500: '#757575',
            600: '#616161',
            700: '#424242',
            800: '#363636',
            900: '#212121',
          }
        }
      },
      // Nerfies fonts
      fontFamily: {
        'google-sans': ['"Google Sans"', 'system-ui', 'sans-serif'],
        'noto-sans': ['"Noto Sans"', 'system-ui', 'sans-serif'],
      },
      spacing: {
        sm: '0.5rem', // 8px
        md: '1rem',   // 16px
        lg: '1.5rem', // 24px
        xl: '2rem',   // 32px
      },
      // Nerfies-inspired shadows
      boxShadow: {
        'nerfies': '0 .5em 1em -.125em rgba(10,10,10,.1)',
        'nerfies-lg': '0 8px 16px 0 rgba(10,10,10,.1)',
      },
      typography: {
        DEFAULT: {
          css: {
            maxWidth: 'none',
            color: '#4a4a4a', // Nerfies text gray
            fontFamily: '"Noto Sans", system-ui, sans-serif',
            a: {
              color: '#3273dc', // Nerfies primary blue
              textDecoration: 'none',
              '&:hover': {
                color: '#2366d1', // Darker blue on hover
                textDecoration: 'underline',
              },
            },
            'h1, h2, h3, h4': {
              color: '#363636', // Nerfies heading color
              fontFamily: '"Google Sans", system-ui, sans-serif',
            },
            code: {
              color: '#757575',
              backgroundColor: '#f5f5f5',
              paddingLeft: '0.5rem',
              paddingRight: '0.5rem',
              paddingTop: '0.25rem',
              paddingBottom: '0.25rem',
              borderRadius: '4px', // Nerfies border radius
              fontSize: '0.875rem',
            },
            'code::before': {
              content: '""',
            },
            'code::after': {
              content: '""',
            },
          },
        },
      },
    },
  },
  plugins: [
    typography,
  ],
} satisfies Config;

export default config