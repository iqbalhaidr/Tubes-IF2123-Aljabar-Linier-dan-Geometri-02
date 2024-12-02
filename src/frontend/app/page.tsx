'use client'
import Image from "next/image";
import Navbar from "@/app/_components/Navbar";

export default function Home() {
  return (
    <div className="relative h-screen overflow-hidden">
      <div className="absolute w-full h-screen bg-cover bg-center" style={{ backgroundImage: "url('/images/background.jpg')" }}>
        <Navbar />
        <div className="flex flex-col items-center justify-center h-3/4 bg-transparent">
          <p className="w-1/3 text-6xl font-extrabold text-white font-montserrat text-center py-6">Find Your Music Match</p>
          <p className="w-1/2 text-l font-bold text-white font-sans text-center">Discover songs by humming or uploading artist images. Seamlessly search for album covers that match your audio dataset. Experience music like never before.</p>
          <button className="rounded-full font-extrabold text-l font-inter text-white px-4 py-1 transition-colors duration-300 bg-[#D16C34] hover:bg-white hover:text-black mt-4">Find Your Song</button>
        </div>
      </div>
    </div>
  );
}

