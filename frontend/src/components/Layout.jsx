import { useState, useEffect, useRef } from 'react'
import { Outlet, Link, useNavigate } from 'react-router-dom'
import { useStore } from '../store'
import Spinner from './Spinner'
import { toast } from 'react-hot-toast'
import { useAuth } from '../context/AuthContext'

function Layout() {
  const [isSticky, setIsSticky] = useState(false)
  const headerRef = useRef(null)
  const [searchQuery, setSearchQuery] = useState('')
  const navigate = useNavigate()
  const { categories, fetchCategories, loading } = useStore()
  const { user, logout, isAuthenticated } = useAuth()

  useEffect(() => {
    fetchCategories().catch(error => {
      toast.error('Failed to load categories')
      console.error('Error fetching categories:', error)
    })
  }, [fetchCategories])

  // Handle sticky header on scroll
  useEffect(() => {
    const handleScroll = () => {
      // Only apply sticky behavior on desktop
      if (window.innerWidth >= 768) {
        if (headerRef.current) {
          setIsSticky(window.scrollY > 10)
        }
      } else {
        setIsSticky(false)
      }
    }

    window.addEventListener('scroll', handleScroll)
    // Check initial state
    handleScroll()
    
    return () => {
      window.removeEventListener('scroll', handleScroll)
    }
  }, [])

  const handleSearch = (e) => {
    e.preventDefault()
    if (searchQuery.trim()) {
      navigate(`/search?q=${encodeURIComponent(searchQuery.trim())}`)
    }
  }

  // Define the animation style
  const slideDownAnimation = `
    @keyframes slideDown {
      from {
        transform: translateY(-100%);
      }
      to {
        transform: translateY(0);
      }
    }
    .animate-slideDown {
      animation: slideDown 0.3s ease-in-out;
    }
  `;

  return (
    <div className="min-h-screen flex flex-col">
      <style>{slideDownAnimation}</style>
      <header 
        ref={headerRef}
        className={`bg-white shadow-md ${
          isSticky 
            ? 'md:fixed md:top-0 md:left-0 md:right-0 md:z-50 md:animate-slideDown' 
            : ''
        }`}
      >
        <div className="container py-4">
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
            <Link to="/" className="text-2xl font-bold text-blue-600">
              YTAudiobookLib
            </Link>

            <div className="flex items-center gap-4">
              <form onSubmit={handleSearch} className="w-full md:w-auto">
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
              
              {/* Auth links */}
              {isAuthenticated ? (
                <div className="relative group">
                  <button className="flex items-center space-x-1">
                    <span>{user.username}</span>
                    <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                    </svg>
                  </button>
                  <div className="absolute right-0 mt-2 w-48 bg-white rounded-md shadow-lg py-1 z-10 hidden group-hover:block">
                    <Link to="/favorites" className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100">
                      My Favorites
                    </Link>
                    <button 
                      onClick={logout} 
                      className="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                    >
                      Logout
                    </button>
                  </div>
                </div>
              ) : (
                <div className="flex space-x-2">
                  <Link to="/login" className="px-4 py-2 text-sm font-medium text-gray-700 hover:text-blue-600">Login</Link>
                  <Link to="/register" className="px-4 py-2 text-sm font-medium bg-blue-500 text-white rounded hover:bg-blue-600">Register</Link>
                </div>
              )}
            </div>
          </div>

          <nav className="mt-4 relative group">
            {loading ? (
              <div className="flex justify-center py-2">
                <Spinner />
              </div>
            ) : (
              <div className="relative">
                <button
                  className="absolute left-0 top-1/2 transform -translate-y-1/2 bg-white bg-opacity-70 p-1 rounded-full shadow-md z-10 hover:bg-opacity-100 opacity-0 group-hover:opacity-100 transition-opacity duration-200"
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
                  className="absolute right-0 top-1/2 transform -translate-y-1/2 bg-white bg-opacity-70 p-1 rounded-full shadow-md z-10 hover:bg-opacity-100 opacity-0 group-hover:opacity-100 transition-opacity duration-200"
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

      {isSticky && <div className="md:h-[132px]"></div>}
      <main className="flex-grow container py-8">
        <Outlet />
      </main>

      <footer className="bg-gray-100 py-6">
        <div className="container text-center text-gray-600">
          <p>&copy; {new Date().getFullYear()} YTAudiobookLib</p>
        </div>
      </footer>
    </div>
  )
}

export default Layout
