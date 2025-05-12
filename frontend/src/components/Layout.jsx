import { useState, useEffect } from 'react'
import { Outlet, Link, useNavigate } from 'react-router-dom'
import { useStore } from '../store'
import Spinner from './Spinner'
import { toast } from 'react-hot-toast'

function Layout() {
  const [searchQuery, setSearchQuery] = useState('')
  const navigate = useNavigate()
  const { categories, fetchCategories, loading } = useStore()

  useEffect(() => {
    fetchCategories().catch(error => {
      toast.error('Failed to load categories')
      console.error('Error fetching categories:', error)
    })
  }, [fetchCategories])

  const handleSearch = (e) => {
    e.preventDefault()
    if (searchQuery.trim()) {
      navigate(`/search?q=${encodeURIComponent(searchQuery.trim())}`)
    }
  }

  return (
    <div className="min-h-screen flex flex-col">
      <header className="bg-white shadow-md">
        <div className="container py-4">
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
            <Link to="/" className="text-2xl font-bold text-blue-600">
              YTAudioBookLib
            </Link>
            
            <form onSubmit={handleSearch} className="w-full md:w-1/3">
              <div className="relative">
                <input
                  type="text"
                  placeholder="Search audiobooks..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full px-4 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
                <button 
                  type="submit"
                  className="absolute right-2 top-1/2 transform -translate-y-1/2 text-gray-500 hover:text-blue-600"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                  </svg>
                </button>
              </div>
            </form>
          </div>
          
          <nav className="mt-4 relative">
            {loading ? (
              <div className="flex justify-center py-2">
                <Spinner />
              </div>
            ) : (
              <div className="relative">
                <button 
                  className="absolute left-0 top-1/2 transform -translate-y-1/2 bg-white bg-opacity-70 p-1 rounded-full shadow-md z-10 hover:bg-opacity-100"
                  onClick={() => {
                    const container = document.getElementById('categories-carousel');
                    container.scrollBy({ left: -200, behavior: 'smooth' });
                  }}
                >
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
                  </svg>
                </button>
                
                <div 
                  id="categories-carousel"
                  className="overflow-x-auto scrollbar-hide flex space-x-6 pb-2 px-6 scroll-smooth"
                  style={{ 
                    msOverflowStyle: 'none', 
                    scrollbarWidth: 'none',
                    WebkitOverflowScrolling: 'touch'
                  }}
                >
                  {categories.map(category => (
                    <div key={category.id} className="flex-shrink-0">
                      <Link 
                        to={`/category/${category.id}`}
                        className="whitespace-nowrap text-gray-700 hover:text-blue-600 hover:underline"
                      >
                        {category.name}
                      </Link>
                    </div>
                  ))}
                </div>
                
                <button 
                  className="absolute right-0 top-1/2 transform -translate-y-1/2 bg-white bg-opacity-70 p-1 rounded-full shadow-md z-10 hover:bg-opacity-100"
                  onClick={() => {
                    const container = document.getElementById('categories-carousel');
                    container.scrollBy({ left: 200, behavior: 'smooth' });
                  }}
                >
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                  </svg>
                </button>
              </div>
            )}
          </nav>
        </div>
      </header>
      
      <main className="flex-grow container py-8">
        <Outlet />
      </main>
      
      <footer className="bg-gray-100 py-6">
        <div className="container text-center text-gray-600">
          <p>&copy; {new Date().getFullYear()} YTAudioBookLib</p>
        </div>
      </footer>
    </div>
  )
}

export default Layout
