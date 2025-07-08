export const mockGames = [
  {
    id: 1,
    homeTeam: { name: "Yankees", abbr: "NYY", logo: "⚾" },
    awayTeam: { name: "Red Sox", abbr: "BOS", logo: "⚾" },
    gameTime: "7:05 PM ET",
    homePitcher: {
      name: "Gerrit Cole",
      hand: "R",
      stats: { k9: 11.2, kPercent: 28.5, whiffRate: 32.1, swingStrikeRate: 14.8 },
      projection: { strikeouts: 8.5, confidence: 78, line: "Over 7.5" }
    },
    awayPitcher: {
      name: "Chris Sale",
      hand: "L",
      stats: { k9: 12.1, kPercent: 31.2, whiffRate: 35.4, swingStrikeRate: 16.2 },
      projection: { strikeouts: 9.2, confidence: 82, line: "Over 8.5" }
    },
    teamStats: {
      home: { vsRHP: 22.1, vsLHP: 24.8 },
      away: { vsRHP: 23.4, vsLHP: 21.9 }
    },
    expectedBatters: [
      { name: "Rafael Devers", hand: "L", kRate: 18.5, vsOpponent: 3 },
      { name: "Xander Bogaerts", hand: "R", kRate: 15.2, vsOpponent: 1 },
      { name: "J.D. Martinez", hand: "R", kRate: 24.1, vsOpponent: 5 },
      { name: "Alex Verdugo", hand: "L", kRate: 19.8, vsOpponent: 2 }
    ]
  },
  {
    id: 2,
    homeTeam: { name: "Dodgers", abbr: "LAD", logo: "⚾" },
    awayTeam: { name: "Padres", abbr: "SD", logo: "⚾" },
    gameTime: "10:10 PM ET",
    homePitcher: {
      name: "Walker Buehler",
      hand: "R",
      stats: { k9: 10.8, kPercent: 26.9, whiffRate: 29.7, swingStrikeRate: 13.5 },
      projection: { strikeouts: 7.8, confidence: 71, line: "Over 6.5" }
    },
    awayPitcher: {
      name: "Yu Darvish",
      hand: "R",
      stats: { k9: 9.9, kPercent: 25.1, whiffRate: 28.3, swingStrikeRate: 12.9 },
      projection: { strikeouts: 6.9, confidence: 68, line: "Over 6.5" }
    },
    teamStats: {
      home: { vsRHP: 21.8, vsLHP: 23.5 },
      away: { vsRHP: 24.2, vsLHP: 22.1 }
    },
    expectedBatters: [
      { name: "Mookie Betts", hand: "R", kRate: 16.8, vsOpponent: 2 },
      { name: "Freddie Freeman", hand: "L", kRate: 12.4, vsOpponent: 1 },
      { name: "Will Smith", hand: "R", kRate: 21.3, vsOpponent: 3 },
      { name: "Max Muncy", hand: "L", kRate: 26.7, vsOpponent: 4 }
    ]
  },
  {
    id: 3,
    homeTeam: { name: "Astros", abbr: "HOU", logo: "⚾" },
    awayTeam: { name: "Angels", abbr: "LAA", logo: "⚾" },
    gameTime: "8:10 PM ET",
    homePitcher: {
      name: "Framber Valdez",
      hand: "L",
      stats: { k9: 8.9, kPercent: 22.8, whiffRate: 25.1, swingStrikeRate: 11.2 },
      projection: { strikeouts: 5.8, confidence: 64, line: "Under 6.5" }
    },
    awayPitcher: {
      name: "Shohei Ohtani",
      hand: "R",
      stats: { k9: 13.4, kPercent: 33.1, whiffRate: 38.2, swingStrikeRate: 17.8 },
      projection: { strikeouts: 10.1, confidence: 85, line: "Over 9.5" }
    },
    teamStats: {
      home: { vsRHP: 20.9, vsLHP: 22.4 },
      away: { vsRHP: 25.1, vsLHP: 23.8 }
    },
    expectedBatters: [
      { name: "Jose Altuve", hand: "R", kRate: 14.2, vsOpponent: 1 },
      { name: "Alex Bregman", hand: "R", kRate: 17.9, vsOpponent: 2 },
      { name: "Yordan Alvarez", hand: "L", kRate: 19.5, vsOpponent: 3 },
      { name: "Kyle Tucker", hand: "L", kRate: 18.1, vsOpponent: 2 }
    ]
  }
];

export const statTooltips = {
  k9: "Strikeouts per 9 innings - measures strikeout rate per game",
  kPercent: "Strikeout percentage - percentage of plate appearances ending in strikeout",
  whiffRate: "Whiff rate - percentage of swings that miss the ball",
  swingStrikeRate: "Swinging strike rate - percentage of pitches that result in swinging strikes",
  vsRHP: "Team strikeout rate when facing right-handed pitching",
  vsLHP: "Team strikeout rate when facing left-handed pitching"
};