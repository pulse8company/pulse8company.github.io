# Pulse8 developer website

Website: https://pulse8company.github.io/

Advertising file: https://pulse8company.github.io/app-ads.txt

## Update app-ads.txt

1. Get the exact app-ads.txt entries from your advertising networks (for example, AdMob).
2. Open app-ads.txt in this repository, click the pencil icon, and replace the setup comments with those entries. Alternatively, use Add file → Upload files to upload a replacement named exactly app-ads.txt at the repository root.
3. Commit the changes to main. GitHub Pages publishes the update automatically.
4. Set https://pulse8company.github.io/ as the developer website in your app store listing.
5. Request verification in your advertising network's dashboard after the public file updates. Crawling can take time.

The initial app-ads.txt contains comments only. Ad verification cannot succeed until the correct publisher entries are supplied.

## Publishing configuration

In Settings → Pages, select Deploy from a branch, branch main, folder / (root), and save. This repository must be public for GitHub Pages on GitHub Free.

Edit index.html to update the homepage. This is a static website; file uploads and edits are managed securely through GitHub, not through a public upload form.
