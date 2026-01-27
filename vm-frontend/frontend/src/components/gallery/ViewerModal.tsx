import { useEffect, useState, useRef } from 'react';

interface ViewerModalProps {
    isOpen: boolean;
    onClose: () => void;
    modelUrl: string | null;
    title: string;
    onDownload?: () => void;
}

export function ViewerModal({ isOpen, onClose, modelUrl, title, onDownload }: ViewerModalProps) {
    const [isVisible, setIsVisible] = useState(false);
    
    // Ref tipado como any pois a API do model-viewer não tem tipos TS oficiais exportados facilmente
    const viewerRef = useRef<any>(null); 

    useEffect(() => {
        if (isOpen) {
            requestAnimationFrame(() => setIsVisible(true));
        } else {
            setIsVisible(false);
        }
    }, [isOpen]);

    if (!isOpen && !isVisible) return null;

    const handleResetCamera = () => {
        const viewer = viewerRef.current;
        if (viewer) {
            // Acesso direto à API do Web Component
            viewer.cameraOrbit = '45deg 55deg 2.5m';
            viewer.fieldOfView = '30deg';
        }
    };

    return (
        <div 
            className={`fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm transition-opacity duration-300 ${
                isVisible ? 'opacity-100' : 'opacity-0'
            }`}
            onClick={onClose}
        >
            <div 
                className={`bg-surface w-full max-w-4xl h-[80vh] rounded-2xl border border-white/10 shadow-2xl flex flex-col relative transform transition-transform duration-300 ${
                    isVisible ? 'scale-100' : 'scale-95'
                }`}
                onClick={(e) => e.stopPropagation()}
            >
                {/* HEADER */}
                <div className="h-14 border-b border-white/5 flex items-center justify-between px-6 bg-gunmetal/50 rounded-t-2xl">
                    <div className="flex items-center gap-3">
                        <h3 className="font-semibold text-white truncate max-w-md">{title}</h3>
                        <span className="text-xs text-primary bg-primary/10 px-2 py-0.5 rounded border border-primary/20">
                            Visualização 3D
                        </span>
                    </div>
                    <div className="flex gap-4">
                        {onDownload && (
                            <button 
                                onClick={onDownload}
                                className="text-textSec hover:text-white transition-colors text-sm flex items-center gap-1"
                            >
                                <i className="fa-solid fa-download"></i> Baixar .GLB
                            </button>
                        )}
                        <button 
                            onClick={onClose} 
                            className="text-textSec hover:text-danger transition-colors text-lg"
                        >
                            <i className="fa-solid fa-xmark"></i>
                        </button>
                    </div>
                </div>

                {/* AREA DO VIEWER 3D */}
                <div className="flex-1 bg-gradient-to-b from-gunmetal to-black relative overflow-hidden rounded-b-2xl">
                    
                    {modelUrl && (
                        /* Agora sem @ts-ignore! */
                        <model-viewer
                            ref={viewerRef}
                            src={modelUrl}
                            alt={`Modelo 3D de ${title}`}
                            ar
                            auto-rotate
                            camera-controls
                            shadow-intensity="1"
                            camera-orbit="45deg 55deg 2.5m"
                            field-of-view="30deg"
                            style={{ width: '100%', height: '100%', backgroundColor: 'transparent' }}
                        >
                            <div slot="poster" className="flex items-center justify-center w-full h-full text-textSec bg-gunmetal/50">
                                <div className="flex flex-col items-center gap-3">
                                    <i className="fa-solid fa-cube fa-spin text-3xl text-primary"></i>
                                    <span className="text-sm animate-pulse">Carregando geometria...</span>
                                </div>
                            </div>
                        </model-viewer>
                    )}

                    {/* CONTROLES */}
                    <div className="absolute bottom-6 left-1/2 transform -translate-x-1/2 flex gap-2 bg-surface/80 backdrop-blur px-2 py-1.5 rounded-full border border-white/10 shadow-lg">
                        <button 
                            onClick={handleResetCamera}
                            className="w-8 h-8 rounded-full hover:bg-white/10 text-white flex items-center justify-center transition-colors" 
                            title="Resetar Câmera"
                        >
                            <i className="fa-solid fa-video"></i>
                        </button>
                        <button className="w-8 h-8 rounded-full hover:bg-white/10 text-white/50 cursor-not-allowed flex items-center justify-center">
                            <i className="fa-solid fa-border-all"></i>
                        </button>
                        <button className="w-8 h-8 rounded-full hover:bg-white/10 text-white/50 cursor-not-allowed flex items-center justify-center">
                            <i className="fa-solid fa-palette"></i>
                        </button>
                    </div>
                </div>

            </div>
        </div>
    );
}