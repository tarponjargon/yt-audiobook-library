import AudiobookCard from './AudiobookCard'

function AudiobookGrid({ audiobooks, lastAudiobookRef }) {
  if (!audiobooks || audiobooks.length === 0) {
    return (
      <div className="text-center py-8 text-gray-500">
        No audiobooks found
      </div>
    )
  }

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
      {audiobooks.map((audiobook, index) => (
        <div 
          key={audiobook.id}
          ref={index === audiobooks.length - 1 ? lastAudiobookRef : null}
        >
          <AudiobookCard audiobook={audiobook} />
        </div>
      ))}
    </div>
  )
}

export default AudiobookGrid
