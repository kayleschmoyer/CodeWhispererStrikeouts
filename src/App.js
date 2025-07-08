import { useState, useMemo, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import Header from './components/Header';
import GameCard from './components/GameCard';
import { mockGames } from './mockData';
import './App.css';

function App() {
  const [darkMode, setDarkMode] = useState(true);
  const [sortBy, setSortBy] = useState('confidence');
  const [filterBy, setFilterBy] = useState('all');

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', darkMode ? 'dark' : 'light');
  }, [darkMode]);

  const filteredAndSortedGames = useMemo(() => {
    let games = [...mockGames];

    // Filter games
    if (filterBy === 'elite') {
      games = games.filter(game => 
        Math.max(game.homePitcher.projection.strikeouts, game.awayPitcher.projection.strikeouts) >= 8.5
      );
    } else if (filterBy === 'high-confidence') {
      games = games.filter(game => 
        Math.max(game.homePitcher.projection.confidence, game.awayPitcher.projection.confidence) >= 75
      );
    }

    // Sort games
    games.sort((a, b) => {
      switch (sortBy) {
        case 'confidence':
          const aMaxConf = Math.max(a.homePitcher.projection.confidence, a.awayPitcher.projection.confidence);
          const bMaxConf = Math.max(b.homePitcher.projection.confidence, b.awayPitcher.projection.confidence);
          return bMaxConf - aMaxConf;
        case 'strikeouts':
          const aMaxK = Math.max(a.homePitcher.projection.strikeouts, a.awayPitcher.projection.strikeouts);
          const bMaxK = Math.max(b.homePitcher.projection.strikeouts, b.awayPitcher.projection.strikeouts);
          return bMaxK - aMaxK;
        case 'pitcher':
          return a.homePitcher.name.localeCompare(b.homePitcher.name);
        case 'time':
        default:
          return a.gameTime.localeCompare(b.gameTime);
      }
    });

    return games;
  }, [sortBy, filterBy]);

  return (
    <div className="app">
      <Header 
        darkMode={darkMode}
        toggleDarkMode={() => setDarkMode(!darkMode)}
        sortBy={sortBy}
        setSortBy={setSortBy}
        filterBy={filterBy}
        setFilterBy={setFilterBy}
      />
      
      <main className="main">
        <div className="container">
          <div className="games-grid">
            <AnimatePresence>
              {filteredAndSortedGames.map((game) => (
                <GameCard key={game.id} game={game} />
              ))}
            </AnimatePresence>
          </div>
          
          {filteredAndSortedGames.length === 0 && (
            <motion.div 
              className="no-games"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
            >
              <p>No games match your current filters.</p>
            </motion.div>
          )}
        </div>
      </main>
    </div>
  );
}

export default App;