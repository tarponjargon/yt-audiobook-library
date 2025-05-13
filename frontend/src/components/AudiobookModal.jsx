import { useEffect, useState } from 'react'
import { fetchAudiobookDetail } from '../api'
import Spinner from './Spinner'

function formatDuration(seconds) {
  if (!seconds) return 'Unknown'

  const hours = Math.floor(seconds / 3600)
  const minutes = Math.floor((seconds % 3600) / 60)

  if (hours > 0) {
    return `${hours} hr ${minutes} min`
  }
  return `${minutes} min`
}

function AudiobookModal({ audiobookId, onClose }) {
  const [audiobook, setAudiobook] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const loadAudiobookDetail = async () => {
      try {
        setLoading(true)
        const data = await fetchAudiobookDetail(audiobookId)
        setAudiobook(data)
      } catch (error) {
        console.error('Error fetching audiobook details:', error)
      } finally {
        setLoading(false)
      }
    }

    if (audiobookId) {
      loadAudiobookDetail()
    }

    // Add event listener for ESC key
    const handleEscKey = (event) => {
      if (event.key === 'Escape') {
        onClose()
      }
    }
    
    window.addEventListener('keydown', handleEscKey)
    
    // Clean up event listener
    return () => {
      window.removeEventListener('keydown', handleEscKey)
    }
  }, [audiobookId, onClose])

  // Handle click outside to close
  const handleBackdropClick = (e) => {
    if (e.target === e.currentTarget) {
      onClose()
    }
  }

  return (
    <div
      className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4"
      onClick={handleBackdropClick}
    >
      <div className="bg-white rounded-lg max-w-4xl w-full max-h-[90vh] overflow-y-auto">
        {loading ? (
          <div className="flex justify-center items-center h-64">
            <Spinner size="large" />
          </div>
        ) : audiobook ? (
          <div className="p-6">
            <div className="flex justify-between items-start mb-4">
              <h2 className="text-2xl font-bold">{audiobook.title}</h2>
              <button
                onClick={onClose}
                className="text-gray-500 hover:text-gray-700"
              >
                <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="md:col-span-1">
                <img
                  src={audiobook.thumbnail || '/placeholder-book.jpg'}
                  alt={audiobook.title}
                  className="w-full rounded-lg shadow-md"
                />

                {audiobook.youtube_url && (
                  <a
                    href={audiobook.youtube_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="mt-4 btn btn-primary w-full flex items-center justify-center"
                  >
                    <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-2" viewBox="0 0 20 20" fill="currentColor">
                      <path d="M10 12a2 2 0 100-4 2 2 0 000 4z" />
                      <path fillRule="evenodd" d="M.458 10C1.732 5.943 5.522 3 10 3s8.268 2.943 9.542 7c-1.274 4.057-5.064 7-9.542 7S1.732 14.057.458 10zM14 10a4 4 0 11-8 0 4 4 0 018 0z" clipRule="evenodd" />
                    </svg>
                    Listen on YouTube
                  </a>
                )}
              </div>

              <div className="md:col-span-2">
                {audiobook.author && (
                  <div className="mb-4">
                    <h3 className="text-lg font-semibold">Author</h3>
                    <p>{audiobook.author}</p>
                  </div>
                )}

                {audiobook.description && (
                  <div className="mb-4">
                    <h3 className="text-lg font-semibold">Description</h3>
                    <p className="text-gray-700">{audiobook.description}</p>
                  </div>
                )}

                <div className="grid grid-cols-2 gap-4">
                  {audiobook.duration_seconds && (
                    <div>
                      <h3 className="text-lg font-semibold">Duration</h3>
                      <p>{formatDuration(audiobook.duration_seconds)}</p>
                    </div>
                  )}

                  {audiobook.language && (
                    <div>
                      <h3 className="text-lg font-semibold">Language</h3>
                      <p>{audiobook.language}</p>
                    </div>
                  )}
                </div>

                {audiobook.categories && audiobook.categories.length > 0 && (
                  <div className="mb-4">
                    <span className="font-semibold">Categories:</span>
                    <div className="flex flex-wrap gap-2 mt-1">
                      {audiobook.categories.map(category => (
                        <span key={category} className="bg-blue-100 text-blue-800 px-2 py-1 rounded text-sm">
                          {category}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        ) : (
          <div className="p-6 text-center">
            <p className="text-gray-500">Audiobook not found</p>
          </div>
        )}
      </div>
    </div>
  )
}

export default AudiobookModal
