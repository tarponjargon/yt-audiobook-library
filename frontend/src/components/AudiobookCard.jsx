import { Link } from 'react-router-dom'

function AudiobookCard({ audiobook }) {
  return (
    <Link to={`/audiobook/${audiobook.id}`} className="block" rel="noopener noreferrer">
      <div className="card h-full flex flex-col">
        <div className="relative pb-[56.25%]">
          <img
            src={audiobook.thumbnail || '/placeholder-book.jpg'}
            alt={audiobook.title}
            className="absolute inset-0 w-full h-full object-cover"
          />
        </div>
        <div className="p-4 flex-grow flex flex-col">
          <h3 className="font-semibold text-lg line-clamp-2 mb-1">{audiobook.title}</h3>
          {audiobook.author && (
            <p className="text-gray-600 text-sm mt-auto">
              By {audiobook.author}
            </p>
          )}
        </div>
      </div>
    </Link>
  )
}

export default AudiobookCard
