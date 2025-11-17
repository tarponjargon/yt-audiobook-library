import { useState, useEffect } from 'react'
import AudiobookModal from './AudiobookModal'
import { useAuth } from '../context/AuthContext'
import api from '../api'
import { toast } from 'react-hot-toast'

function AudiobookCard({ audiobook }) {
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [isFavorite, setIsFavorite] = useState(false)
  const [inMyBooks, setInMyBooks] = useState(false)
  const { isAuthenticated } = useAuth()

  const openModal = () => setIsModalOpen(true)
  const closeModal = () => setIsModalOpen(false)

  useEffect(() => {
    // Check if audiobook is in favorites
    const checkFavorite = async () => {
      if (!isAuthenticated) return;

      try {
        const response = await api.get(`/favorites/check/${audiobook.id}`);
        setIsFavorite(response.is_favorite);
      } catch (error) {
        console.error('Error checking favorite status:', error);
      }
    };

    // Check if audiobook is in My Books
    const checkMyBooks = async () => {
      if (!isAuthenticated) return;

      try {
        const response = await api.get(`/user-books/check/${audiobook.id}`);
        setInMyBooks(response.in_library);
      } catch (error) {
        console.error('Error checking My Books status:', error);
      }
    };

    checkFavorite();
    checkMyBooks();
  }, [audiobook.id, isAuthenticated]);
  
  const toggleFavorite = async (e) => {
    e.stopPropagation();

    if (!isAuthenticated) {
      toast.info('Please login to add favorites');
      return;
    }

    try {
      if (isFavorite) {
        await api.delete(`/favorites/${audiobook.id}`);
        toast.success('Removed from favorites');
      } else {
        await api.post(`/favorites/${audiobook.id}`);
        toast.success('Added to favorites');
      }
      setIsFavorite(!isFavorite);
    } catch (error) {
      console.error('Error toggling favorite:', error);
      toast.error('Failed to update favorites');
    }
  };

  const addToMyBooks = async (e) => {
    e.stopPropagation();

    if (!isAuthenticated) {
      toast.info('Please login to add books to your library');
      return;
    }

    if (inMyBooks) {
      return;
    }

    try {
      await api.post(`/user-books/${audiobook.id}`);
      toast.success('Added to My Books');
      setInMyBooks(true);
    } catch (error) {
      console.error('Error adding to My Books:', error);
      toast.error('Failed to add to My Books');
    }
  };

  return (
    <>
      <div onClick={openModal} className="cursor-pointer">
        <div className="card h-full flex flex-col relative">
          <div className="relative pb-[56.25%]">
            <img
              src={audiobook.thumbnail || '/placeholder-book.jpg'}
              alt={audiobook.title}
              className="absolute inset-0 w-full h-full object-cover"
            />
            
            {/* Add favorite button */}
            {isAuthenticated && (
              <button 
                onClick={toggleFavorite}
                className="absolute top-2 right-2 p-1 bg-white rounded-full shadow-md z-10"
              >
                {isFavorite ? (
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 text-red-500" viewBox="0 0 20 20" fill="currentColor">
                    <path fillRule="evenodd" d="M3.172 5.172a4 4 0 015.656 0L10 6.343l1.172-1.171a4 4 0 115.656 5.656L10 17.657l-6.828-6.829a4 4 0 010-5.656z" clipRule="evenodd" />
                  </svg>
                ) : (
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
                  </svg>
                )}
              </button>
            )}
          </div>
          <div className="p-4 flex-grow flex flex-col">
            <h3 className="font-semibold text-lg line-clamp-2 mb-1">{audiobook.title}</h3>
            {audiobook.rating && (
              <div className="flex items-center gap-1 my-1">
                {[...Array(5)].map((_, index) => {
                  const starValue = index + 1;
                  const isFilled = starValue <= Math.round(audiobook.rating);
                  return (
                    <svg
                      key={index}
                      xmlns="http://www.w3.org/2000/svg"
                      className="h-4 w-4"
                      viewBox="0 0 20 20"
                      fill={isFilled ? "#FBBF24" : "#D1D5DB"}
                    >
                      <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                    </svg>
                  );
                })}
                <span className="text-xs text-gray-600 ml-1">({audiobook.rating.toFixed(1)})</span>
              </div>
            )}
            {audiobook.author && (
              <p className="text-gray-600 text-sm mt-auto">
                By {audiobook.author}
              </p>
            )}
            {isAuthenticated && (
              <button
                onClick={addToMyBooks}
                disabled={inMyBooks}
                className={`mt-2 w-full py-2 px-4 rounded text-sm font-medium transition-colors ${
                  inMyBooks
                    ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                    : 'bg-blue-500 text-white hover:bg-blue-600'
                }`}
              >
                {inMyBooks ? 'Added' : 'Add to My Books'}
              </button>
            )}
          </div>
        </div>
      </div>

      {isModalOpen && (
        <AudiobookModal 
          audiobookId={audiobook.id} 
          onClose={closeModal} 
        />
      )}
    </>
  )
}

export default AudiobookCard
