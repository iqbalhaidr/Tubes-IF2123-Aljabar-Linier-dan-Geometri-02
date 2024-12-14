'use client'
import Image from "next/image";
import Navbar from "@/app/_components/Navbar";
import Pagination from '@/app/_components/Pagination'; 
import { useState, useRef } from 'react';
import FileUploader from "@/app/_components/FileUploader";

const Music: React.FC = () => {
  const [currentPage, setCurrentPage] = useState(1);
  const totalPages = 3; // Jumlah total halaman
  const [imageUrl, setImageUrl] = useState<string | null>(null); // State untuk menyimpan URL gambar yang diunggah
  const [fileName, setFileName] = useState<string | null>(null); // State untuk menyimpan nama file yang diunggah
  const [audioFile, setAudioFile] = useState<File | null>(null);
  
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

  const handleImageUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      const url = URL.createObjectURL(file);
      setImageUrl(url);
      setFileName(file.name); // Atur nama file
    }
  };

  const handleAudioFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
      if (event.target.files) {
        setAudioFile(event.target.files[0]);
      }
    };

    return (
        <div className="relative h-screen" ref={secondPageRef}>
            <div className="flex space-y-9 bg-blue-950 h-full">
                <div className="flex flex-col bg-white w-1/5 my-20 h-auto rounded-lg shadow-lg ">
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
                                id="pictures-file"
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
                                className='px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600'>
                                Upload
                            </button>
                        </div>
                    </div>
                    <FileUploader />
                </div>
                <div className="mx-auto py-10">
                    <Pagination />
                </div>
            </div>
        </div>
    );
}
export default Music;