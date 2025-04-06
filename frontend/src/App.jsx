import { useState } from "react";
import { uploadDentalImage } from "../apis";
import "./App.css";
import FileUploader from "./components/FileUploader";
import ImagePreview from "./components/ImagePreview";
import { FaTooth } from "react-icons/fa";

const App = () => {
  const [image, setImage] = useState(null);
  const [file, setFile] = useState(null);
  const [url, setUrl] = useState(null);

  const handleFile = (file) => {
    setFile(file);
    setImage(URL.createObjectURL(file));
  };

  const onClickReset = () => {
    setImage(null);
    setUrl(null);
  };

  const onClickProcess = async () => {
    const response = await uploadDentalImage(file);
    response?.result_image_url && setUrl(response?.result_image_url);
  };

  return (
    <div className="min-h-screen text-white bg-[linear-gradient(-45deg,#111827,#1e293b,#0f172a,#1e1b4b,#111827)] bg-[length:300%_300%] [animation:wave_8s_ease-in-out_infinite]">
      <div className="flex justify-center pt-5">
        <FaTooth size={50}/>
        <div className="p-3 rounded-2xl">
          <p className="text-gray-300 text-2xl font-bold">Denti-Scan</p>
        </div>
      </div>
      {!image && (
        <div className="flex justify-center pt-5">
          <FileUploader onFileSelected={handleFile} />
        </div>
      )}
      {image && (
        <div className="flex justify-center pt-5">
          <div className="bg-gray-300 p-3 m-3 rounded-xl">
            <h2 className="text-lg mb-1 text-center text-gray-900">Preview</h2>
            <ImagePreview image={image} />
          </div>
          {url && (
            <div className="bg-gray-300 p-3 m-3 rounded-xl">
              <h2 className="text-lg mb-1 text-center text-gray-900">Predict</h2>
              <ImagePreview image={url} />
            </div>
          )}
        </div>
      )}
      <div className="flex justify-center pt-5 pb-5 space-x-5">
        <button
          className="bg-gray-300 hover:bg-gray-900 text-gray-900 hover:text-gray-300 border hover:border-gray-300 font-bold py-2 px-5 rounded-xl cursor-pointer"
          onClick={onClickReset}
        >
          RESET
        </button>
        <button
          className="bg-gray-300 hover:bg-gray-900 text-gray-900 hover:text-gray-300 border hover:border-gray-300 font-bold py-2 px-5 rounded-xl cursor-pointer"
          onClick={onClickProcess}
        >
          PREDICT
        </button>
      </div>
    </div>
  );
};

export default App;
