import React, { useState } from 'react';
import Album from '@/app/_components/Album'; // Mengimpor komponen Album
import Music from '@/app/_components/Music'; // Mengimpor komponen Music

const ToggleComponents: React.FC = () => {
  const [activeComponent, setActiveComponent] = useState<'Album' | 'Music'>('Album');

  const handleShowAlbum = () => setActiveComponent('Album');
  const handleShowMusic = () => setActiveComponent('Music');

  return (
    <div className="flex flex-col items-center">
      <div className="space-x-4 mb-4">
        <button
          onClick={handleShowAlbum}
          className={`px-4 py-2 rounded-md ${
            activeComponent === 'Album' ? 'bg-blue-500 text-white' : 'bg-gray-200 text-gray-700'
          }`}
        >
          Album
        </button>
        <button
          onClick={handleShowMusic}
          className={`px-4 py-2 rounded-md ${
            activeComponent === 'Music' ? 'bg-green-500 text-white' : 'bg-gray-200 text-gray-700'
          }`}
        >
          Music
        </button>
      </div>
      <div className="w-full">
        {activeComponent === 'Album' && <Album />}
        {activeComponent === 'Music' && <Music />}
      </div>
    </div>
  );
};

export default ToggleComponents;
