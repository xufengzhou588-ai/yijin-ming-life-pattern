# App Review Notes

MING is an informational lifestyle app for cultural exploration and personal
reflection. It translates Chinese Four Pillars and I Ching-inspired structures
into modern language. It does not provide medical, legal, financial,
mental-health, safety, or emergency advice. It does not promise outcomes or
make fixed predictions.

The product is positioned as reflective journaling and cultural interpretation,
not as a tool for fixed future outcomes. All generated content should be read
as personal reflection prompts.

Pro access is sold through App Store auto-renewable subscriptions:

- `ming.pro.monthly`
- `ming.pro.yearly`

Restore Purchase is available on the native Pro screen.

The app contains native navigation and subscription handling. The current
life-pattern reading experience is presented inside a controlled WKWebView
while the product is migrated toward deeper native screens.

The WKWebView loads first-party MING content only. It is not a general web
browser and does not provide unrestricted web access.

The app does not include third-party advertising and does not use external
payment methods.

Reviewer instructions:

1. Open the app.
2. Use the Reading tab to generate a free life-pattern reading.
3. Use the Pro tab to view subscription options.
4. Use Restore Purchase to verify purchase recovery.
5. Use Trust to open Privacy Policy, Terms, and Support.

If Apple requests a Pro test path, provide a sandbox tester account after
StoreKit products are created in App Store Connect.

Required production URLs before submission:

- Privacy Policy: `https://mingpattern.app/legal/privacy`
- Terms of Use: `https://mingpattern.app/legal/terms`
- Support: `https://mingpattern.app/support`
