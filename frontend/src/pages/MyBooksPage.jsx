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
  const { isAuthenticated } = useAuth()
  const navigate = useNavigate()

  useEffect(() => {
    if (!isAuthenticated) {
      navigate('/login')
      return
    }

    fetchMyBooks()
  }, [isAuthenticated, navigate])

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

  if (loading) {
    return (
      <div className="flex justify-center items-center min-h-screen">
        <Spinner />
      </div>
    )
  }

  return (
    <div className="max-w-6xl mx-auto">
      <h1 className="text-3xl font-bold mb-6">My Books</h1>

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
                    <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                      book.status === 'completed' ? 'bg-green-100 text-green-800' :
                      book.status === 'downloading' ? 'bg-yellow-100 text-yellow-800' :
                      book.status === 'failed' ? 'bg-red-100 text-red-800' :
                      'bg-gray-100 text-gray-800'
                    }`}>
                      {book.status}
                    </span>
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
