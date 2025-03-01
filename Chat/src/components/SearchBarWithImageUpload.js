import React, { useState } from "react";

const SearchBarWithImageUpload = ({ onSearch, onImageUpload }) => {
  const [query, setQuery] = useState(""); // State for the search query
  const [image, setImage] = useState(null); // State for the uploaded image

  // Handle text input change
  const handleInputChange = (e) => {
    setQuery(e.target.value);
  };

  // Handle image upload
  const handleImageUpload = (e) => {
    const file = e.target.files[0];
    if (file) {
      setImage(file); // Set the uploaded image
      setQuery(""); // Clear the text input
    }
  };

  // Handle form submission
  const handleSubmit = (e) => {
    e.preventDefault();

    if (image) {
      // If an image is uploaded, process the image
      onImageUpload(image); // Call the onImageUpload function
    } else if (query.trim()) {
      // If a query is entered, process the text
      onSearch(query); // Call the onSearch function
    } else {
      // Show an error if neither is provided
      alert("Please enter a prompt or upload an image.");
    }

    // Reset the form
    setQuery("");
    setImage(null);
  };

  return (
    <form onSubmit={handleSubmit} className="flex items-center gap-4 w-full max-w-2xl mx-auto">
      {/* Image Upload Button */}
      <label className="flex items-center justify-center p-3 bg-purple-100 rounded-lg cursor-pointer hover:bg-purple-200">
        <input
          type="file"
          accept="image/*"
          onChange={handleImageUpload}
          className="hidden"
        />
        <svg
          xmlns="http://www.w3.org/2000/svg"
          className="h-6 w-6 text-purple-600"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"
          />
        </svg>
      </label>

      {/* Search Input */}
      <input
        type="text"
        value={query}
        onChange={handleInputChange}
        placeholder="Enter your prompt or upload an image..."
        className="flex-1 px-6 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
      />

      {/* Send Button */}
      <button
        type="submit"
        className="px-6 py-3 bg-purple-600 text-white font-semibold rounded-lg hover:bg-purple-700 focus:outline-none focus:ring-2 focus:ring-purple-500"
      >
        Search
      </button>
    </form>
  );
};

export default SearchBarWithImageUpload;