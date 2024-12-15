'use client';
import React, { useState, useEffect } from 'react';
import mapperData from '../../../backend/mapper.json';
import Image from 'next/image';

interface MapperItem {
  audio_file: string;
  pic_name: string;
}

const Pagination: React.FC = () => {
  const [mapperItems, setMapperItems] = useState<MapperItem[]>([]);
  const [currentPage, setCurrentPage] = useState(1);
  const itemsPerPage = 12;

  useEffect(() => {
    setMapperItems(mapperData);
  }, []);

  const totalPages = Math.ceil(mapperItems.length / itemsPerPage);
  const indexOfLastItem = currentPage * itemsPerPage;
  const indexOfFirstItem = indexOfLastItem - itemsPerPage;
  const currentItems = mapperItems.slice(indexOfFirstItem, indexOfLastItem);

  const handlePageChange = (pageNumber: number) => {
    setCurrentPage(pageNumber);
  };

  const handlePrevPage = () => {
    if (currentPage > 1) {
      setCurrentPage(currentPage - 1);
    }
  };

  const handleNextPage = () => {
    if (currentPage < totalPages) {
      setCurrentPage(currentPage + 1);
    }
  };

  return (
    <div className='mt-16'>
      <div className="grid grid-cols-4 gap-x-8 gap-y-4">
        {currentItems.map((item, index) => (
          <div key={index} className="flex flex-col items-center">
            <div className="w-44 h-[6.5rem] bg-gray-200 flex items-center justify-center overflow-hidden rounded-md">
              <Image
                src={`http://localhost:8000/datasetimage/${item.pic_name}`}
                alt={item.pic_name}
                width={256}
                height={256}
                className="object-contain"
              />
            </div>
            <p className="font-medium">{item.audio_file}</p>
          </div>
        ))}
      </div>
      <div className="flex justify-center items-center  space-x-4">
        <button
          onClick={handlePrevPage}
          className={`p-2 rounded-md ${
            currentPage === 1 ? 'text-gray-700 cursor-not-allowed' : 'text-gray-300 hover:text-gray-700 hover:bg-gray-100'
          }`}
          disabled={currentPage === 1}
        >
          <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="m15 18-6-6 6-6"/>
          </svg>
        </button>
        
        <div className="text-white text-sm">
          Page {currentPage} of {totalPages}
        </div>
        
        <button
          onClick={handleNextPage}
          className={`p-2 rounded-md ${
            currentPage === totalPages ? 'text-gray-700 cursor-not-allowed' : 'text-gray-300 hover:text-gray-700 hover:bg-gray-100'
          }`}
          disabled={currentPage === totalPages}
        >
          <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="m9 18 6-6-6-6"/>
          </svg>
        </button>
      </div>
    </div>
  );
};

export default Pagination;