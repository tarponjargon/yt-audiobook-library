import { useEffect, useState } from 'react'
import { toast } from 'react-hot-toast'
import AudiobookGrid from '../components/AudiobookGrid'
import Spinner from '../components/Spinner'
import { fetchRandomAudiobooks } from '../api'

function HomePage() {
  const [audiobooks, setAudiobooks] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const loadRandomAudiobooks = async () => {
      try {
        setLoading(true)
        const data = await fetchRandomAudiobooks(5)
        setAudiobooks(data.audiobooks)
      } catch (error) {
        console.error('Error fetching random audiobooks:', error)
        toast.error('Failed to load audiobooks')
      } finally {
        setLoading(false)
      }
    }

    loadRandomAudiobooks()
  }, [])

  return (
    <div>
      <section className="mb-10">
        <h1 className="text-3xl font-bold mb-2">Welcome to YTAudioBookLib</h1>
        <p className="text-gray-600 mb-6">
          Discover and enjoy a curated collection of audiobooks from YouTube.
          Browse by category, search for your favorite titles, or explore our recommendations.
        </p>
      </section>

      <section>
        <h2 className="text-2xl font-semibold mb-6">Featured Audiobooks</h2>
        
        {loading ? (
          <div className="flex justify-center py-12">
            <Spinner size="large" />
          </div>
        ) : (
          <AudiobookGrid audiobooks={audiobooks} />
        )}
      </section>
    </div>
  )
}

export default HomePage
