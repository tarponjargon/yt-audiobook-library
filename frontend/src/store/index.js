import { create } from 'zustand'
import { fetchCategories as apiFetchCategories } from '../api'

export const useStore = create((set, get) => ({
  // Categories state
  categories: [],
  loading: false,
  error: null,
  
  // Fetch categories
  fetchCategories: async () => {
    // Don't fetch if we already have categories
    if (get().categories.length > 0) return
    
    try {
      set({ loading: true, error: null })
      const data = await apiFetchCategories()
      set({ categories: data.categories, loading: false })
    } catch (error) {
      set({ 
        error: error.message || 'Failed to fetch categories', 
        loading: false 
      })
      throw error
    }
  },
  
  // Clear categories (useful for testing or forced refresh)
  clearCategories: () => set({ categories: [] }),
}))
