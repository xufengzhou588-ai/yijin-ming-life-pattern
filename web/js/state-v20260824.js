window.MING_STATE = {
  storageKeys: {
    history: "bazi.recentCharts.v1",
    profile: "ming.birthProfile.v1",
    productEvents: "ming.productEvents.v1",
    oracleJournal: "ming.oracleJournal.v1",
    dailyCheckins: "ming.dailyCheckins.v1"
  },
  ritualState: { skip: false, active: false },
  oracleState: {
    lines: [],
    question: "",
    category: "general",
    horizon: "one_month",
    result: null,
    casting: false
  },
  resultState: {
    payload: null,
    traits: null,
    displayName: "",
    activePro: "",
    requestedPro: "",
    annualOutlook: null,
    monthlyCompass: null,
    selectedMonthIndex: 0,
    generatedAt: "",
    isPro: false,
    entitlementReady: false,
    canDemoUnlock: false,
    setupComplete: false,
    proReports: {}
  }
};
