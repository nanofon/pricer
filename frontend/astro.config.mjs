import { defineConfig } from 'astro/config';
import react from '@astrojs/react';

// https://astro.build/config
export default defineConfig({
	// Enable React to support React JSX components.
	integrations: [react()],
	server: {
		port: 4321,
		host: '0.0.0.0',
		watch: {
			polling: true,
			interval: 1000,
		},
		hmr: {
			protocol: 'http',
			host: '0.0.0.0',
			port: 4321,
		},
	},
});
