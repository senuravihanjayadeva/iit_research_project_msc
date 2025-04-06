import { useState } from "react";

const ImagePreview = ({ image }) => {
  const [scale, setScale] = useState(1);

  const handleZoomIn = () => {
    setScale((prev) => Math.min(prev + 0.2, 3));
  };

  const handleZoomOut = () => {
    setScale((prev) => Math.max(prev - 0.2, 1));
  };

  return (
    <div>
      {image && (
        <div className="mt-3 relative w-full max-w-3xl h-[500px] border rounded-md bg-gray-100">
          {/* Fixed Zoom Buttons (outside scrollable area) */}
          <div className="absolute top-4 right-4 z-20 flex gap-2">
            <button
              onClick={handleZoomIn}
              className="px-3 py-1 bg-white/80 hover:bg-white text-gray-800 font-bold rounded shadow"
              title="Zoom In"
            >
              +
            </button>
            <button
              onClick={handleZoomOut}
              className="px-3 py-1 bg-white/80 hover:bg-white text-gray-800 font-bold rounded shadow"
              title="Zoom Out"
            >
              –
            </button>
          </div>

          {/* Scrollable Zoomable Image */}
          <div className="w-full h-full overflow-auto p-2">
            <img
              src={image}
              alt="Uploaded"
              style={{ transform: `scale(${scale})`, transformOrigin: "top left" }}
              className="transition-transform duration-300"
            />
          </div>
        </div>
      )}
    </div>
  );
};

export default ImagePreview;
