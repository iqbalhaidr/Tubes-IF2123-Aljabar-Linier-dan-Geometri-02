import React, { useEffect, useState } from 'react';
import resultData from '../../../backend/result.json';
import mapperData from '../../../backend/mapper.json';
import Image from 'next/image';

// Define the types for resultData and mapperData
interface ResultItem {
  name: string;
  sim: number;
}

interface MapperItem {
  audio_file: string;
  pic_name: string;
}

interface CombinedItem {
  audio_file: string;
  pic_name: string;
  sim: number;
}

interface ExecutionItem {
  execution: number;
}

const ResultPagination: React.FC = () => {
  const [mapperItems, setMapperItems] = useState<CombinedItem[]>([]);
  const [currentPage, setCurrentPage] = useState(1);
  const [executionTime, setExecutionTime] = useState<number | null>(null);
  const itemsPerPage = 8;

  useEffect(() => {
    console.log('Raw resultData:', resultData); // Log the raw result.json
    console.log('Raw mapperData:', mapperData); // Log mapper.json
    // Combine data from result.json and mapper.json
    const combinedData: CombinedItem[] = [];
    for (let i = 0; i < resultData.length - 1; i++) {
      const resultItem = resultData[i] as ResultItem;
      const mapperItem = mapperData.find((item: MapperItem) => item.audio_file == resultItem.name);
      combinedData.push({
        audio_file: mapperItem ? mapperItem.audio_file : '',
        pic_name: mapperItem ? mapperItem.pic_name : '',
        sim: resultItem.sim,
      });
      console.log('Combined data:', combinedData); // Log the combined data
    }

    // Extract the last element as the execution time
    const executionTime = resultData[resultData.length - 1] as ExecutionItem;
    setExecutionTime(executionTime.execution);
    setMapperItems(combinedData);
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

  const renderPageNumbers = () => {
    const pageNumbers = [];
    for (let i = 1; i <= totalPages; i++) {
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

  return (
    <div className="mt-16">
      {/* Render current items in grid */}
      <div className="grid grid-cols-4">
        {currentItems.map((item, index) => (
          <div key={index} className="flex flex-col items-center p-4 rounded-md">
            <div className="w-44 h-[6.5rem] bg-gray-200 flex items-center justify-center overflow-hidden rounded-md">
              <Image
                src={`http://localhost:8000/datasetimage/${item.pic_name}`}
                alt={item.pic_name}
                width={256}
                height={256}
                className="object-contain"
              />
            </div>
            <p className="font-medium text-m mt-2">{item.audio_file}</p>
            <p className="text-white text-m">Similarity: {item.sim.toFixed(2)}</p>
          </div>
        ))}
      </div>

      {/* Render execution time */}
      {executionTime !== null && (
        <div className="mt-4 text-center text-white">
          <p>Execution time: {executionTime} ms</p>
        </div>
      )}

      {/* Render pagination controls */}
      <div className="flex justify-center items-center space-x-4">
        <button
          onClick={handlePrevPage}
          className={`p-2 rounded-md ${
            currentPage === 1
              ? 'text-gray-700 cursor-not-allowed'
              : 'text-gray-300 hover:text-gray-700 hover:bg-gray-100'
          }`}
          disabled={currentPage === 1}
        >
          <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="m15 18-6-6 6-6" />
          </svg>
        </button>

        <div className="text-white text-sm">
          Page {currentPage} of {totalPages}
        </div>

        <button
          onClick={handleNextPage}
          className={`p-2 rounded-md ${
            currentPage === totalPages
              ? 'text-gray-700 cursor-not-allowed'
              : 'text-gray-300 hover:text-gray-700 hover:bg-gray-100'
          }`}
          disabled={currentPage === totalPages}
        >
          <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="m9 18 6-6-6-6" />
          </svg>
        </button>
      </div>
    </div>
  );
};

export default ResultPagination;
