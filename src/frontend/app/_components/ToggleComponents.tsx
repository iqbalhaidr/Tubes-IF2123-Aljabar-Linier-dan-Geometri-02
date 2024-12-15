// _components/ToggleComponents.tsx
import React from 'react';

interface ToggleComponentsProps {
  activeComponent: 'Album' | 'Music'; // Terima activeComponent dan fungsi untuk mengganti
  onShowAlbum: () => void;
  onShowMusic: () => void;
}

const ToggleComponents: React.FC<ToggleComponentsProps> = ({ activeComponent, onShowAlbum, onShowMusic }) => {
  return (
    <div className="flex space-x-4">
      <button
        onClick={onShowAlbum}
        className={`px-5 py-1 rounded-md ${
          activeComponent === 'Album' ? 'bg-blue-500 text-white' : 'bg-gray-200 text-gray-700'
        }`}
      >
        Album
      </button>
      <button
        onClick={onShowMusic}
        className={`px-5 py-1 rounded-md ${
          activeComponent === 'Music' ? 'bg-blue-500 text-white' : 'bg-gray-200 text-gray-700'
        }`}
      >
        Music
      </button>
    </div>
  );
};

export default ToggleComponents;
