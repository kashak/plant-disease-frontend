import { Link } from 'react-router-dom';

export default function Navbar() {
  return (
    <nav className="w-full bg-white shadow-md border-b border-gray-200 py-6 px-10 flex justify-between items-center">
      {/* Maximized App Title */}
      <Link to="/" className="text-3xl font-extrabold text-green-700 flex items-center gap-3 tracking-wide hover:opacity-90 transition">
        <span className="text-4xl">🌿</span> AgroScan
      </Link>

      {/* Maximized Links */}
      <div className="flex gap-10 text-lg font-bold text-gray-700">
        <Link to="/" className="hover:text-green-600 transition">
          Home
        </Link>
        <Link to="/scan" className="hover:text-green-600 transition">
          Scan
        </Link>
      </div>
    </nav>
  );
}