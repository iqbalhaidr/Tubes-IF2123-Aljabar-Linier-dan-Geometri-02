import React from "react";

const Navbar = () => {
  return (
    <div className="relative w-full h-12 flex items-center justify-between px-6">
      <p className="text-white font-bold">Audio Search</p>
      <button className="rounded-full text-white px-4 py-1 transition-colors duration-300 hover:bg-white hover:text-stone-900">
        About Us
      </button>
    </div>
  );
};

export default Navbar;
