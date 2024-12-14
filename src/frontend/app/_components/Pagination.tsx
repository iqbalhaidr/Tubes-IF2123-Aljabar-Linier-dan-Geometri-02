'use client';
import React, { useState, useEffect } from 'react';
import mapperData from '@/app/_components/mapper.json';
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

  const indexOfLastItem = currentPage * itemsPerPage;
  const indexOfFirstItem = indexOfLastItem - itemsPerPage;
  const currentItems = mapperItems.slice(indexOfFirstItem, indexOfLastItem);

  const handlePageChange = (pageNumber: number) => {
    setCurrentPage(pageNumber);
  };

  const renderPageNumbers = () => {
    const pageNumbers = [];
    for (let i = 1; i <= Math.ceil(mapperItems.length / itemsPerPage); i++) {
      pageNumbers.push(
        <button
          key={i}
          onClick={() => handlePageChange(i)}
          className={`px-3 py-1 rounded-md ${
            currentPage === i ? 'bg-blue-500 text-white' : 'bg-gray-200 text-gray-700'
          }`}
        >
          {i}
        </button>
      );
    }
    return pageNumbers;
  };

  const handlePrevPage = () => {
    if (currentPage > 1) {
      setCurrentPage(currentPage - 1);
    }
  };

  const handleNextPage = () => {
    if (currentPage < Math.ceil(mapperItems.length / itemsPerPage)) {
      setCurrentPage(currentPage + 1);
    }
  };

  return (
    <div>
      <div className="grid grid-cols-3 gap-4">
        {currentItems.map((item, index) => (
          <div key={index} className="flex flex-col items-center mb-4">
            <div className="w-44 h-24 bg-gray-200 flex items-center justify-center overflow-hidden">
              <Image
                src={`/images/${item.pic_name}`} // Fixed the syntax
                alt={item.pic_name}
                width={256}
                height={256}
                className="object-contain"
              />
            </div>
            <p className="mt-2 font-medium">{item.audio_file}</p>
          </div>
        ))}
      </div>
      <div className="flex justify-center mt-4">
        <button
          onClick={handlePrevPage}
          className={`px-3 py-1 rounded-md ${
            currentPage === 1 ? 'bg-gray-200 text-gray-700 cursor-not-allowed' : 'bg-blue-500 text-white'
          }`}
          disabled={currentPage === 1}
        >
          Prev
        </button>
        {renderPageNumbers()}
        <button
          onClick={handleNextPage}
          className={`px-3 py-1 rounded-md ${
            currentPage === Math.ceil(mapperItems.length / itemsPerPage)
              ? 'bg-gray-200 text-gray-700 cursor-not-allowed'
              : 'bg-blue-500 text-white'
          }`}
          disabled={currentPage === Math.ceil(mapperItems.length / itemsPerPage)}
        >
          Next
        </button>
      </div>
    </div>
  );
};

export default Pagination;
