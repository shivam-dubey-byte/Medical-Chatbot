import React, { useState } from "react";
import axios from "axios";
import SearchBarWithImageUpload from "./components/SearchBarWithImageUpload"; // Updated component
import DrugInfoDisplay from "./components/DrugInfoDisplay";
import ErrorDisplay from "./components/ErrorDisplay";
import "./App.css";

const App = () => {
  const [drugInfo, setDrugInfo] = useState(null);
  const [error, setError] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  // Function to handle text search
  const handleSearch = async (drugName) => {
    setIsLoading(true);
    setError(null);
    setDrugInfo(null);

    try {
      const response = await axios.post("http://127.0.0.1:5000/drug-info", {
        drug_name: drugName,
      });
      setDrugInfo(response.data);
    } catch (err) {
      setError(err.response?.data?.error || "An error occurred.");
    } finally {
      setIsLoading(false);
    }
  };

  // Function to handle image upload
  const handleImageUpload = async (file) => {
    setIsLoading(true);
    setError(null);
    setDrugInfo(null);

    try {
      const formData = new FormData();
      formData.append("file", file);

      // Send the image to the backend
      const response = await axios.post("http://127.0.0.1:5000/medicine-info", formData, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      });
      setDrugInfo(response.data);
    } catch (err) {
      setError(err.response?.data?.error || "An error occurred.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-purple-50 py-12">
      <div className="max-w-4xl mx-auto px-6">
        {/* Header */}
        <h1 className="text-5xl font-bold text-center text-blue-800 mb-10">
          Drug Information System
        </h1>

        {/* Search Bar with Image Upload */}
        <SearchBarWithImageUpload
          onSearch={handleSearch} // Pass the handleSearch function
          onImageUpload={handleImageUpload} // Pass the handleImageUpload function
        />

        {/* Loading Spinner */}
        {isLoading && (
          <div className="text-center mt-8">
            <div className="animate-spin rounded-full h-14 w-14 border-b-2 border-blue-600 mx-auto"></div>
          </div>
        )}

        {/* Error Display */}
        <ErrorDisplay error={error} />

        {/* Drug Info Display */}
        <DrugInfoDisplay drugInfo={drugInfo} />
      </div>
    </div>
  );
};

export default App;