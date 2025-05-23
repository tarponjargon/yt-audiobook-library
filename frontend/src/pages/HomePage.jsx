import { useEffect, useState, useRef, useCallback } from 'react'
import { toast } from 'react-hot-toast'
import AudiobookGrid from '../components/AudiobookGrid'
import Spinner from '../components/Spinner'
import { fetchAllAudiobooks, fetchAudiobookCount } from '../api'

function HomePage() {
  const [audiobooks, setAudiobooks] = useState([])
  const [loading, setLoading] = useState(true)
  const [loadingMore, setLoadingMore] = useState(false)
  const [totalBooks, setTotalBooks] = useState(0)
  const [pagination, setPagination] = useState({
    page: 1,
    hasNext: false,
    total: 0
  })
  const observer = useRef()

  // Setup intersection observer for infinite scroll
  const lastAudiobookElementRef = useCallback(node => {
    if (loading || loadingMore) return
    if (observer.current) observer.current.disconnect()

    observer.current = new IntersectionObserver(entries => {
      if (entries[0].isIntersecting && pagination.hasNext) {
        loadMoreAudiobooks()
      }
    })

    if (node) observer.current.observe(node)
  }, [loading, loadingMore, pagination.hasNext])

  // Load initial audiobooks
  useEffect(() => {
    const loadInitialData = async () => {
      try {
        setLoading(true)

        // Fetch both the audiobooks and the total count
        try {
          const [audiobooksData, countData] = await Promise.all([
            fetchAllAudiobooks(1),
            fetchAudiobookCount()
          ])

          setAudiobooks(audiobooksData.audiobooks)
          setTotalBooks(countData?.count || 0)
          setPagination({
            page: audiobooksData.pagination.page,
            hasNext: audiobooksData.pagination.has_next,
            total: audiobooksData.pagination.total
          })
        } catch (error) {
          console.error('Error fetching data:', error)
          toast.error('Failed to load audiobooks')
        }
      } finally {
        setLoading(false)
      }
    }

    loadInitialData()
  }, [])

  // Function to load more audiobooks when scrolling
  const loadMoreAudiobooks = async () => {
    if (!pagination.hasNext || loadingMore) return

    try {
      setLoadingMore(true)
      const nextPage = pagination.page + 1
      const data = await fetchAllAudiobooks(nextPage)

      setAudiobooks(prev => [...prev, ...data.audiobooks])
      setPagination({
        page: data.pagination.page,
        hasNext: data.pagination.has_next,
        total: data.pagination.total
      })
    } catch (error) {
      console.error('Error loading more audiobooks:', error)
      toast.error('Failed to load more audiobooks')
    } finally {
      setLoadingMore(false)
    }
  }

  return (
    <div>
      <section className="mb-10">
        <h1 className="text-3xl font-bold mb-2">Welcome to YT-Audiobooks</h1>
        <p className="text-gray-600 mb-2">
          YT-Audiobooks helps you find audiobooks more easily. This web application collects audiobook information from YouTube and organizes it in a clean, searchable interface.
        </p>
        <p className="text-gray-600 font-semibold mb-6">
          Our library currently contains {totalBooks.toLocaleString()} audiobooks and growing!
        </p>
        <div className="bg-gray-50 p-4 rounded-lg border border-gray-200 mb-6">
          <h2 className="text-xl font-semibold mb-2">With YT-Audiobooks, you can:</h2>
          <ul className="list-disc pl-5 space-y-1">
            <li>Browse audiobooks by category</li>
            <li>Search for specific titles or topics</li>
            <li>Explore works from your favorite authors</li>
            <li>See important details like duration at a glance</li>
            <li>Discover new audiobooks with random suggestions</li>
          </ul>
        </div>
      </section>

      <section>
        <h2 className="text-2xl font-semibold mb-6">Browse All Audiobooks</h2>

        {loading ? (
          <div className="flex justify-center py-12">
            <Spinner size="large" />
          </div>
        ) : (
          <>
            <AudiobookGrid
              audiobooks={audiobooks}
              lastAudiobookRef={lastAudiobookElementRef}
            />

            {loadingMore && (
              <div className="flex justify-center py-4">
                <Spinner />
              </div>
            )}

            {!pagination.hasNext && audiobooks.length > 0 && (
              <p className="text-center text-gray-500 mt-8 mb-4">
                You've reached the end of the list
              </p>
            )}
          </>
        )}
      </section>
    </div>
  )
}

export default HomePage
