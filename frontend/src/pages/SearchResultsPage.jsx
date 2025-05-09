import { useEffect, useState, useRef, useCallback } from 'react'
import { useSearchParams } from 'react-router-dom'
import { toast } from 'react-hot-toast'
import AudiobookGrid from '../components/AudiobookGrid'
import Spinner from '../components/Spinner'
import { searchAudiobooks } from '../api'

function SearchResultsPage() {
  const [searchParams] = useSearchParams()
  const query = searchParams.get('q') || ''
  
  const [audiobooks, setAudiobooks] = useState([])
  const [loading, setLoading] = useState(true)
  const [loadingMore, setLoadingMore] = useState(false)
  const [pagination, setPagination] = useState({
    page: 1,
    hasNext: false,
    total: 0
  })
  
  const observer = useRef()
  const loadMoreRef = useCallback(node => {
    if (loadingMore) return
    if (observer.current) observer.current.disconnect()
    
    observer.current = new IntersectionObserver(entries => {
      if (entries[0].isIntersecting && pagination.hasNext) {
        loadMoreAudiobooks()
      }
    })
    
    if (node) observer.current.observe(node)
  }, [loadingMore, pagination.hasNext])

  useEffect(() => {
    const performSearch = async () => {
      if (!query) return
      
      try {
        setLoading(true)
        setAudiobooks([])
        setPagination({ page: 1, hasNext: false, total: 0 })
        
        const data = await searchAudiobooks(query, 1)
        setAudiobooks(data.audiobooks)
        setPagination({
          page: data.pagination.page,
          hasNext: data.pagination.has_next,
          total: data.pagination.total
        })
      } catch (error) {
        console.error('Error searching audiobooks:', error)
        toast.error('Failed to search audiobooks')
      } finally {
        setLoading(false)
      }
    }

    performSearch()
  }, [query])

  const loadMoreAudiobooks = async () => {
    if (!pagination.hasNext || loadingMore) return
    
    try {
      setLoadingMore(true)
      const nextPage = pagination.page + 1
      const data = await searchAudiobooks(query, nextPage)
      
      setAudiobooks(prev => [...prev, ...data.audiobooks])
      setPagination({
        page: data.pagination.page,
        hasNext: data.pagination.has_next,
        total: data.pagination.total
      })
    } catch (error) {
      console.error('Error loading more search results:', error)
      toast.error('Failed to load more results')
    } finally {
      setLoadingMore(false)
    }
  }

  if (!query) {
    return (
      <div className="text-center py-12">
        <h2 className="text-2xl font-semibold mb-2">No search query</h2>
        <p className="text-gray-600">Please enter a search term to find audiobooks.</p>
      </div>
    )
  }

  return (
    <div>
      <h1 className="text-3xl font-bold mb-2">Search Results</h1>
      <p className="text-gray-600 mb-8">
        {loading ? 'Searching...' : `Found ${pagination.total} results for "${query}"`}
      </p>
      
      {loading ? (
        <div className="flex justify-center py-12">
          <Spinner size="large" />
        </div>
      ) : (
        <>
          <AudiobookGrid audiobooks={audiobooks} />
          
          {pagination.hasNext && (
            <div 
              ref={loadMoreRef} 
              className="flex justify-center mt-8 py-4"
            >
              {loadingMore && <Spinner />}
            </div>
          )}
        </>
      )}
    </div>
  )
}

export default SearchResultsPage
