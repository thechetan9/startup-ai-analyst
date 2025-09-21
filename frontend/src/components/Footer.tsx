import React from 'react'

const Footer: React.FC = () => {
  return (
    <footer className="bg-gray-50 border-t border-gray-200 py-6 mt-12">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center">
          <p className="text-sm text-gray-600">
            Made with <span className="text-red-500">❤️</span> by <span className="font-semibold text-gray-800">Cosmos team</span>
          </p>
        </div>
      </div>
    </footer>
  )
}

export default Footer
