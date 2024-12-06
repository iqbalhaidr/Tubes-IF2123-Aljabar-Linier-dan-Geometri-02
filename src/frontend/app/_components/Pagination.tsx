import React from 'react';

interface PaginationProps {
  currentPage: number;
  totalPages: number;
  onPageChange: (page: number) => void;
}

const Pagination: React.FC<PaginationProps> = ({ currentPage, totalPages, onPageChange }) => {
  const pages = [];
  for (let i = 1; i <= totalPages; i++) {
    pages.push(i);
  }

  return (
    <div className="flex justify-center items-center space-x-2 mt-4">
      <button
        onClick={() => onPageChange(currentPage - 1)}
        disabled={currentPage === 1}
        className="px-3 py-1 bg-black text-white rounded disabled:opacity-50 disabled:cursor-not-allowed transition-colors duration-300 hover:bg-[#1C1C1C]"
      >
        Previous
      </button>
      {pages.map((page) => (
        <button
          key={page}
          onClick={() => onPageChange(page)}
          className={`px-3 py-1 rounded ${page === currentPage ? 'border-2 border-white bg-black text-white' : 'bg-black text-white'}`}
        >
          {page}
        </button>
      ))}
      <span className="px-3 py-1">...</span>
      <button
        onClick={() => onPageChange(currentPage + 1)}
        disabled={currentPage === totalPages}
        className="px-3 py-1 bg-black text-white rounded disabled:opacity-50 disabled:cursor-not-allowed transition-colors duration-300 hover:bg-[#1C1C1C]"
      >
        Next
      </button>
    </div>
  );
};

export default Pagination;

