import React from "react";

const ErrorDisplay = ({ error }) => {
  if (!error) return null;

  return (
    <div className="mt-6 p-4 bg-red-50 border border-red-200 rounded-lg text-red-600">
      <p className="font-semibold">Error:</p>
      <p>{error}</p>
    </div>
  );
};

export default ErrorDisplay;