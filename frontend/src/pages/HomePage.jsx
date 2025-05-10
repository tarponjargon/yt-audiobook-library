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
        <h1 className="text-3xl font-bold mb-2">Welcome to AudioBookFinder</h1>
        <p className="text-gray-600 mb-6">
          AudioBookFinder helps you find audiobooks more easily. This web application collects audiobook information from YouTube and organizes it in a clean, searchable interface.
        </p>
        <div className="bg-gray-50 p-4 rounded-lg border border-gray-200 mb-6">
          <h2 className="text-xl font-semibold mb-2">With AudioBookFinder, you can:</h2>
          <ul className="list-disc pl-5 space-y-1">
            <li>Browse audiobooks by category</li>
            <li>Search for specific titles or topics</li>
            <li>Explore works from your favorite authors</li>
            <li>See important details like duration at a glance</li>
            <li>Discover new audiobooks with random suggestions</li>
          </ul>
        </div>
        <p className="text-gray-600">
          The application automatically processes YouTube content to identify audiobooks, categorizes them appropriately, and presents them in a straightforward, easy-to-navigate website that works well on both desktop and mobile devices.
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
