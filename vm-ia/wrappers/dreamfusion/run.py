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

VENV_PYTHON = os.getenv("DREAMFUSION_PYTHON_PATH")
MODEL_SCRIPT = os.getenv("DREAMFUSION_SCRIPT_PATH")
BASE_CONFIG = os.getenv("DREAMFUSION_CONFIG", "configs/dreamfusion-sd.yaml")

# Configuração de Logs
logging.basicConfig(level=logging.INFO, format='%(asctime)s - [DreamFusion Wrapper] - %(message)s')
logger = logging.getLogger(__name__)

def run_inference(prompt: str, output_path: str, max_steps: int = 1000):
    """
    Executa o pipeline completo do Threestudio: Treino -> Exportação.
    Args:
	max_steps: Mínimo forçado de 1000 steps para garantir geometria válida.
    """

    # Garantindo que tenha no mínimo 1000 steps
    if max_steps < 1000:
        logger.warning(f"Passos solicitados ({max_steps}) insuficientes para convergência de geometria.")
        logger.warning("Ajustando automaticamente para o MÍNIMO DE 1000 STEPS.")
        max_steps = 1000

    # 1. Validações
    if not VENV_PYTHON or not MODEL_SCRIPT:
        logger.error("ERRO: Variáveis de ambiente DREAMFUSION_* não definidas.")
        sys.exit(1)

    # Diretório raiz do modelo (para CWD)
    model_root = Path(MODEL_SCRIPT).parent
    
    # 2. Configuração de Variáveis de Ambiente (CUDA/TCNN e Warnings)
    env_vars = os.environ.copy()
    
    # Configurações Críticas de GPU
    env_vars["TCNN_CUDA_ARCHITECTURES"] = "86"
    env_vars["CUDA_HOME"] = "/usr/local/cuda-12.2"
    
    # Injeção do PATH do venv
    venv_bin = os.path.dirname(VENV_PYTHON)
    env_vars["PATH"] = f"{venv_bin}:{env_vars.get('PATH', '')}"
    
    # --- SUPRESSÃO DE WARNINGS ---
    # Limpa a poluição visual do PyTorch/Threestudio no terminal
    env_vars["PYTHONWARNINGS"] = "ignore"

    # Identificador único da execução
    job_tag = f"temp_df_{os.getpid()}"
    base_output_dir = model_root / "outputs" / job_tag

    try:
        # --- FASE 1: TREINAMENTO ---
        logger.info(f"--- FASE 1: TREINAMENTO (Steps: {max_steps}) ---")
        
        train_cmd = [
            VENV_PYTHON,
            MODEL_SCRIPT,
            "--config", BASE_CONFIG,
            "--train",
            "--gpu", "0",
            f"system.prompt_processor.prompt={prompt}",
            f"name={job_tag}",
            f"trainer.max_steps={max_steps}"
        ]

        logger.info(f"Executando Treino...")
        
        result_train = subprocess.run(
            train_cmd,
            cwd=model_root,
            env=env_vars,
            text=True
        )

        if result_train.returncode != 0:
            # Em caso de erro, não temos como suprimir o stderr, pois ele pode conter a causa
            raise RuntimeError(f"Falha na etapa de treinamento. Código: {result_train.returncode}")
        
        logger.info("Treinamento concluído.")

        # --- BUSCA DA PASTA DO EXPERIMENTO ---
        if not base_output_dir.exists():
            raise FileNotFoundError(f"Pasta de saída esperada não criada: {base_output_dir}")
        
        # Pega as subpastas (ex: "hamburger@20260115-220039")
        subdirs = [d for d in base_output_dir.iterdir() if d.is_dir()]
        
        if not subdirs:
             raise FileNotFoundError(f"Nenhuma subpasta de experimento encontrada em {base_output_dir}")
        
        real_experiment_dir = subdirs[0]
        logger.info(f"Pasta do experimento detectada: {real_experiment_dir}")

        # --- FASE 2: EXPORTAÇÃO (MESH) ---
        logger.info("--- FASE 2: EXPORTAÇÃO ---")
        
        parsed_config = real_experiment_dir / "configs" / "parsed.yaml"
        ckpt_file = real_experiment_dir / "ckpts" / "last.ckpt"

        if not parsed_config.exists():
            raise FileNotFoundError(f"Configuração parsed.yaml não encontrada.")
        
        if not ckpt_file.exists():
             raise FileNotFoundError(f"Checkpoint last.ckpt não encontrado.")

        export_cmd = [
            VENV_PYTHON,
            MODEL_SCRIPT,
            "--config", str(parsed_config),
            "--export",
            "--gpu", "0",
            f"resume={ckpt_file}",
            "system.exporter_type=mesh-exporter",
            "system.exporter.context_type=cuda",
            "system.exporter.fmt=obj"
        ]

        logger.info(f"Executando Export...")
        result_export = subprocess.run(
            export_cmd,
            cwd=model_root,
            env=env_vars,
            text=True
        )

        if result_export.returncode != 0:
            raise RuntimeError(f"Falha na etapa de exportação. Código: {result_export.returncode}")

        # --- FASE 3: CAPTURA E LIMPEZA ---
        save_dir = real_experiment_dir / "save"
        
        # Procura recursivamente por .obj (às vezes fica em it300-export/...)
        found_objs = list(save_dir.rglob("*.obj"))

        if not found_objs:
            if save_dir.exists():
                logger.error(f"Conteúdo de {save_dir}: {[p.name for p in save_dir.rglob('*')]}")
            logger.error(f"Nenhum .obj encontrado. Motivo provável: Treino muito curto (max_steps < 300) gerou geometria vazia.")
            raise FileNotFoundError("O Threestudio não gerou o arquivo de malha.")

        source_file = found_objs[0]
        
        shutil.move(str(source_file), output_path)
        logger.info(f"Sucesso! Modelo salvo em: {output_path}")

    except Exception as e:
        logger.error(f"Erro crítico: {e}")
        sys.exit(1)

    else:
        # --- FASE 4: FAXINA ---
        if base_output_dir.exists():
            logger.info(f"Removendo pasta temporária: {base_output_dir}")
            shutil.rmtree(base_output_dir)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Wrapper CLI para DreamFusion (Threestudio)")
    parser.add_argument("--prompt", required=True, help="Prompt de texto")
    parser.add_argument("--output_path", required=True, help="Destino do arquivo")
    # Alterado default para 300 para segurança
    parser.add_argument("--max_steps", type=int, default=1000, help="Passos de treino")

    args = parser.parse_args()

    run_inference(
        args.prompt,
        args.output_path,
        args.max_steps
    )
