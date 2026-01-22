import { Link } from 'react-router-dom';

export function Dashboard() {
  return (
    <div className="min-h-screen bg-gunmetal p-8">
      <h1 className="text-3xl font-bold text-white mb-4">Nova Geração</h1>
      <p className="text-textSec mb-6">Área de criação de Jobs (Placeholder)</p>
      <Link to="/gallery" className="text-primary hover:underline">Ir para Galeria &rarr;</Link>
    </div>
  );
}