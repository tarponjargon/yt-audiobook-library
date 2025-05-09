import { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { toast } from 'react-hot-toast'
import Spinner from '../components/Spinner'
import { fetchAudiobookDetail } from '../api'

function AudiobookDetailPage() {
  const { audiobookId } = useParams()
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
        toast.error('Failed to load audiobook details')
      } finally {
        setLoading(false)
      }
    }

    loadAudiobookDetail()
  }, [audiobookId])

  if (loading) {
    return (
      <div className="flex justify-center py-12">
        <Spinner size="large" />
      </div>
    )
  }

  if (!audiobook) {
    return (
      <div className="text-center py-12">
        <h2 className="text-2xl font-semibold mb-2">Audiobook not found</h2>
        <p className="text-gray-600">The audiobook you're looking for doesn't exist.</p>
      </div>
    )
  }

  return (
    <div className="max-w-4xl mx-auto">
      <div className="bg-white rounded-lg shadow-lg overflow-hidden">
        <div className="md:flex">
          <div className="md:w-1/3">
            <img 
              src={audiobook.thumbnail || '/placeholder-book.jpg'} 
              alt={audiobook.title}
              className="w-full h-auto object-cover"
            />
          </div>
          <div className="p-6 md:w-2/3">
            <h1 className="text-2xl font-bold mb-2">{audiobook.title}</h1>
            
            {audiobook.author && (
              <p className="text-gray-700 mb-4">
                <span className="font-semibold">Author:</span> {audiobook.author}
              </p>
            )}
            
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
            
            {audiobook.duration && (
              <p className="text-gray-700 mb-4">
                <span className="font-semibold">Duration:</span> {formatDuration(audiobook.duration)}
              </p>
            )}
            
            <div className="mt-6">
              <a 
                href={`https://www.youtube.com/watch?v=${audiobook.video_id}`}
                target="_blank"
                rel="noopener noreferrer"
                className="btn btn-primary"
              >
                Listen on YouTube
              </a>
            </div>
          </div>
        </div>
        
        {audiobook.description && (
          <div className="p-6 border-t">
            <h2 className="text-xl font-semibold mb-4">Description</h2>
            <div className="prose max-w-none text-gray-700 whitespace-pre-line">
              {audiobook.description}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

function formatDuration(seconds) {
  if (!seconds) return 'Unknown'
  
  const hours = Math.floor(seconds / 3600)
  const minutes = Math.floor((seconds % 3600) / 60)
  
  if (hours > 0) {
    return `${hours} hr ${minutes} min`
  }
  return `${minutes} min`
}

export default AudiobookDetailPage
