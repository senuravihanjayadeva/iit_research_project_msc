import { useState } from "react";
import { getTreatmentPlan, uploadDentalImage } from "../apis";
import "./App.css";
import FileUploader from "./components/FileUploader";
import ImagePreview from "./components/ImagePreview";
import { FaTooth } from "react-icons/fa";
import { CircleLoader } from "react-spinners";
import TreatmentSuggestion from "./components/TreatmentSuggestion";

const App = () => {
  const [image, setImage] = useState(null);
  const [file, setFile] = useState(null);
  const [url, setUrl] = useState(null);
  const [selectedModel, setSelectedModel] = useState(1);
  const [selectedCategory, setSelectedCategory] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [recommendation, setRecommendation] = useState(null);

  const handleFile = (file) => {
    setFile(file);
    setImage(URL.createObjectURL(file));
  };

  const onClickReset = () => {
    setImage(null);
    setUrl(null);
    setSelectedModel(1);
    setSelectedCategory(null);
    setRecommendation(null);
  };

  const onClickProcess = async () => {
    setIsLoading(true);
    const response = await uploadDentalImage(
      file,
      selectedModel,
      selectedCategory
    );
    response?.result_image_url && setUrl(response?.result_image_url);
    setTimeout(() => {
      setIsLoading(false);
    }, 1000);
    const treatmentResponse = await getTreatmentPlan();
    setRecommendation(treatmentResponse.recommendation);
  };

  const onSelectModal = (selectedModel) => {
    setSelectedModel(selectedModel);
  };

  return (
    <div className="min-h-screen text-white bg-[linear-gradient(-45deg,#111827,#1e293b,#0f172a,#1e1b4b,#111827)] bg-[length:300%_300%] [animation:wave_8s_ease-in-out_infinite]">
      <div className="flex justify-center pt-5">
        <FaTooth size={50} />
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
          {isLoading ? (
            <div className="flex justify-center mt-3 relative w-full max-w-3xl h-[570px] border border-gray-100 rounded-md">
              <div className="self-center">
                <CircleLoader
                  color="white"
                  loading={true}
                  size={150}
                  aria-label="Loading Spinner"
                  data-testid="loader"
                />
              </div>
            </div>
          ) : (
            url && (
              <div className="bg-gray-300 p-3 m-3 rounded-xl">
                <h2 className="text-lg mb-1 text-center text-gray-900">
                  Predict
                </h2>
                <ImagePreview image={url} />
              </div>
            )
          )}
        </div>
      )}

      <div className="flex justify-center pt-5 pb-5 space-x-5">
        <button
          className={`${
            selectedModel === 1
              ? `bg-gray-900 text-gray-300`
              : `bg-gray-300 text-gray-900`
          } hover:bg-gray-900  hover:text-gray-300 border hover:border-gray-300 font-bold py-2 px-5 rounded-xl cursor-pointer`}
          onClick={() => {
            onSelectModal(1);
          }}
        >
          Model 1
        </button>
        <button
          className={`${
            selectedModel === 2
              ? `bg-gray-900 text-gray-300`
              : `bg-gray-300 text-gray-900`
          } hover:bg-gray-900 hover:text-gray-300 border hover:border-gray-300 font-bold py-2 px-5 rounded-xl cursor-pointer`}
          onClick={() => {
            onSelectModal(2);
          }}
        >
          Model 2
        </button>
        <button
          className={`${
            selectedModel === 3
              ? `bg-gray-900 text-gray-300`
              : `bg-gray-300 text-gray-900`
          } hover:bg-gray-900 hover:text-gray-300 border hover:border-gray-300 font-bold py-2 px-5 rounded-xl cursor-pointer`}
          onClick={() => {
            onSelectModal(3);
          }}
        >
          Model 3
        </button>
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
      {selectedModel === 2 && (
        <div className="flex justify-center pt-5 pb-5 space-x-5">
          <button
            className={`${
              selectedCategory === 1
                ? `bg-gray-900 text-gray-300`
                : `bg-gray-300 text-gray-900`
            } hover:bg-gray-900  hover:text-gray-300 border hover:border-gray-300 font-bold py-2 px-5 rounded-xl cursor-pointer`}
            onClick={() => {
              setSelectedCategory(1);
            }}
          >
            Cavity
          </button>
          <button
            className={`${
              selectedCategory === 2
                ? `bg-gray-900 text-gray-300`
                : `bg-gray-300 text-gray-900`
            } hover:bg-gray-900 hover:text-gray-300 border hover:border-gray-300 font-bold py-2 px-5 rounded-xl cursor-pointer`}
            onClick={() => {
              setSelectedCategory(2);
            }}
          >
            Fillings
          </button>
          <button
            className={`${
              selectedCategory === 3
                ? `bg-gray-900 text-gray-300`
                : `bg-gray-300 text-gray-900`
            } hover:bg-gray-900 hover:text-gray-300 border hover:border-gray-300 font-bold py-2 px-5 rounded-xl cursor-pointer`}
            onClick={() => {
              setSelectedCategory(3);
            }}
          >
            Impacted Tooth
          </button>
          <button
            className={`${
              selectedCategory === 4
                ? `bg-gray-900 text-gray-300`
                : `bg-gray-300 text-gray-900`
            } hover:bg-gray-900 hover:text-gray-300 border hover:border-gray-300 font-bold py-2 px-5 rounded-xl cursor-pointer`}
            onClick={() => {
              setSelectedCategory(4);
            }}
          >
            Implant
          </button>
          <button
            className={`${
              selectedCategory === 5
                ? `bg-gray-900 text-gray-300`
                : `bg-gray-300 text-gray-900`
            } hover:bg-gray-900 hover:text-gray-300 border hover:border-gray-300 font-bold py-2 px-5 rounded-xl cursor-pointer`}
            onClick={() => {
              setSelectedCategory(5);
            }}
          >
            infected-teeth
          </button>
        </div>
      )}
      {selectedModel === 3 && (
        <div className="flex justify-center pt-5 pb-5 space-x-5">
          <button
            className={`${
              selectedCategory === 1
                ? `bg-gray-900 text-gray-300`
                : `bg-gray-300 text-gray-900`
            } hover:bg-gray-900  hover:text-gray-300 border hover:border-gray-300 font-bold py-2 px-5 rounded-xl cursor-pointer`}
            onClick={() => {
              setSelectedCategory(1);
            }}
          >
            Caries
          </button>
          <button
            className={`${
              selectedCategory === 2
                ? `bg-gray-900 text-gray-300`
                : `bg-gray-300 text-gray-900`
            } hover:bg-gray-900 hover:text-gray-300 border hover:border-gray-300 font-bold py-2 px-5 rounded-xl cursor-pointer`}
            onClick={() => {
              setSelectedCategory(2);
            }}
          >
            Cavity
          </button>
          <button
            className={`${
              selectedCategory === 3
                ? `bg-gray-900 text-gray-300`
                : `bg-gray-300 text-gray-900`
            } hover:bg-gray-900 hover:text-gray-300 border hover:border-gray-300 font-bold py-2 px-5 rounded-xl cursor-pointer`}
            onClick={() => {
              setSelectedCategory(3);
            }}
          >
            Crack
          </button>
          <button
            className={`${
              selectedCategory === 4
                ? `bg-gray-900 text-gray-300`
                : `bg-gray-300 text-gray-900`
            } hover:bg-gray-900 hover:text-gray-300 border hover:border-gray-300 font-bold py-2 px-5 rounded-xl cursor-pointer`}
            onClick={() => {
              setSelectedCategory(4);
            }}
          >
            Tooth
          </button>
        </div>
      )}
      {recommendation && (
        <TreatmentSuggestion recommendation={recommendation} />
      )}
    </div>
  );
};

export default App;
