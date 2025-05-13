import axios from 'axios'

const API_BASE_URL = '/api'

// Create axios instance with default config
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

export default api;

// Add response interceptor to handle errors globally
api.interceptors.response.use(
  response => response.data,
  error => {
    // Handle error or pass it to the caller
    return Promise.reject(error)
  }
)

// API functions
export const fetchCategories = async () => {
  return api.get('/categories')
}

export const fetchCategoryAudiobooks = async (categoryId, page = 1, perPage = 12) => {
  return api.get(`/categories/${categoryId}`, {
    params: { page, per_page: perPage }
  })
}

export const searchAudiobooks = async (query, page = 1, perPage = 12) => {
  return api.get('/audiobooks/search', {
    params: { q: query, page, per_page: perPage }
  })
}

export const fetchAudiobookDetail = async (audiobookId) => {
  return api.get(`/audiobooks/${audiobookId}`)
}

export const fetchRandomAudiobooks = async (number = 5) => {
  return api.get('/audiobooks/random', {
    params: { number }
  })
}

export const fetchAllAudiobooks = async (page = 1, perPage = 12) => {
  return api.get('/audiobooks', {
    params: { page, per_page: perPage }
  })
}

export const fetchAudiobookCount = async () => {
  try {
    return api.get('/audiobooks/count')
  } catch (error) {
    console.error('Error fetching audiobook count:', error)
    return { count: 0 } // Return a default value if the API call fails
  }
}
