import { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import AudiobookGrid from '../components/AudiobookGrid';
import Spinner from '../components/Spinner';
import api from '../api';
import { toast } from 'react-hot-toast';

function FavoritesPage() {
  const [favorites, setFavorites] = useState([]);
  const [loading, setLoading] = useState(true);
  const { isAuthenticated } = useAuth();

  useEffect(() => {
    const fetchFavorites = async () => {
      if (!isAuthenticated) return;

      try {
        setLoading(true);
        const response = await api.get('/favorites/');
        console.log('Favorites API response:', response);
        // The response itself contains the data we need
        const favoritesData = response.audiobooks || [];
        console.log('Processed favorites data:', favoritesData);
        setFavorites(favoritesData);
      } catch (error) {
        console.error('Error fetching favorites:', error);
        toast.error('Failed to load favorites');
      } finally {
        setLoading(false);
      }
    };

    fetchFavorites();
  }, [isAuthenticated]);

  if (!isAuthenticated) {
    return (
      <div className="container mx-auto py-12 text-center">
        <h1 className="text-2xl font-bold mb-4">Please Login</h1>
        <p className="mb-4">You need to be logged in with your email to view your favorites.</p>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="flex justify-center items-center py-20">
        <Spinner size="large" />
      </div>
    );
  }

  return (
    <div className="container mx-auto py-8">
      <h1 className="text-3xl font-bold mb-8">My Favorites</h1>
      <AudiobookGrid audiobooks={favorites} />
    </div>
  );
}

export default FavoritesPage;
