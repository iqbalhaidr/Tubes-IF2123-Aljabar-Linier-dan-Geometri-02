'use client'
import Image from "next/image";
import Navbar from "@/app/_components/Navbar";
import Pagination from '@/app/_components/Pagination'; 
import { useState, useRef } from 'react'; 
import FileUploader from "@/app/_components/FileUploader";
import ToggleComponents from "@/app/_components/ToggleComponents";

const Album: React.FC = () => {
  const [currentPage, setCurrentPage] = useState(1);
  const totalPages = 3; // Jumlah total halaman
  const [picturesFile, setPicturesFile] = useState<File | null>(null);
  
  interface PaginationProps {
    currentPage: number;
    totalPages: number;
    onPageChange: (page: number) => void;
  }

  const secondPageRef = useRef<HTMLDivElement | null>(null);

  const handlePageChange = (page: number): void => {
    setCurrentPage(page);
  };

  const scrollToSection = () => { 
    if (secondPageRef.current) { 
      secondPageRef.current.scrollIntoView({ behavior: 'smooth' }); 
    } 
  };

  const handlePicturesFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
      if (event.target.files) {
        setPicturesFile(event.target.files[0]);
      }
    };

    const handleSearchImage = async () => {
      try {
        const response = await fetch('http://127.0.0.1:8000/search_image/', {
          method: 'POST',
        });
    
      } catch (error) {
        console.error('Search error:', error);
        alert('An error occurred while searching');
      }
    };

    const handleUploadImage = async (file: File | null) => {
      if (!file) return alert('No file selected');

    
      const formData = new FormData();
      formData.append('file', file);
    
      try {
        const response = await fetch('http://127.0.0.1:8000/upload_image/', {
          method: 'POST',
          body: formData,
        });
    
        const data = await response.json();
        if (response.ok) {
          alert(data.message || 'Upload successful!');
        } else {
          throw new Error(data.error || 'Upload failed.');
        }
      } catch (error) {
        console.error('Upload error:', error);
        alert('An error occurred while uploading');
      }
    };

    return (
        <div className="relative h-screen" ref={secondPageRef}>
            <div className="flex space-y-14 bg-black h-full">
                <div className="flex flex-col bg-blue-950 w-1/5 mt-14 h-auto shadow-lg ">
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
                                accept=".jpg, .png"
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
                                className='px-4 py-1 bg-blue-500 text-white rounded-md hover:bg-blue-600 mt-2 text-sm'
                                onClick={() => handleUploadImage(picturesFile)}>
                                Upload
                            </button>
                        </div>
                    </div>
                    <FileUploader />
                    <div className='py-4 w-full'>
                      <div className='flex flex-col items-center justify-center space-x-2'> 
                        <button
                          onClick={handleSearchImage} 
                          className='px-4 py-1 bg-green-500 text-white rounded-md hover:bg-blue-600 mt-2 text-sm'
                        >
                          Search
                        </button>
                      </div>
                    </div>
                </div>
                <div className="ml-2 justify-center w-full bg-blue-950">
                    <Pagination />
                </div>
                
            </div>
        </div>
    );
}
export default Album;