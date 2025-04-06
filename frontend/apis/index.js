import axios from "axios";

export const uploadDentalImage = async (file) => {
  const formData = new FormData();
  formData.append("file", file);

  try {
    const response = await axios.post("http://134.122.38.78:8000/predict", formData, {
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
