import { motion } from 'framer-motion';
import { Search, MapPin, BookOpen, X } from 'lucide-react';

export default function Filters({ 
  searchQuery, setSearchQuery, 
  selectedCity, setSelectedCity, 
  selectedCategory, setSelectedCategory,
  cities, categories
}) {
  return (
    <motion.div 
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ duration: 0.5, delay: 0.1 }}
      className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6 space-y-6"
    >
      <div>
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Filters</h2>
        
        {/* Search */}
        <div className="relative mb-5">
          <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
            <Search className="h-4 w-4 text-gray-400" />
          </div>
          <input
            type="text"
            className="block w-full pl-10 pr-3 py-2.5 border border-gray-200 rounded-xl text-sm placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-shadow"
            placeholder="Search institutes..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
          {searchQuery && (
            <button 
              onClick={() => setSearchQuery('')}
              className="absolute inset-y-0 right-0 pr-3 flex items-center text-gray-400 hover:text-gray-600"
            >
              <X className="h-4 w-4" />
            </button>
          )}
        </div>

        {/* City Filter */}
        <div className="mb-5">
          <label className="flex items-center text-sm font-medium text-gray-700 mb-2">
            <MapPin className="w-4 h-4 mr-1.5 text-gray-400" />
            Region / City
          </label>
          <select
            className="block w-full py-2.5 px-3 border border-gray-200 bg-gray-50 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:bg-white transition-colors appearance-none"
            value={selectedCity}
            onChange={(e) => setSelectedCity(e.target.value)}
          >
            <option value="All">All Maharashtra</option>
            {cities.map(city => (
              <option key={city} value={city}>{city}</option>
            ))}
          </select>
        </div>

        {/* Category Filter */}
        <div>
          <label className="flex items-center text-sm font-medium text-gray-700 mb-2">
            <BookOpen className="w-4 h-4 mr-1.5 text-gray-400" />
            Category
          </label>
          <div className="flex flex-wrap gap-2">
            <button
              onClick={() => setSelectedCategory('All')}
              className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${
                selectedCategory === 'All' 
                  ? 'bg-blue-600 text-white shadow-sm' 
                  : 'bg-gray-50 text-gray-600 hover:bg-gray-100 border border-gray-200'
              }`}
            >
              All
            </button>
            {categories.map(cat => (
              <button
                key={cat}
                onClick={() => setSelectedCategory(cat)}
                className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${
                  selectedCategory === cat 
                    ? 'bg-blue-600 text-white shadow-sm' 
                    : 'bg-gray-50 text-gray-600 hover:bg-gray-100 border border-gray-200'
                }`}
              >
                {cat}
              </button>
            ))}
          </div>
        </div>
      </div>
    </motion.div>
  );
}
