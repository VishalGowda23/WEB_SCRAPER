import { motion } from 'framer-motion';
import { GraduationCap } from 'lucide-react';

export default function Header() {
  return (
    <motion.header 
      initial={{ opacity: 0, y: -20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className="bg-white border-b border-gray-100 shadow-sm sticky top-0 z-50"
    >
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          <div className="flex items-center gap-3">
            <div className="bg-blue-50 p-2 rounded-xl text-blue-600">
              <GraduationCap className="w-6 h-6" />
            </div>
            <div>
              <h1 className="text-xl font-bold text-gray-900 leading-tight">Commerce Classes</h1>
              <p className="text-xs text-gray-500 font-medium">Maharashtra Education Directory</p>
            </div>
          </div>
        </div>
      </div>
    </motion.header>
  );
}
