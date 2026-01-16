# AI CLI Wrappers

Este diretório contém os scripts wrappers responsáveis por intermediar a comunicação entre o Worker (Orquestrador) e os Modelos de IA (Executores).

## Padrão de Arquitetura

Adotamos o padrão de isolamento de processos para evitar conflitos de dependências.
* **Worker:** Roda em Python 3.11+ (Ambiente Poetry limpo).
* **Modelos:** Rodam em seus próprios `venvs` (Python 3.10, CUDA específico, etc).
* **Comunicação:** O Wrapper é chamado via `subprocess`, recebe argumentos via CLI, e garante a entrega do arquivo final em um caminho especificado.

---

## 🖼️ 1. Stable Fast 3D (SF3D)
**Tipo:** Image-to-3D  
**Wrapper:** `sf3d/run.py`

Gera um modelo 3D rápido a partir de uma imagem única.

### Parâmetros
| Argumento | Obrigatório | Descrição | Exemplo |
| :--- | :---: | :--- | :--- |
| `--input_path` | Sim | Caminho absoluto da imagem de entrada (.png, .jpg) | `/tmp/cadeira.png` |
| `--output_path` | Sim | Caminho absoluto onde o .glb final deve ser salvo | `/tmp/saida.glb` |
| `--texture_resolution` | Não | Resolução da textura (Default: 1024) | `1024` |
| `--remesh_option` | Não | Algoritmo de malha (Default: triangle) | `triangle` |

### Exemplo de Uso Manual
```bash
python3 wrappers/sf3d/run.py \
  --input_path /home/user/img.png \
  --output_path /home/user/result.glb
```

---

## ✨ 2. DreamFusion (Threestudio)

**Tipo:** Text-to-3D

**Wrapper:** `dreamfusion/run.py`

Gera um modelo 3D a partir de um prompt de texto usando otimização SDS (Score Distillation Sampling). O processo envolve duas etapas automáticas: Treinamento e Exportação de Malha.

### Parâmetros

| Argumento | Obrigatório | Descrição | Exemplo |
| --- | --- | --- | --- |
| `--prompt` | Sim | Descrição textual do objeto | "a hamburger" |
| `--output_path` | Sim | Caminho absoluto onde o .obj final deve ser salvo | `/tmp/burger.obj` |
| `--max_steps` | Não | Passos de treino. Mínimo 300 para geometria válida. (Default: 300) | `5000` |

### Notas Técnicas

* O wrapper injeta automaticamente as variáveis `TCNN_CUDA_ARCHITECTURES=86` e `CUDA_HOME`.
* O script suprime warnings do PyTorch (`PYTHONWARNINGS=ignore`) para limpar o log.
* O processo é demorado. Para testes rápidos, use `--max_steps 300`. Para qualidade, use `5000+`.

### Exemplo de Uso Manual

```bash
python3 wrappers/dreamfusion/run.py \
  --prompt "a red sports car" \
  --output_path /home/user/car.obj \
  --max_steps 500

```
