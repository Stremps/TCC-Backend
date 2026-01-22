import { Link } from 'react-router-dom';

export function Gallery() {
  return (
    <div className="min-h-screen bg-gunmetal p-8">
      <h1 className="text-3xl font-bold text-white mb-4">Meus Jobs</h1>
      <p className="text-textSec mb-6">Histórico de criações (Placeholder)</p>
      <Link to="/dashboard" className="text-primary hover:underline">&larr; Voltar para Dashboard</Link>
    </div>
  );
}