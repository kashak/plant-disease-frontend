import { Link, useLocation } from 'react-router-dom';

export default function Result() {
  const location = useLocation();
  const resultData = location.state?.resultData || {
    disease: 'Tomato Early Blight',
    confidence: 94,
    severity: 'Medium',
    cause: 'Caused by the fungal pathogen Alternaria solani. It thrives in warm, humid conditions.',
    cure: 'Remove affected lower leaves immediately. Apply a copper-based fungicide every 7 to 10 days and avoid overhead watering.',
  };

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col items-center justify-center p-6">
      <div className="bg-white p-8 rounded-xl shadow-md w-full max-w-lg text-left">
        <h2 className="text-2xl font-bold text-gray-800 mb-1">
          Analysis Results
        </h2>
        <p className="text-sm text-gray-500 mb-6">
          Based on the uploaded leaf scan
        </p>

        <div className="bg-green-50 p-4 rounded-lg mb-6 border border-green-200">
          <div className="flex justify-between items-center mb-1">
            <h3 className="text-xl font-bold text-green-900">
              {resultData.disease}
            </h3>
            <span className="bg-green-600 text-white text-xs font-semibold px-2.5 py-1 rounded-full">
              {resultData.confidence}% Match
            </span>
          </div>
        </div>

        <div className="mb-6">
          <div className="flex justify-between text-sm font-semibold text-gray-700 mb-2">
            <span>Severity Level</span>
            <span className="text-amber-600">{resultData.severity}</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-3">
            <div
              className="bg-amber-500 h-3 rounded-full"
              style={{ width: '65%' }}
            ></div>
          </div>
        </div>

        <div className="mb-4">
          <h4 className="font-semibold text-gray-800 mb-1">Possible Cause</h4>
          <p className="text-gray-600 text-sm leading-relaxed">
            {resultData.cause}
          </p>
        </div>

        <div className="mb-8">
          <h4 className="font-semibold text-gray-800 mb-1">Recommended Treatment</h4>
          <p className="text-gray-600 text-sm leading-relaxed">
            {resultData.cure}
          </p>
        </div>

        <Link
          to="/scan"
          className="block w-full text-center py-3 bg-gray-800 text-white font-semibold rounded-lg shadow hover:bg-gray-900 transition"
        >
          Scan Another Leaf
        </Link>
      </div>
    </div>
  );
}