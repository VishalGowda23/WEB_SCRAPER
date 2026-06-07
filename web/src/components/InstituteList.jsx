import { motion, AnimatePresence } from 'framer-motion';
import { Phone, ExternalLink, MapPin } from 'lucide-react';

export default function InstituteList({ institutes }) {
  if (institutes.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-12 text-center bg-white rounded-2xl shadow-sm border border-gray-100 h-64">
        <MapPin className="w-12 h-12 text-gray-300 mb-3" />
        <h3 className="text-lg font-medium text-gray-900">No institutes found</h3>
        <p className="text-gray-500 mt-1">Try adjusting your search or filters.</p>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 xl:grid-cols-2 gap-4">
      <AnimatePresence>
        {institutes.map((inst, index) => (
          <motion.div
            key={inst.id}
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.95 }}
            transition={{ duration: 0.2, delay: index < 10 ? index * 0.05 : 0 }}
            className="bg-white p-5 rounded-2xl border border-gray-100 shadow-sm hover:shadow-md transition-all duration-300 flex flex-col justify-between"
          >
            <div>
              <div className="flex justify-between items-start mb-2">
                <span className="inline-block px-2.5 py-1 bg-blue-50 text-blue-700 text-xs font-semibold rounded-lg mb-2">
                  {inst.category}
                </span>
                <span className="text-xs font-medium text-gray-400 bg-gray-50 px-2 py-1 rounded-md">
                  {inst.city}
                </span>
              </div>
              <h3 className="text-[15px] font-bold text-gray-900 leading-tight mb-3 line-clamp-2" title={inst.name}>
                {inst.name}
              </h3>
            </div>
            
            <div className="flex flex-col gap-2 mt-auto pt-4 border-t border-gray-50">
              {inst.phone ? (
                <div className="flex items-center text-sm text-gray-600">
                  <Phone className="w-4 h-4 mr-2 text-gray-400" />
                  <a href={`tel:${inst.phone}`} className="hover:text-blue-600 transition-colors">
                    {inst.phone}
                  </a>
                </div>
              ) : (
                <div className="flex items-center text-sm text-gray-400 italic">
                  <Phone className="w-4 h-4 mr-2 opacity-50" />
                  No phone available
                </div>
              )}
              
              <div className="flex justify-between items-center mt-2">
                <a 
                  href={inst.website || inst.source_url} 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="inline-flex items-center text-xs font-medium text-blue-600 hover:text-blue-800 transition-colors"
                >
                  Visit Website
                  <ExternalLink className="w-3 h-3 ml-1" />
                </a>
              </div>
            </div>
          </motion.div>
        ))}
      </AnimatePresence>
    </div>
  );
}
