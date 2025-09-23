// clone.js
const { chromium } = require('playwright');
const fs = require('fs').promises;
const path = require('path');
const cheerio = require('cheerio'); // For parsing HTML easily

const targetUrl = 'https://www.longi.com/en/modules-authenticity/';
const outputDir = 'longi_js_clone';

async function clonePage() {
    let browser;
    try {
        browser = await chromium.launch({ headless: true }); // set headless to false to see the browser
        const page = await browser.newPage();

        console.log(`Navigating to ${targetUrl}...`);
        await page.goto(targetUrl, { waitUntil: 'networkidle' }); // Wait for network to be idle, helps ensure all resources loaded

        // Create output directory
        await fs.mkdir(outputDir, { recursive: true });

        // 1. Get the fully rendered HTML
        const htmlContent = await page.content();
        const htmlFilePath = path.join(outputDir, 'index.html');
        await fs.writeFile(htmlFilePath, htmlContent, 'utf8');
        console.log(`Saved HTML to ${htmlFilePath}`);

        // 2. Identify and download assets (Simplified example - highly complex for a full clone)
        const $ = cheerio.load(htmlContent);

        const assetsToDownload = [];

        // Find CSS files
        $('link[rel="stylesheet"]').each((i, el) => {
            const href = $(el).attr('href');
            if (href) {
                assetsToDownload.push({ type: 'css', url: new URL(href, targetUrl).href });
            }
        });

        // Find images
        $('img').each((i, el) => {
            const src = $(el).attr('src');
            if (src) {
                assetsToDownload.push({ type: 'img', url: new URL(src, targetUrl).href });
            }
        });

        // Find JS files
        $('script[src]').each((i, el) => {
            const src = $(el).attr('src');
            if (src) {
                assetsToDownload.push({ type: 'js', url: new URL(src, targetUrl).href });
            }
        });

        console.log(`Found ${assetsToDownload.length} potential assets.`);

        // Download each asset (this is a very basic implementation and needs refinement)
        for (const asset of assetsToDownload) {
            try {
                const assetUrl = asset.url;
                const assetFileName = path.basename(new URL(assetUrl).pathname);
                const assetFilePath = path.join(outputDir, assetFileName);

                const response = await page.goto(assetUrl); // Use page.goto to download
                if (response.ok()) {
                    const buffer = await response.body();
                    await fs.writeFile(assetFilePath, buffer);
                    console.log(`Downloaded ${asset.type}: ${assetFileName}`);
                    // In a real cloner, you'd also rewrite the HTML/CSS paths here.
                } else {
                    console.warn(`Failed to download ${asset.type} ${assetUrl}: ${response.status()}`);
                }
            } catch (dlError) {
                console.error(`Error downloading asset ${asset.url}:`, dlError.message);
            }
        }

        console.log('Cloning process completed (basic assets downloaded).');

    } catch (error) {
        console.error('An error occurred:', error);
    } finally {
        if (browser) {
            await browser.close();
        }
    }
}

clonePage();