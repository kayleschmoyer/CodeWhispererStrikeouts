import { Moon, Sun, Filter, Search } from 'lucide-react';
import { motion } from 'framer-motion';

const Header = ({ darkMode, toggleDarkMode, sortBy, setSortBy, filterBy, setFilterBy }) => {
  return (
    <header className="header">
      <div className="container">
        <div className="header-content">
          <div className="header-left">
            <h1>MLB Strikeout Predictions</h1>
            <p className="header-subtitle">Today's Elite Pitching Matchups</p>
          </div>
          
          <div className="header-controls">
            <div className="filter-controls">
              <div className="control-group">
                <Filter size={16} />
                <select 
                  value={sortBy} 
                  onChange={(e) => setSortBy(e.target.value)}
                  className="control-select"
                >
                  <option value="confidence">Confidence</option>
                  <option value="strikeouts">Projected K's</option>
                  <option value="time">Game Time</option>
                  <option value="pitcher">Pitcher Name</option>
                </select>
              </div>
              
              <div className="control-group">
                <Search size={16} />
                <select 
                  value={filterBy} 
                  onChange={(e) => setFilterBy(e.target.value)}
                  className="control-select"
                >
                  <option value="all">All Games</option>
                  <option value="elite">Elite Picks (8.5+ K)</option>
                  <option value="high-confidence">High Confidence (75%+)</option>
                </select>
              </div>
            </div>
            
            <motion.button
              className="theme-toggle"
              onClick={toggleDarkMode}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              {darkMode ? <Sun size={20} /> : <Moon size={20} />}
            </motion.button>
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;