import React, { useState } from "react";
import axios from "axios";
import SearchBar from "./components/SearchBar";
import DrugInfoDisplay from "./components/DrugInfoDisplay";
import ErrorDisplay from "./components/ErrorDisplay";

const App = () => {
  const [drugInfo, setDrugInfo] = useState(null);
  const [error, setError] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

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

  return (
    <div className="min-h-screen bg-gray-100 py-8">
      <div className="max-w-4xl mx-auto px-4">
        <h1 className="text-4xl font-bold text-center text-blue-600 mb-8">
          Drug Information System
        </h1>
        <SearchBar onSearch={handleSearch} />
        {isLoading && (
          <div className="text-center mt-4">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          </div>
        )}
        <ErrorDisplay error={error} />
        <DrugInfoDisplay drugInfo={drugInfo} />
      </div>
    </div>
  );
};

export default App;