import { useEffect, useState, useRef, useCallback } from 'react'
import { useParams } from 'react-router-dom'
import { toast } from 'react-hot-toast'
import AudiobookGrid from '../components/AudiobookGrid'
import Spinner from '../components/Spinner'
import { fetchCategoryAudiobooks } from '../api'

function CategoryPage() {
  const { categoryId } = useParams()
  const [category, setCategory] = useState(null)
  const [audiobooks, setAudiobooks] = useState([])
  const [loading, setLoading] = useState(true)
  const [loadingMore, setLoadingMore] = useState(false)
  const [pagination, setPagination] = useState({
    page: 1,
    hasNext: false
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
    const loadCategory = async () => {
      try {
        setLoading(true)
        setAudiobooks([])
        setPagination({ page: 1, hasNext: false })
        
        const data = await fetchCategoryAudiobooks(categoryId, 1)
        setCategory(data.category)
        setAudiobooks(data.audiobooks)
        setPagination({
          page: data.pagination.page,
          hasNext: data.pagination.has_next
        })
      } catch (error) {
        console.error('Error fetching category:', error)
        toast.error('Failed to load category')
      } finally {
        setLoading(false)
      }
    }

    loadCategory()
  }, [categoryId])

  const loadMoreAudiobooks = async () => {
    if (!pagination.hasNext || loadingMore) return
    
    try {
      setLoadingMore(true)
      const nextPage = pagination.page + 1
      const data = await fetchCategoryAudiobooks(categoryId, nextPage)
      
      setAudiobooks(prev => [...prev, ...data.audiobooks])
      setPagination({
        page: data.pagination.page,
        hasNext: data.pagination.has_next
      })
    } catch (error) {
      console.error('Error loading more audiobooks:', error)
      toast.error('Failed to load more audiobooks')
    } finally {
      setLoadingMore(false)
    }
  }

  if (loading) {
    return (
      <div className="flex justify-center py-12">
        <Spinner size="large" />
      </div>
    )
  }

  if (!category) {
    return (
      <div className="text-center py-12">
        <h2 className="text-2xl font-semibold mb-2">Category not found</h2>
        <p className="text-gray-600">The category you're looking for doesn't exist.</p>
      </div>
    )
  }

  return (
    <div>
      <h1 className="text-3xl font-bold mb-8">{category.name}</h1>
      
      <AudiobookGrid audiobooks={audiobooks} />
      
      {pagination.hasNext && (
        <div 
          ref={loadMoreRef} 
          className="flex justify-center mt-8 py-4"
        >
          {loadingMore && <Spinner />}
        </div>
      )}
    </div>
  )
}

export default CategoryPage
