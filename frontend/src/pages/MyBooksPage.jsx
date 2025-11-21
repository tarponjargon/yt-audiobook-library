import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import api from '../api'
import { toast } from 'react-hot-toast'
import Spinner from '../components/Spinner'

function MyBooksPage() {
  const [books, setBooks] = useState([])
  const [loading, setLoading] = useState(true)
  const [deleteConfirm, setDeleteConfirm] = useState(null)
  const [rssUrl, setRssUrl] = useState('')
  const { isAuthenticated, loading: authLoading } = useAuth()
  const navigate = useNavigate()

  useEffect(() => {
    if (authLoading) return

    if (!isAuthenticated) {
      navigate('/login')
      return
    }

    fetchMyBooks()
    fetchRssUrl()
  }, [isAuthenticated, authLoading, navigate])

  // Separate effect for auto-refresh polling
  useEffect(() => {
    const hasDownloading = books.some(book => book.status === 'downloading' || book.status === 'pending')

    if (!hasDownloading) {
      return
    }

    const interval = setInterval(() => {
      fetchMyBooks()
    }, 5000) // Refresh every 5 seconds if there are downloading books

    return () => clearInterval(interval)
  }, [books])

  const fetchMyBooks = async () => {
    try {
      setLoading(true)
      const response = await api.get('/user-books')
      setBooks(response.books)
    } catch (error) {
      console.error('Error fetching My Books:', error)
      toast.error('Failed to load your books')
    } finally {
      setLoading(false)
    }
  }

  const fetchRssUrl = async () => {
    try {
      const data = await api.get('/user-books/rss-url')
      setRssUrl(`http://ytbooks.com/rss-feed/${data.token}`)
    } catch (error) {
      console.error('Error fetching RSS URL:', error)
    }
  }

  const copyRssUrl = (e) => {
    if (e) {
      e.preventDefault()
      e.stopPropagation()
    }

    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(rssUrl)
        .then(() => toast.success('RSS feed URL copied to clipboard'))
        .catch(() => {
          // Fallback if clipboard fails
          fallbackCopy()
        })
    } else {
      fallbackCopy()
    }
  }

  const fallbackCopy = () => {
    try {
      const textArea = document.createElement('textarea')
      textArea.value = rssUrl
      textArea.style.position = 'fixed'
      textArea.style.left = '-999999px'
      textArea.style.top = '0'
      document.body.appendChild(textArea)
      textArea.focus()
      textArea.select()

      const successful = document.execCommand('copy')
      document.body.removeChild(textArea)

      if (successful) {
        toast.success('RSS feed URL copied to clipboard')
      } else {
        toast.error('Failed to copy URL. Please copy manually.')
      }
    } catch (err) {
      toast.error('Failed to copy URL. Please copy manually.')
    }
  }

  const handleDelete = async (bookId) => {
    try {
      await api.delete(`/user-books/${bookId}`)
      setBooks(books.filter(book => book.id !== bookId))
      setDeleteConfirm(null)
      toast.success('Book removed from your library')
    } catch (error) {
      console.error('Error deleting book:', error)
      toast.error('Failed to remove book')
    }
  }

  const confirmDelete = (bookId) => {
    setDeleteConfirm(bookId)
  }

  const cancelDelete = () => {
    setDeleteConfirm(null)
  }

  const formatDate = (dateString) => {
    const date = new Date(dateString)
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    })
  }

  if (authLoading || loading) {
    return (
      <div className="flex justify-center items-center min-h-screen">
        <Spinner />
      </div>
    )
  }

  return (
    <div className="max-w-6xl mx-auto">
      <h1 className="text-3xl font-bold mb-6">My Books</h1>

      {rssUrl && (
        <div className="mb-6 bg-blue-50 border border-blue-200 rounded-lg p-4">
          <h2 className="text-lg font-semibold mb-2 text-blue-900">Podcast Feed</h2>
          <p className="text-sm text-blue-700 mb-3">
            Add this URL to your podcast app to listen to your books:
          </p>
          <div className="flex items-center gap-2">
            <input
              type="text"
              readOnly
              value={rssUrl}
              className="flex-1 px-3 py-2 bg-white border border-blue-300 rounded text-sm font-mono"
            />
            <button
              onClick={copyRssUrl}
              className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 whitespace-nowrap"
            >
              Copy URL
            </button>
          </div>
        </div>
      )}

      {books.length === 0 ? (
        <div className="text-center py-12">
          <p className="text-gray-500 text-lg">You haven't added any books yet.</p>
          <button
            onClick={() => navigate('/')}
            className="mt-4 px-6 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
          >
            Browse Audiobooks
          </button>
        </div>
      ) : (
        <div className="bg-white shadow-md rounded-lg overflow-hidden">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Title
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Author
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Date Added
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {books.map((book) => (
                <tr key={book.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm font-medium text-gray-900">
                      {book.audiobook?.title || 'Unknown Title'}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm text-gray-500">
                      {book.audiobook?.author || 'Unknown Author'}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm text-gray-500">
                      {formatDate(book.created_at)}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center space-x-2">
                      <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                        book.status === 'completed' ? 'bg-green-100 text-green-800' :
                        book.status === 'downloading' ? 'bg-yellow-100 text-yellow-800' :
                        book.status === 'failed' ? 'bg-red-100 text-red-800' :
                        'bg-gray-100 text-gray-800'
                      }`}>
                        {book.status}
                      </span>
                      {(book.status === 'downloading' || book.status === 'pending') && (
                        <div className="flex space-x-1">
                          <div className="w-2 h-2 bg-yellow-500 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                          <div className="w-2 h-2 bg-yellow-500 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                          <div className="w-2 h-2 bg-yellow-500 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
                        </div>
                      )}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                    {deleteConfirm === book.id ? (
                      <div className="flex space-x-2">
                        <button
                          onClick={() => handleDelete(book.id)}
                          className="text-red-600 hover:text-red-900"
                        >
                          Confirm
                        </button>
                        <button
                          onClick={cancelDelete}
                          className="text-gray-600 hover:text-gray-900"
                        >
                          Cancel
                        </button>
                      </div>
                    ) : (
                      <button
                        onClick={() => confirmDelete(book.id)}
                        className="text-red-600 hover:text-red-900"
                      >
                        Delete
                      </button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}

export default MyBooksPage
