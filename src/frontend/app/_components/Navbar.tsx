import React from "react";

const Navbar = () => {
  return (
    <nav className="fixed top-0 w-full h-14 flex items-center justify-between px-8 z-10">
      <p className="text-white font-extrabold font-inter text-xl">Audio Searcher</p>
      <button className="rounded-full font-extrabold font-inter text-white px-4 py-1 text-l transition-colors duration-300 hover:bg-white hover:text-black">
        About Us
      </button>
    </nav>
  );
};

export default Navbar;
