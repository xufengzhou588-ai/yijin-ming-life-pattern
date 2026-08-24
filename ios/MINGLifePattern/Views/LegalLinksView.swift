import SwiftUI

struct LegalLinksView: View {
    var body: some View {
        NavigationStack {
            List {
                Section("Trust and safety") {
                    Link("Privacy Policy", destination: AppEnvironment.privacyURL)
                    Link("Terms of Use", destination: AppEnvironment.termsURL)
                    Link("Support", destination: AppEnvironment.supportURL)
                    Link("Methodology & Data Sources", destination: AppEnvironment.methodologyURL)
                }

                Section("Product boundary") {
                    Text("MING provides cultural interpretation and personal reflection. It does not guarantee outcomes or replace licensed professional advice.")
                    Text("Saved charts and oracle entries should remain private by default. Cloud sync should be added only after account and deletion flows are ready.")
                }

                Section("Data update policy") {
                    Text("Daily, monthly, and annual prompts are generated automatically from the user's chart and date rhythm.")
                    Text("Rule tables, location data, calendar dependencies, paid report copy, and App Store metadata require manual review before release.")
                }
            }
            .navigationTitle("Trust")
        }
    }
}
