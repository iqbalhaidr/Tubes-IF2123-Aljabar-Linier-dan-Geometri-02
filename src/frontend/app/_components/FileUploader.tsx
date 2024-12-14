'use client'
import React, { useState } from 'react';

const FileUploader: React.FC = () => {
  const [audioFile, setAudioFile] = useState<File | null>(null);
  const [picturesFile, setPicturesFile] = useState<File | null>(null);
  const [mapperFile, setMapperFile] = useState<File | null>(null);

  const handleAudioFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.files) {
      setAudioFile(event.target.files[0]);
    }
  };

  const handlePicturesFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.files) {
      setPicturesFile(event.target.files[0]);
    }
  };

  const handleMapperFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.files) {
      setMapperFile(event.target.files[0]);
    }
  };

  return (
    <div className='flex flex-col items-center justify-center w-full max-w-md mx-auto'>
      <div className='py-4 w-full'>
        <label 
          htmlFor="audio-file" 
          className='block text-center text-black mb-2'
        >
          Audio File
        </label>
        <div className='flex items-center justify-center space-x-2'>
          <input
            type="file"
            id="audio-file"
            accept=".wav"
            onChange={handleAudioFileChange}
            className="w-full text-sm text-gray-500 
              file:mr-2 file:py-2 file:px-4 
              file:rounded-md file:border-0 
              file:text-sm file:font-semibold 
              file:bg-blue-50 file:text-blue-700 
              hover:file:bg-blue-100 
              focus:outline-none focus:ring-2 
              focus:ring-blue-500 focus:ring-offset-2 
              focus:ring-offset-gray-100" 
          />
          <button 
            className='px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600'
          >
            Upload
          </button>
        </div>
      </div>
      <div className='py-4 w-full'>
        <label 
          htmlFor="pictures-file" 
          className='block text-center text-black mb-2'
        >
          Pictures File
        </label>
        <div className='flex items-center justify-center space-x-2'>
          <input
            type="file"
            id="pictures-file"
            accept=".jpg, .png"
            onChange={handlePicturesFileChange}
            className="w-full text-sm text-gray-500 
              file:mr-2 file:py-2 file:px-4 
              file:rounded-md file:border-0 
              file:text-sm file:font-semibold 
              file:bg-blue-50 file:text-blue-700 
              hover:file:bg-blue-100 
              focus:outline-none focus:ring-2 
              focus:ring-blue-500 focus:ring-offset-2 
              focus:ring-offset-gray-100" 
          />
          <button 
            className='px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600'
          >
            Upload
          </button>
        </div>
      </div>
      <div className='py-4 w-full'>
        <label 
          htmlFor="mapper-file" 
          className='block text-center text-black mb-2'
        >
          Mapper File
        </label>
        <div className='flex items-center justify-center space-x-2'>
          <input
            type="file"
            id="mapper-file"
            accept=".json"
            onChange={handleMapperFileChange}
            className="w-full text-sm text-gray-500 
              file:mr-2 file:py-2 file:px-4 
              file:rounded-md file:border-0 
              file:text-sm file:font-semibold 
              file:bg-blue-50 file:text-blue-700 
              hover:file:bg-blue-100 
              focus:outline-none focus:ring-2 
              focus:ring-blue-500 focus:ring-offset-2 
              focus:ring-offset-gray-100" 
          />
          <button 
            className='px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600'
          >
            Upload
          </button>
        </div>
      </div>
    </div>
  );
};

export default FileUploader;