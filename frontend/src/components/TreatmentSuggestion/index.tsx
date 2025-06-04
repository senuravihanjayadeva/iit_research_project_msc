import React from "react";

const TreatmentSuggestion = ({ recommendation }) => {
  return <div className="min-h-screen text-white bg-[linear-gradient(-45deg,#111827,#1e293b,#0f172a,#1e1b4b,#111827)] bg-[length:300%_300%] [animation:wave_8s_ease-in-out_infinite]"><div className="m-5 p-8 rounded-xl bg-white text-gray-800">{recommendation}</div></div>;
};
export default TreatmentSuggestion;
