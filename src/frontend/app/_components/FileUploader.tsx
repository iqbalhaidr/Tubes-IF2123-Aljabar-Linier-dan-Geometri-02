'use client'
import React, { useState } from 'react';

const FileUploader: React.FC = () => {
  const [audioFile, setAudioFile] = useState<File | null>(null);
  const [picturesFile, setPicturesFile] = useState<File | null>(null);
  const [mapperFile, setMapperFile] = useState<File | null>(null);

  const handleUpload = async (file: File | null, type: string) => {
    if (!file) return alert('No file selected');

    const formData = new FormData();
    formData.append('file', file);
    formData.append('file_type', type);

    try {
      const response = await fetch('http://127.0.0.1:8000/upload/', {
        method: 'POST',
        body: formData,
      });

      const data = await response.json();
      alert(data.message || data.error || 'Upload successful!');
    } catch (error) {
      console.error('Upload error:', error);
      alert('An error occurred while uploading');
    }
  };


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
      <div className='w-full'>
        <label 
          htmlFor="audio-file" 
          className='block text-center text-white mb-1'
        >
          Audio File
        </label>
        <div className='flex flex-col items-center justify-center space-x-2'>
          <input
            type="file"
            id="audio-file"
            accept=".zip"
            onChange={handleAudioFileChange}
            className="w-full text-sm text-gray-500 
              file:mr-2 file:py-1 file:px-4 
              file:rounded-md file:border-0 
              file:text-sm file:font-semibold 
              file:bg-blue-50 file:text-blue-700 
              hover:file:bg-blue-100 
              focus:outline-none focus:ring-2 
              focus:ring-blue-500 focus:ring-offset-2 
              focus:ring-offset-gray-100" 
          />
          <button
            onClick={() => handleUpload(audioFile, 'audio')}
            className='px-4 py-1 bg-blue-500 text-white rounded-md hover:bg-blue-600 mt-2 text-sm'
          >
            Upload
          </button>
        </div>
      </div>
      <div className='py-4 w-full'>
        <label 
          htmlFor="pictures-file" 
          className='block text-center text-white mb-1'
        >
          Pictures File
        </label>
        <div className='flex flex-col items-center justify-center space-x-2'>
          <input
            type="file"
            id="pictures-file"
            accept=".zip"
            onChange={handlePicturesFileChange}
            className="w-full text-sm text-gray-500 
              file:mr-2 file:py-1 file:px-4 
              file:rounded-md file:border-0 
              file:text-sm file:font-semibold 
              file:bg-blue-50 file:text-blue-700 
              hover:file:bg-blue-100 
              focus:outline-none focus:ring-2 
              focus:ring-blue-500 focus:ring-offset-2 
              focus:ring-offset-gray-100" 
          />
          <button 
            onClick={() => handleUpload(picturesFile, 'pictures')}
            className='px-4 py-1 bg-blue-500 text-white rounded-md hover:bg-blue-600 mt-2 text-sm'
          >
            Upload
          </button>
        </div>
      </div>
      <div className='w-full'> 
        <label 
          htmlFor="mapper-file" 
          className='block text-center text-white mb-1'
        >
          Mapper File
        </label>
        <div className='flex flex-col items-center justify-center space-x-2'>
          <input
            type="file"
            id="mapper-file"
            accept=".json"
            onChange={handleMapperFileChange}
            className="w-full text-sm text-gray-500 
              file:mr-2 file:py-1 file:px-4 
              file:rounded-md file:border-0 
              file:text-sm file:font-semibold 
              file:bg-blue-50 file:text-blue-700 
              hover:file:bg-blue-100 
              focus:outline-none focus:ring-2 
              focus:ring-blue-500 focus:ring-offset-2 
              focus:ring-offset-gray-100" 
          />
          <button
            onClick={() => handleUpload(mapperFile, 'mapper')}
            className='px-4 py-1 bg-blue-500 text-white rounded-md hover:bg-blue-600 mt-2 text-sm'
          >
            Upload
          </button>
        </div>
      </div>
    </div>
  );
};

export default FileUploader;