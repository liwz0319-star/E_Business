
const { chromium } = require('playwright');
const fs = require('fs');

(async () => {
    console.log('Starting enhanced reproduction script with Auth (Register -> Login -> Home)...');
    const browser = await chromium.launch({ headless: true });
    const context = await browser.newContext();
    const page = await context.newPage();

    // --- Logging Setup ---
    page.on('console', msg => {
        const text = msg.text();
        if (text.includes('WebSocket')) {
            console.log(`[BROWSER-WS] ${text}`);
        } else if (msg.type() === 'error') {
            console.log(`[BROWSER-ERR] ${text}`);
        }
    });

    page.on('response', async response => {
        const url = response.url();
        if (url.includes('/api/') || url.includes('socket.io')) {
            try {
                const status = response.status();
                if (status >= 400) {
                    const body = await response.text();
                    console.log(`[API-FAIL] ${status} ${url}: ${body.substring(0, 500)}`);
                } else if (url.includes('/generate') || url.includes('/copywriting')) {
                    console.log(`[API-OK] ${status} ${url}`);
                }
            } catch (e) { }
        }
    });
    // ---------------------

    try {
        console.log('Navigating to http://localhost:3000...');
        await page.goto('http://localhost:3000');
        await page.waitForLoadState('networkidle');

        // Check if we are on Login page
        const welcomeHeader = page.getByRole('heading', { name: /Welcome back/i });

        if (await welcomeHeader.isVisible()) {
            console.log('On Login Page. Switching to Sign Up...');
            const signUpLink = page.getByText('Sign up', { exact: true });
            await signUpLink.click();
            await page.waitForTimeout(1000);
        }

        const createAccountHeader = page.getByRole('heading', { name: /Create Account/i });
        const timestamp = Date.now();
        const email = `auto_${timestamp}@test.com`;
        const password = 'Password@123';

        if (await createAccountHeader.isVisible()) {
            console.log('On Signup Page. Registering user...');

            await page.getByPlaceholder('name@company.com').fill(email);
            // First password field
            await page.getByPlaceholder('••••••••').nth(0).fill(password);
            // Second password field
            await page.getByPlaceholder('••••••••').nth(1).fill(password);
            // Terms
            await page.locator('#terms').check();

            console.log(`Submitting registration for ${email}...`);
            await page.getByRole('button', { name: /Create Account/i }).click();

            console.log('Waiting for redirection to Login page...');
            // Wait for "Welcome back" header again
            await page.getByRole('heading', { name: /Welcome back/i }).waitFor({ state: 'visible', timeout: 15000 });
            console.log('Redirected to Login page successfully!');

            // --- Login Step ---
            console.log('Logging in with new credentials...');
            await page.getByPlaceholder('name@company.com').fill(email);
            await page.getByPlaceholder('••••••••').fill(password); // Login only has one password field

            await page.getByRole('button', { name: /Sign in/i }).click();

            console.log('Waiting for navigation to Home (Product Copy card)...');
            await page.getByText('Product Copy').first().waitFor({ state: 'visible', timeout: 15000 });
            console.log('Login successful! At Home page.');

        } else {
            console.log('Not on Signup/Login? Check if already at Home...');
            if (await page.getByText('Product Copy').first().isVisible()) {
                console.log('Already at Home page.');
            } else {
                throw new Error('Unknown page state.');
            }
        }

        // --- At Home Page ---
        console.log('Locating "Product Copy" card...');
        const card = page.getByRole('button').filter({ hasText: 'Product Copy' });
        await card.click();
        console.log('Clicked "Product Copy". Expecting immediate generation trigger...');

        console.log('Monitoring logs for 40 seconds (waiting for WebSocket/API error)...');

        // Wait for error message in UI
        try {
            const errorMsg = page.getByText(/DeepSeek API key is required/i);
            await errorMsg.waitFor({ state: 'visible', timeout: 30000 });
            console.log('✅ UI ERROR DETECTED: "DeepSeek API key is required"');
        } catch (e) {
            console.log('UI Error message not found within timeout.');
        }

        // Wait for final logs
        await page.waitForTimeout(5000);

        // Screenshot
        await page.screenshot({ path: 'reproduce_final.png', fullPage: true });
        console.log('Saved reproduce_final.png');

    } catch (error) {
        console.error('SCRIPT CRASH:', error);
        await page.screenshot({ path: 'reproduce_crash.png' });
    } finally {
        await browser.close();
    }
})();
