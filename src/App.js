import { useState, useMemo, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import Header from './components/Header';
import GameCard from './components/GameCard';
import './App.css';

function App() {
  const [darkMode, setDarkMode] = useState(true);
  const [sortBy, setSortBy] = useState('confidence');
  const [filterBy, setFilterBy] = useState('all');
  const [games, setGames] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', darkMode ? 'dark' : 'light');
  }, [darkMode]);

  useEffect(() => {
    fetchGames();
  }, []);

  const fetchGames = async () => {
    try {
      setLoading(true);
      const response = await fetch('http://localhost:8000/api/games/today');
      if (!response.ok) throw new Error('Failed to fetch games');
      const data = await response.json();
      console.log('API Response:', data);
      if (data.error) {
        setError(data.error);
        setGames([]);
      } else {
        setGames(data);
        setError(null);
      }
    } catch (err) {
      setError(err.message);
      console.error('Error fetching games:', err);
    } finally {
      setLoading(false);
    }
  };

  const filteredAndSortedGames = useMemo(() => {
    let gamesList = [...games];

    // Filter games
    if (filterBy === 'elite') {
      gamesList = gamesList.filter(game => 
        Math.max(game.homePitcher.projection.projected_strikeouts, game.awayPitcher.projection.projected_strikeouts) >= 8.5
      );
    } else if (filterBy === 'high-confidence') {
      gamesList = gamesList.filter(game => 
        Math.max(game.homePitcher.projection.confidence, game.awayPitcher.projection.confidence) >= 75
      );
    }

    // Sort games
    gamesList.sort((a, b) => {
      switch (sortBy) {
        case 'confidence':
          const aMaxConf = Math.max(a.homePitcher.projection.confidence, a.awayPitcher.projection.confidence);
          const bMaxConf = Math.max(b.homePitcher.projection.confidence, b.awayPitcher.projection.confidence);
          return bMaxConf - aMaxConf;
        case 'strikeouts':
          const aMaxK = Math.max(a.homePitcher.projection.projected_strikeouts, a.awayPitcher.projection.projected_strikeouts);
          const bMaxK = Math.max(b.homePitcher.projection.projected_strikeouts, b.awayPitcher.projection.projected_strikeouts);
          return bMaxK - aMaxK;
        case 'pitcher':
          return a.homePitcher.name.localeCompare(b.homePitcher.name);
        case 'time':
        default:
          return a.gameTime.localeCompare(b.gameTime);
      }
    });

    return gamesList;
  }, [games, sortBy, filterBy]);

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
          {loading && (
            <motion.div 
              className="loading"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
            >
              <p>Loading today's games...</p>
            </motion.div>
          )}
          
          {error && (
            <motion.div 
              className="error"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
            >
              <p>Error: {error}</p>
              <button onClick={fetchGames} className="retry-btn">Retry</button>
            </motion.div>
          )}
          
          {!loading && !error && (
            <>
              <div className="games-grid">
                <AnimatePresence>
                  {filteredAndSortedGames.map((game) => (
                    <GameCard key={game.id} game={game} />
                  ))}
                </AnimatePresence>
              </div>
              
              {filteredAndSortedGames.length === 0 && games.length > 0 && (
                <motion.div 
                  className="no-games"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                >
                  <p>No games match your current filters.</p>
                </motion.div>
              )}
            </>
          )}
        </div>
      </main>
    </div>
  );
}

export default App;