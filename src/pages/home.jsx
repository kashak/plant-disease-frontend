import { Link } from 'react-router-dom';

export default function Home() {
  return (
    <div className="min-h-screen bg-gray-50 flex flex-col items-center justify-center p-6 text-center">
      <div className="bg-white p-8 rounded-xl shadow-md w-full max-w-lg">
        {/* AgroScan Icon */}
        <div className="w-16 h-16 bg-green-100 text-green-600 rounded-full flex items-center justify-center mx-auto mb-4 text-3xl">
          🌿
        </div>

        {/* App Title & Tagline */}
        <h1 className="text-3xl font-extrabold text-gray-900 mb-3">
          AgroScan
        </h1>
        <p className="text-gray-600 text-base mb-8 leading-relaxed">
          Detect crop diseases early with AI. Upload a clear picture of an affected leaf to get instant diagnosis and recommended treatments.
        </p>

        {/* CTA Button */}
        <Link
          to="/scan"
          className="inline-block w-full py-3 bg-green-600 text-white font-semibold rounded-lg shadow-md hover:bg-green-700 transition duration-200"
        >
          Scan Leaf Now
        </Link>
      </div>
    </div>
  );
}