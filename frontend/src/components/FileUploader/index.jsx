import { useRef } from "react";

const FileUploader = ({onFileSelected}) => {
  const fileInputRef = useRef();

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file) onFileSelected(file);
  };
  
  return (
    <div
      onClick={() => fileInputRef.current.click()}
      className="cursor-pointer w-full max-w-md border-2 border-dashed border-blue-500 p-8 py-30 rounded-xl text-center text-white bg-gray-800 hover:bg-gray-700 transition"
    >
      <p className="text-xl mb-2">📤 Upload Dental Image</p>
      <p className="text-sm text-gray-400">Drag & Drop or Click to Upload</p>
      <input
        type="file"
        accept="image/*"
        ref={fileInputRef}
        onChange={handleFileChange}
        className="hidden"
      />
    </div>
  );
};

export default FileUploader;
