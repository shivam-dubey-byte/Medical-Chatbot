import React from "react";

const DrugInfoDisplay = ({ drugInfo }) => {
  if (!drugInfo) return null;

  // Function to parse and highlight text between **
  const parseText = (text) => {
    return text.split("**").map((part, index) => {
      // Highlight text between ** (odd indices)
      if (index % 2 === 1) {
        return (
          <span key={index} className="font-bold text-blue-600">
            {part}
          </span>
        );
      }
      // Return normal text (even indices)
      return part;
    });
  };

  // Function to split side effects into smaller chunks
  const splitSideEffects = (sideEffects) => {
    const effectsList = sideEffects.split(", ");
    const chunkSize = 10; // Number of side effects per chunk
    const chunks = [];

    for (let i = 0; i < effectsList.length; i += chunkSize) {
      chunks.push(effectsList.slice(i, i + chunkSize).join(", "));
    }

    return chunks;
  };

  return (
    <div className="bg-white p-6 rounded-lg shadow-lg mt-8">
      {/* Drug Name */}
      <h2 className="text-2xl font-bold text-blue-600 mb-4">
        Drug Information: {drugInfo.drug_name}
      </h2>

      {/* Split Response into Sections */}
      <div className="space-y-4">
        {drugInfo.response.split("\n").map((line, index) => {
          // Check if the line contains a heading (e.g., "Side Effects:")
          if (line.endsWith(":")) {
            return (
              <h3 key={index} className="text-xl font-semibold text-gray-800 mt-4 mb-2">
                {line}
              </h3>
            );
          }

          // Handle Side Effects Section
          if (line.startsWith("Common side effects include")) {
            const sideEffects = line.replace("Common side effects include **", "").replace("**.", "");
            const sideEffectChunks = splitSideEffects(sideEffects);

            return (
              <div key={index} className="space-y-2">
                <p className="text-gray-700">
                  <strong>Common side effects</strong> include:
                </p>
                <div className="max-h-48 overflow-y-auto border border-gray-200 rounded-lg p-3">
                  {sideEffectChunks.map((chunk, i) => (
                    <p key={i} className="text-gray-700">
                      {chunk}
                    </p>
                  ))}
                </div>
              </div>
            );
          }

          // Default paragraph
          return (
            <p key={index} className="text-gray-700">
              {parseText(line)}
            </p>
          );
        })}
      </div>
    </div>
  );
};

export default DrugInfoDisplay;