'use client'
import Image from "next/image";
import Navbar from "@/app/_components/Navbar";
import Pagination from '@/app/_components/Pagination'; 
import { useState, useRef } from 'react';
import FileUploader from "./_components/FileUploader";
import Album from "./_components/Album";

export default function Home() {
  const [currentPage, setCurrentPage] = useState(1);
  const totalPages = 3; // Jumlah total halaman
  const [imageUrl, setImageUrl] = useState<string | null>(null); // State untuk menyimpan URL gambar yang diunggah
  const [fileName, setFileName] = useState<string | null>(null); // State untuk menyimpan nama file yang diunggah
  
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

  return (
    <div>
      <div className="relative h-screen overflow-hidden">
        <div className="absolute w-full h-screen bg-cover bg-center" style={{ backgroundImage: "url('/images/background.jpg')" }}>
          <Navbar />
          <div className="flex flex-col items-center justify-center h-full bg-transparent">
            <p className="w-1/3 text-6xl font-extrabold text-white font-montserrat text-center py-6">Find Your Music Match</p>
            <p className="w-1/2 text-l font-bold text-white font-sans text-center">Discover songs by humming or uploading artist images. Seamlessly search for album covers that match your audio dataset. Experience music like never before.</p>
            <button className="rounded-full font-extrabold text-l font-inter text-white px-4 py-1 transition-colors duration-300 bg-[#D16C34] hover:bg-white hover:text-black mt-4" onClick={scrollToSection }>Find Your Song</button>
          </div>
        </div>
      </div>
      <Album />
    </div>
  );
}

