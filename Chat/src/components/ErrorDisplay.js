import React from "react";

const ErrorDisplay = ({ error }) => {
  if (!error) return null;

  return (
    <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded-lg mt-8">
      {error}
    </div>
  );
};

export default ErrorDisplay;