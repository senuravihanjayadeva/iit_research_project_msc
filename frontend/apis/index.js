import axios from "axios";

export const uploadDentalImage = async (file, selectedModel, selectedCategory) => {
  const formData = new FormData();
  formData.append("file", file);
  selectedCategory && formData.append("category_id", selectedCategory);
  try {
    const URL = `http://162.243.49.66:8000/${selectedModel === 1 ? 'predict/model1':'predict/model2/custom'}`
    const response = await axios.post(URL, formData, {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    });
    console.log({response})
    return response.data; // assuming it returns the image URL or blob
  } catch (error) {
    console.error("Upload failed:", error);
    throw error;
  }
};
