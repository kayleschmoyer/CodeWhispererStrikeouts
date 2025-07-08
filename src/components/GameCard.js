import { motion } from 'framer-motion';
import { TrendingUp, TrendingDown, Info } from 'lucide-react';
import { statTooltips } from '../mockData';

const StatTooltip = ({ stat, value, children }) => (
  <div className="tooltip-container">
    {children}
    <div className="tooltip">
      <strong>{stat}:</strong> {statTooltips[stat]}
      <br />
      <span className="tooltip-value">Current: {value}%</span>
    </div>
  </div>
);

const PitcherCard = ({ pitcher, isHome, teamStats, expectedBatters }) => {
  const confidence = pitcher.projection.confidence;
  const confidenceColor = confidence >= 75 ? 'var(--success)' : confidence >= 65 ? 'var(--warning)' : 'var(--danger)';
  
  return (
    <div className={`pitcher-card ${isHome ? 'home' : 'away'}`}>
      <div className="pitcher-header">
        <div className="pitcher-info">
          <h3>{pitcher.name}</h3>
          <span className="pitcher-hand">{pitcher.hand}HP</span>
        </div>
        <div className="projection">
          <div className="projection-main">
            <span className="projection-line">{pitcher.projection.line}</span>
            <span className="projection-value">{pitcher.projection.strikeouts} K</span>
          </div>
          <div className="confidence" style={{ color: confidenceColor }}>
            {confidence}% confidence
          </div>
        </div>
      </div>
      
      <div className="pitcher-stats">
        <StatTooltip stat="k9" value={pitcher.stats.k9}>
          <div className="stat">
            <span className="stat-label">K/9</span>
            <span className="stat-value">{pitcher.stats.k9}</span>
          </div>
        </StatTooltip>
        <StatTooltip stat="kPercent" value={pitcher.stats.kPercent}>
          <div className="stat">
            <span className="stat-label">K%</span>
            <span className="stat-value">{pitcher.stats.kPercent}%</span>
          </div>
        </StatTooltip>
        <StatTooltip stat="whiffRate" value={pitcher.stats.whiffRate}>
          <div className="stat">
            <span className="stat-label">Whiff</span>
            <span className="stat-value">{pitcher.stats.whiffRate}%</span>
          </div>
        </StatTooltip>
        <StatTooltip stat="swingStrikeRate" value={pitcher.stats.swingStrikeRate}>
          <div className="stat">
            <span className="stat-label">SwStr</span>
            <span className="stat-value">{pitcher.stats.swingStrikeRate}%</span>
          </div>
        </StatTooltip>
      </div>

      <div className="team-matchup">
        <div className="matchup-stat">
          <span className="matchup-label">vs {pitcher.hand}HP</span>
          <span className="matchup-value">
            {pitcher.hand === 'R' ? teamStats.vsRHP : teamStats.vsLHP}% K
          </span>
        </div>
      </div>

      <div className="expected-batters">
        <h4>Key Matchups</h4>
        <div className="batters-list">
          {expectedBatters.slice(0, 4).map((batter, idx) => (
            <div key={idx} className="batter-item">
              <span className="batter-name">{batter.name}</span>
              <div className="batter-stats">
                <span className="batter-k-rate">{batter.kRate}% K</span>
                {batter.vsOpponent > 0 && (
                  <span className="vs-pitcher">{batter.vsOpponent} K vs {pitcher.name.split(' ')[1]}</span>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

const GameCard = ({ game }) => {
  const topProjection = Math.max(
    game.homePitcher.projection.strikeouts,
    game.awayPitcher.projection.strikeouts
  );
  
  const isTopGame = topProjection >= 8.5;

  return (
    <motion.div
      className={`game-card ${isTopGame ? 'top-game' : ''}`}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      whileHover={{ y: -4 }}
      transition={{ duration: 0.3 }}
    >
      <div className="game-header">
        <div className="teams">
          <div className="team away">
            <span className="team-logo">{game.awayTeam.logo}</span>
            <span className="team-name">{game.awayTeam.name}</span>
          </div>
          <div className="vs">@</div>
          <div className="team home">
            <span className="team-logo">{game.homeTeam.logo}</span>
            <span className="team-name">{game.homeTeam.name}</span>
          </div>
        </div>
        <div className="game-time">{game.gameTime}</div>
        {isTopGame && (
          <div className="top-game-badge">
            <TrendingUp size={16} />
            Elite Pick
          </div>
        )}
      </div>

      <div className="pitchers">
        <PitcherCard
          pitcher={game.awayPitcher}
          isHome={false}
          teamStats={game.teamStats.home}
          expectedBatters={game.expectedBatters}
        />
        <PitcherCard
          pitcher={game.homePitcher}
          isHome={true}
          teamStats={game.teamStats.away}
          expectedBatters={game.expectedBatters}
        />
      </div>
    </motion.div>
  );
};

export default GameCard;