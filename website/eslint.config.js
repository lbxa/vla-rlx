import eslintPluginAstro from 'eslint-plugin-astro';
import typescriptEslintParser from '@typescript-eslint/parser';

export default [
  // Ignore patterns first
  {
    ignores: [
      'dist/',
      'node_modules/',
      '.astro/',
      'bun.lockb',
      '*.lock',
    ],
  },
  
  // Astro recommended configuration
  ...eslintPluginAstro.configs.recommended,
  
  // TypeScript and JavaScript files
  {
    files: ['**/*.{js,ts}'],
    languageOptions: {
      parser: typescriptEslintParser,
      parserOptions: {
        ecmaVersion: 'latest',
        sourceType: 'module',
      },
    },
    rules: {
      // General rules
      'no-console': 'warn',
      'no-unused-vars': 'warn',
      'prefer-const': 'error',
    },
  },
  
  // Astro files specific configuration
  {
    files: ['**/*.astro'],
    rules: {
      // Astro specific rules
      'astro/no-conflict-set-directives': 'error',
      'astro/no-unused-define-vars-in-style': 'error',
      
      // Allow console in Astro files (for development)
      'no-console': 'off',
    },
  },
];