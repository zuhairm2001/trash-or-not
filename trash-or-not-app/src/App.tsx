import React, { useState, useRef, ChangeEvent, FormEvent } from 'react';
import axios from 'axios';

interface PredictionResult {
  prediction: string;
  confidence: number;
}

export default function ImageClassifier() {
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [result, setResult] = useState<PredictionResult | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileChange = (e: ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const selectedFile = e.target.files[0];
      setFile(selectedFile);
      setPreview(URL.createObjectURL(selectedFile));
      setResult(null);
      setError(null);
    }
  };

  const handleSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (!file) return;

    setLoading(true);
    setError(null);

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await axios.post<PredictionResult>('http://localhost:5000/predict', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      setResult(response.data);
    } catch (err) {
      setError('An error occurred while processing the image. Please try again.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleRetake = () => {
    setFile(null);
    setPreview(null);
    setResult(null);
    setError(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  return (
    <div className="min-h-screen bg-[#282828] py-6 flex flex-col items-center text-[#ebdbb2]">
      <div className="w-full max-w-md">
        <h1 className="text-3xl font-bold text-center mb-8 text-[#ebdbb2]">Trash or Not?</h1>
        <div className="bg-[#3c3836] shadow-lg rounded-lg p-6">
          <form onSubmit={handleSubmit} className="space-y-6">
            <div className="flex items-center justify-center w-full">
              <label className="flex flex-col items-center px-4 py-6 bg-[#504945] text-[#b8bb26] rounded-lg shadow-md tracking-wide uppercase border border-[#b8bb26] cursor-pointer hover:bg-[#665c54] hover:text-[#ebdbb2] transition duration-300">
                <span className="mt-2 text-base leading-normal">Select an image</span>
                <input
                  type="file"
                  className="hidden"
                  accept="image/*"
                  capture="environment"
                  onChange={handleFileChange}
                  ref={fileInputRef}
                />
              </label>
            </div>
            {preview && (
              <div className="mt-4">
                <img src={preview} alt="Preview" className="max-w-full h-auto rounded-lg" />
              </div>
            )}
            {file && (
              <div className="flex justify-between">
                <button
                  type="submit"
                  className="px-4 py-2 font-bold text-[#282828] bg-[#b8bb26] rounded-full hover:bg-[#98971a] focus:outline-none focus:shadow-outline transition duration-300"
                  disabled={loading}
                >
                  {loading ? 'Processing...' : 'Classify'}
                </button>
                <button
                  type="button"
                  onClick={handleRetake}
                  className="px-4 py-2 font-bold text-[#282828] bg-[#fb4934] rounded-full hover:bg-[#cc241d] focus:outline-none focus:shadow-outline transition duration-300"
                >
                  Retake
                </button>
              </div>
            )}
          </form>
          {result && (
            <div className="mt-6 p-4 bg-[#504945] rounded-lg">
              <h2 className="text-xl font-semibold text-[#ebdbb2] mb-2">Result:</h2>
              <p className="text-[#83a598]">Prediction: {result.prediction}</p>
              <p className="text-[#b8bb26]">Confidence: {(result.confidence * 100).toFixed(2)}%</p>
            </div>
          )}
          {error && (
            <div className="mt-6 p-4 bg-[#fb4934] bg-opacity-20 rounded-lg">
              <p className="text-[#fb4934]">{error}</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
