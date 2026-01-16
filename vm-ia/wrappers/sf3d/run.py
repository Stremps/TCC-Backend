import argparse
import subprocess
import sys
import os
import shutil
import logging
from pathlib import Path
from dotenv import load_dotenv

# --- CONFIGURAÇÃO DE AMBIENTE ---
env_path = Path(__file__).resolve().parents[2] / '.env'
load_dotenv(env_path)

VENV_PYTHON = os.getenv("SF3D_PYTHON_PATH")
MODEL_SCRIPT = os.getenv("SF3D_SCRIPT_PATH")

# Configuração de Logs
logging.basicConfig(level=logging.INFO, format='%(asctime)s - [SF3D Wrapper] - %(message)s')
logger = logging.getLogger(__name__)

def run_inference(input_path: str, output_path: str, texture_res: int, remesh_option: str):
    """
    Executa a inferência do Stable Fast 3D isoladamente.
    """
    
    if not VENV_PYTHON or not MODEL_SCRIPT:
        logger.error("ERRO: Variáveis de ambiente SF3D_PYTHON_PATH ou SF3D_SCRIPT_PATH não definidas.")
        sys.exit(1)

    if not os.path.exists(input_path):
        logger.error(f"Arquivo de entrada não encontrado: {input_path}")
        sys.exit(1)

    # Preparação de Diretório Temporário
    temp_output_dir = Path(output_path).parent / f"temp_sf3d_{os.getpid()}"
    if temp_output_dir.exists():
        shutil.rmtree(temp_output_dir)
    os.makedirs(temp_output_dir, exist_ok=True)

    try:
        # Montagem do Comando
        # Ajuste: Removido ':0' do cuda, mantendo apenas 'cuda'
        cmd = [
            VENV_PYTHON,
            MODEL_SCRIPT,
            input_path,
            "--output-dir", str(temp_output_dir),
            "--texture-resolution", str(texture_res),
            "--remesh_option", remesh_option,
            "--device", "cuda" 
        ]

        logger.info(f"Iniciando subprocesso: {' '.join(cmd)}")

        # Execução
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=os.path.dirname(MODEL_SCRIPT) 
        )

        # --- LOG DINÂMICO ---
        # Agora mostramos o que o modelo falou (Ex: "Device used: cuda")
        # Isso atende ao seu pedido de ver o log real em vez de uma string fixa.
        if result.stdout:
            logger.info(f"--- OUTPUT MODELO ---\n{result.stdout.strip()}\n---------------------")

        if result.returncode != 0:
            logger.error("STDERR do Modelo:")
            logger.error(result.stderr)
            raise RuntimeError(f"O script do modelo falhou com código {result.returncode}")

        # Captura do Artefato
        found_glbs = list(temp_output_dir.rglob("*.glb"))

        if not found_glbs:
            logger.error(f"Nenhum .glb encontrado em {temp_output_dir}")
            raise FileNotFoundError("O modelo não gerou o arquivo .glb esperado.")

        source_file = found_glbs[0]
        
        # Move para o destino final
        shutil.move(str(source_file), output_path)
        logger.info(f"Sucesso! Resultado salvo em: {output_path}")

    except Exception as e:
        logger.error(f"Erro durante a inferência: {e}")
        sys.exit(1)
    
    finally:
        # Faxina
        if os.path.exists(temp_output_dir):
            shutil.rmtree(temp_output_dir)
            logger.info("Limpeza temporária concluída.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Wrapper CLI para Stable Fast 3D")
    parser.add_argument("--input_path", required=True, help="Caminho da imagem de entrada")
    parser.add_argument("--output_path", required=True, help="Caminho onde salvar o GLB final")
    parser.add_argument("--texture_resolution", type=int, default=1024, help="Resolução da textura")
    parser.add_argument("--remesh_option", type=str, default="triangle", help="Opção de remesh")

    args = parser.parse_args()

    run_inference(
        args.input_path,
        args.output_path,
        args.texture_resolution,
        args.remesh_option
    )
