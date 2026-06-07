import { useState, useMemo } from 'react';
import Header from './components/Header';
import Filters from './components/Filters';
import InstituteList from './components/InstituteList';
import HeatMap from './components/HeatMap';

// Load static JSON data imported from the asset folder
import institutesData from './assets/institutes.json';

function App() {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCity, setSelectedCity] = useState('All');
  const [selectedCategory, setSelectedCategory] = useState('All');
  const [viewMode, setViewMode] = useState('map'); // 'map' or 'list'

  // Extract unique cities and categories for filters
  const cities = useMemo(() => {
    return [...new Set(institutesData.map(item => item.city))].sort();
  }, []);

  const categories = useMemo(() => {
    return [...new Set(institutesData.map(item => item.category))].sort();
  }, []);

  // Filter the data based on current state
  const filteredInstitutes = useMemo(() => {
    return institutesData.filter(inst => {
      const matchesSearch = inst.name.toLowerCase().includes(searchQuery.toLowerCase()) || 
                            inst.category.toLowerCase().includes(searchQuery.toLowerCase());
      const matchesCity = selectedCity === 'All' || inst.city === selectedCity;
      const matchesCategory = selectedCategory === 'All' || inst.category === selectedCategory;
      return matchesSearch && matchesCity && matchesCategory;
    });
  }, [searchQuery, selectedCity, selectedCategory]);

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col font-sans">
      <Header />

      <main className="flex-1 w-full max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="flex flex-col lg:flex-row gap-8 h-full">
          
          {/* Left Sidebar: Filters */}
          <div className="w-full lg:w-1/3 xl:w-1/4 flex-shrink-0">
            <Filters 
              searchQuery={searchQuery} setSearchQuery={setSearchQuery}
              selectedCity={selectedCity} setSelectedCity={setSelectedCity}
              selectedCategory={selectedCategory} setSelectedCategory={setSelectedCategory}
              cities={cities} categories={categories}
            />
            
            {/* View Mode Toggle (Mobile/Tablet friendly) */}
            <div className="mt-6 bg-white rounded-2xl p-2 shadow-sm border border-gray-100 flex gap-2">
              <button
                onClick={() => setViewMode('map')}
                className={`flex-1 py-2 text-sm font-medium rounded-xl transition-all ${
                  viewMode === 'map' ? 'bg-blue-50 text-blue-700 shadow-sm' : 'text-gray-500 hover:bg-gray-50'
                }`}
              >
                Heatmap View
              </button>
              <button
                onClick={() => setViewMode('list')}
                className={`flex-1 py-2 text-sm font-medium rounded-xl transition-all ${
                  viewMode === 'list' ? 'bg-blue-50 text-blue-700 shadow-sm' : 'text-gray-500 hover:bg-gray-50'
                }`}
              >
                List View
              </button>
            </div>

            <div className="mt-6">
              <p className="text-sm text-gray-500 text-center">
                Showing <strong className="text-gray-900">{filteredInstitutes.length}</strong> institutes
              </p>
            </div>
          </div>

          {/* Right Content Area: Map or List */}
          <div className="w-full lg:w-2/3 xl:w-3/4 h-[600px] lg:h-[800px] flex flex-col">
            {viewMode === 'map' ? (
              <HeatMap institutes={filteredInstitutes} selectedCity={selectedCity} />
            ) : (
              <div className="h-full overflow-y-auto pr-2 pb-10">
                <InstituteList institutes={filteredInstitutes} />
              </div>
            )}
          </div>

        </div>
      </main>
    </div>
  );
}

export default App;
