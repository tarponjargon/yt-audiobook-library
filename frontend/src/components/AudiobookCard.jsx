import { useState, useEffect } from 'react'
import AudiobookModal from './AudiobookModal'
import { useAuth } from '../context/AuthContext'
import * as api from '../api'
import { toast } from 'react-hot-toast'

function AudiobookCard({ audiobook }) {
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [isFavorite, setIsFavorite] = useState(false)
  const { isAuthenticated } = useAuth()
  
  const openModal = () => setIsModalOpen(true)
  const closeModal = () => setIsModalOpen(false)
  
  useEffect(() => {
    // Check if audiobook is in favorites
    const checkFavorite = async () => {
      if (!isAuthenticated) return;
      
      try {
        const response = await api.get(`/api/favorites/check/${audiobook.id}`);
        setIsFavorite(response.data.is_favorite);
      } catch (error) {
        console.error('Error checking favorite status:', error);
      }
    };
    
    checkFavorite();
  }, [audiobook.id, isAuthenticated]);
  
  const toggleFavorite = async (e) => {
    e.stopPropagation(); // Prevent opening the modal
    
    if (!isAuthenticated) {
      toast.info('Please login to add favorites');
      return;
    }
    
    try {
      if (isFavorite) {
        await api.delete(`/api/favorites/${audiobook.id}`);
        toast.success('Removed from favorites');
      } else {
        await api.post(`/api/favorites/${audiobook.id}`);
        toast.success('Added to favorites');
      }
      setIsFavorite(!isFavorite);
    } catch (error) {
      console.error('Error toggling favorite:', error);
      toast.error('Failed to update favorites');
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
            {audiobook.author && (
              <p className="text-gray-600 text-sm mt-auto">
                By {audiobook.author}
              </p>
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
