import axios from "axios";

export const uploadDentalImage = async (file, selectedModel, selectedCategory) => {
  const formData = new FormData();
  formData.append("file", file);
  selectedCategory && formData.append("category_id", selectedCategory);
  try {
    const DOMAIN = '159.203.39.245';
    let URL = '';
    if(selectedModel === 1){
      URL = `http://${DOMAIN}:8000/predict/model1`
    }else if(selectedModel === 2){
      URL = `http://${DOMAIN}:8000/predict/model2/custom`
    }else if(selectedModel === 3){
      URL = `http://${DOMAIN}:8000/predict/model3/custom`
    }
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
