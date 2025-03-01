import React, { useState } from "react";

const SearchBar = ({ onSearch }) => {
  const [drugName, setDrugName] = useState("");

  const handleSubmit = (e) => {
    e.preventDefault();
    onSearch(drugName);
  };

  return (
    <form onSubmit={handleSubmit} className="flex justify-center mb-8">
      <input
        type="text"
        placeholder="Enter drug name"
        value={drugName}
        onChange={(e) => setDrugName(e.target.value)}
        className="w-full max-w-md px-4 py-2 border border-gray-300 rounded-l-lg focus:outline-none focus:ring-2 focus:ring-blue-600"
      />
      <button
        type="submit"
        className="px-6 py-2 bg-blue-600 text-white rounded-r-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-600"
      >
        Search
      </button>
    </form>
  );
};

export default SearchBar;