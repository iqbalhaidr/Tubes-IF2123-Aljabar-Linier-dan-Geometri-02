'use client'

import { useState, useRef } from 'react';
import Navbar from "@/app/_components/Navbar";
import Album from "@/app/_components/Album";
import Music from "@/app/_components/Music";
import ToggleComponents from "./_components/ToggleComponents";

export default function Home() {
  const [activeComponent, setActiveComponent] = useState<'Album' | 'Music'>('Album');
  const [isContentVisible, setIsContentVisible] = useState(false);
  const contentRef = useRef<HTMLDivElement>(null);

  const handleShowAlbum = () => {
    setActiveComponent('Album');
  };

  const handleShowMusic = () => {
    setActiveComponent('Music');
  };

  const handleFindYourSong = () => {
    setIsContentVisible(true);
    
    setTimeout(() => {
      contentRef.current?.scrollIntoView({ 
        behavior: 'smooth',
        block: 'start'
      });
    }, 100);
  };

  return (
    <div>
      <div className="relative h-screen overflow-hidden">
        <div className="absolute w-full h-screen bg-cover bg-center" style={{ backgroundImage: "url('/images/background.jpg')" }}>
          <Navbar />
          <div className="flex flex-col items-center justify-center h-full bg-transparent">
            <p className="w-1/3 text-6xl font-extrabold text-white font-montserrat text-center py-6">Find Your Music Match</p>
            <p className="w-1/2 text-l font-bold text-white font-sans text-center">Discover songs by humming or uploading artist images. Seamlessly search for album covers that match your audio dataset. Experience music like never before.</p>
            <button 
              onClick={handleFindYourSong}
              className="rounded-full font-extrabold text-l font-inter text-white px-4 py-1 transition-colors duration-300 bg-[#D16C34] hover:bg-white hover:text-black mt-4"
            >
              Find Your Song
            </button>
          </div>
        </div>
      </div>

      {/* Main content for Album and Music */}
      {isContentVisible && (
        <div 
          ref={contentRef} 
          className="w-full h-screen relative transition-all duration-500 ease-in-out"
        >
          {/* Toggle button always at the top */}
          <div className="absolute mt-14 right-1/4 transform -translate-x-1/2 z-50 bg-transparent p-4 rounded-lg">
            <ToggleComponents 
              activeComponent={activeComponent}
              onShowAlbum={handleShowAlbum}
              onShowMusic={handleShowMusic}
            />
          </div>

          {activeComponent === 'Album' && <Album />}
          {activeComponent === 'Music' && <Music />}
        </div>
      )}
    </div>
  );
}