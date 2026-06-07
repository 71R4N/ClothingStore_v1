# === Ячейка исправления окружения (Запустить один раз) ===
import sys
import os

# 1. Устанавливаем PyTorch 2.3.1 (в нем есть device_mesh, необходимый для новых diffusers)
!pip install -q torch==2.3.1 torchvision==0.18.1 torchaudio==2.3.1 --index-url https://download.pytorch.org/whl/cu121

# 2. Полностью удаляем xformers, чтобы избежать ошибки infer_schema
!pip uninstall -y xformers

# 3. Устанавливаем совместимые версии diffusers и accelerate
!pip install -q diffusers==0.29.2 accelerate==0.32.1 transformers==4.42.4

# 4. Чистим кэш импорта Python в памяти Colab
for mod in list(sys.modules.keys()):
    if 'torch' in mod or 'diffusers' in mod or 'xformers' in mod or 'accelerate' in mod:
        del sys.modules[mod]

print("✅ Окружение исправлено. Теперь запустите ячейку создания main.py и ячейку запуска uvicorn.")

%%writefile
main.py
"""
FastAPI-сервис для инференса модели CatVTON.
"""
import sys
import os
import types
import torch
import torch.distributed
import io
import base64
import logging
from typing import Optional
from contextlib import asynccontextmanager

# ============================================================================
# CRITICAL FIX 1: Mock torch.distributed.device_mesh
# ============================================================================
if not hasattr(torch.distributed, 'device_mesh'):
    mock_device_mesh = types.ModuleType('device_mesh')


    class DeviceMesh:
        pass


    mock_device_mesh.DeviceMesh = DeviceMesh
    torch.distributed.device_mesh = mock_device_mesh
    sys.modules['torch.distributed.device_mesh'] = mock_device_mesh

# ============================================================================
# CRITICAL FIX 2: Block xformers and flash_attn
# ============================================================================
for mod in list(sys.modules.keys()):
    if 'xformers' in mod or 'flash_attn' in mod:
        del sys.modules[mod]
sys.modules['xformers'] = None
sys.modules['xformers.ops'] = None
sys.modules['xformers.profiler'] = None
sys.modules['xformers.components'] = None
sys.modules['flash_attn'] = None
sys.modules['flash_attn.flash_attn_interface'] = None

os.environ["DIFFUSERS_USE_XFORMERS"] = "0"
os.environ["USE_FLASH_ATTENTION"] = "0"


# ============================================================================
# CRITICAL FIX 3: Bulletproof Mock for torch.xpu
# Перехватывает обращения к ЛЮБЫМ методам (manual_seed, amp, autocast и т.д.)
# ============================================================================
class XPUMock:
    """Универсальный мок для torch.xpu, предотвращающий AttributeError."""

    def __getattr__(self, name):
        # Возвращаем функцию-заглушку для любого запрашиваемого атрибута
        return lambda *args, **kwargs: None


# Применяем мок, если xpu отсутствует или не имеет нужных методов
if not hasattr(torch, 'xpu') or not hasattr(torch.xpu, 'manual_seed'):
    torch.xpu = XPUMock()
# ============================================================================

from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from PIL import Image
from starlette.concurrency import run_in_threadpool

# Добавляем путь к CatVTON
catvton_path = os.path.abspath("./CatVTON")
if catvton_path not in sys.path:
    sys.path.insert(0, catvton_path)

from huggingface_hub import snapshot_download
from model.cloth_masker import AutoMasker
from model.pipeline import CatVTONPipeline
from utils import resize_and_crop, resize_and_padding
from diffusers.image_processor import VaeImageProcessor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

pipeline = None
automasker = None
mask_processor = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global pipeline, automasker, mask_processor
    logger.info("🚀 Загрузка весов CatVTON и Stable Diffusion...")

    try:
        repo_path = snapshot_download(repo_id="zhengchong/CatVTON")

        pipeline = CatVTONPipeline(
            base_ckpt="runwayml/stable-diffusion-inpainting",
            attn_ckpt=repo_path,
            attn_ckpt_version="mix",
            weight_dtype=torch.float16,
            use_tf32=True,
            device='cuda'
        )

        automasker = AutoMasker(
            densepose_ckpt=os.path.join(repo_path, "DensePose"),
            schp_ckpt=os.path.join(repo_path, "SCHP"),
            device='cuda',
        )

        mask_processor = VaeImageProcessor(
            vae_scale_factor=8, do_normalize=False,
            do_binarize=True, do_convert_grayscale=True
        )
        logger.info("✅ Модель успешно загружена и готова к инференсу.")
    except Exception as e:
        logger.error(f"❌ Ошибка загрузки модели: {e}")
        raise

    yield

    del pipeline, automasker
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
    logger.info("🧹 Ресурсы GPU освобождены.")


app = FastAPI(title="CatVTON Inference Service", version="1.0.0", lifespan=lifespan)


@app.get("/health")
async def health_check():
    return {
        "status": "ok",
        "model_loaded": pipeline is not None,
        "device": "cuda" if torch.cuda.is_available() else "cpu",
    }


@app.post("/predict")
async def predict(
        person_image: UploadFile = File(...),
        garment_image: UploadFile = File(...),
        mask_image: Optional[UploadFile] = File(None),
        category: str = Form("upper_body"),
        num_inference_steps: int = Form(30),
        guidance_scale: float = Form(2.5),
):
    if pipeline is None:
        raise HTTPException(status_code=503, detail="Model is not loaded yet")

    try:
        person_pil = Image.open(io.BytesIO(await person_image.read())).convert("RGB")
        garment_pil = Image.open(io.BytesIO(await garment_image.read())).convert("RGB")

        person_pil = resize_and_crop(person_pil, (768, 1024))
        garment_pil = resize_and_padding(garment_pil, (768, 1024))

        mask_pil = None
        if mask_image:
            mask_pil = Image.open(io.BytesIO(await mask_image.read())).convert("L")
            mask_pil = resize_and_crop(mask_pil, (768, 1024))
        else:
            cloth_type_map = {"upper_body": "upper", "lower_body": "lower", "dresses": "overall"}
            cloth_type = cloth_type_map.get(category, "upper")
            mask_pil = automasker(person_pil, cloth_type)['mask']

        if mask_processor:
            mask_pil = mask_processor.blur(mask_pil, blur_factor=9)

        def run_inference():
            generator = torch.Generator(device='cuda').manual_seed(42)
            result = pipeline(
                image=person_pil,
                condition_image=garment_pil,
                mask=mask_pil,
                num_inference_steps=num_inference_steps,
                guidance_scale=guidance_scale,
                generator=generator
            )
            return result[0]

        output_image = await run_in_threadpool(run_inference)

        buffer = io.BytesIO()
        output_image.save(buffer, format="JPEG", quality=90, optimize=True)
        img_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")

        return {
            "status": "success",
            "result_image_base64": img_base64,
            "format": "jpeg",
            "size_bytes": len(buffer.getvalue()),
        }

    except Exception as exc:
        logger.error(f"Inference failed: {exc}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Inference error: {str(exc)}")













    # Очистка возможных предыдущих установок
    !rm - rf
    clo
    clo - 3.1
    .0 - stable - linux - x86_64.tar.gz

    # Загрузка утилиты CloudPub
    !wget - q
    https: // cloudpub.ru / download / stable / clo - 3.1
    .0 - stable - linux - x86_64.tar.gz

    # Распаковка архива
    !tar - xzf
    clo - 3.1
    .0 - stable - linux - x86_64.tar.gz

    # Установка прав на выполнение
    !chmod + x
    clo

    # Настройка токена авторизации CloudPub
    !./ clo
    set
    token
    HHqJYj4gEX9pk5UE - 164
    ZTYn1EK0g8IULKok - tD - n4I









    # 1. Полностью удаляем xformers и flash-attn, чтобы они не ломали импорт
    !pip
    uninstall - y
    xformers
    flash - attn

    # 2. Устанавливаем актуальный PyTorch (>= 2.4), требуемый для transformers
    !pip
    install - U
    torch
    torchvision
    torchaudio - -index - url
    https: // download.pytorch.org / whl / cu121

    # 3. Обновляем diffusers и transformers
    !pip
    install - U
    diffusers
    transformers
    accelerate
    safetensors

    print("✅ Окружение обновлено. Теперь перезапустите ячейку с запуском uvicorn.")




















    # 1. Полное удаление конфликтующих пакетов
    !pip
    uninstall - y
    transformers
    diffusers
    accelerate
    torchvision
    xformers

    # 2. Установка стабильных версий с принудительной перезаписью
    !pip
    install - q - -force - reinstall \
            transformers == 4.44
    .2 \
            diffusers == 0.30
    .3 \
            accelerate == 0.34
    .2 \
            torchvision == 0.19
    .0 \
            Pillow

    import subprocess
    import time
    import threading
    import sys
    import re
    import os

    # Принудительно отключаем xformers и flash attention для diffusers
    os.environ["DIFFUSERS_USE_XFORMERS"] = "0"
    os.environ["USE_FLASH_ATTENTION"] = "0"

    print("🚀 Запуск ML-сервиса (uvicorn)...")
    proc = subprocess.Popen(
        ["uvicorn", "main:app", "--host", "127.0.0.1", "--port", "8000", "--workers", "1"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
        env={**os.environ, "DIFFUSERS_USE_XFORMERS": "0", "USE_FLASH_ATTENTION": "0"}
    )

    log_lines = []
    has_critical_error = False

    def read_logs():
        global has_critical_error
        try:
            for line in proc.stdout:
                line = line.rstrip()
                log_lines.append(line)
                if any(k in line for k in ["INFO", "WARNING", "ERROR", "Traceback", "Uvicorn running", "✅", "❌", "Загрузка", "OOM", "CUDA", "killed"]):
                    print(f"  [LOG] {line}")
                if "Traceback (most recent call last)" in line:
                    has_critical_error = True
                sys.stdout.flush()
        except Exception as e:
            print(f"  [LOG ERROR] {e}")

    log_thread = threading.Thread(target=read_logs, daemon=True)
    log_thread.start()

    print("⏳ Ожидание загрузки весов (может занять до 5 минут)...")
    ready = False
    critical_detected = False

    for i in range(300):
        time.sleep(1)
        if any("Uvicorn running" in line for line in log_lines):
            ready = True
            print(f"\n✅ Сервер запущен (через {i} сек)")
            break
        if has_critical_error:
            critical_detected = True
            print(f"\n❌ Обнаружен Traceback на {i}-й секунде.")
            time.sleep(2)
            break
        if proc.poll() is not None and i > 10:
            print(f"\n⚠️ Процесс завершился на {i}-й секунде с кодом {proc.poll()}")
            break

    if critical_detected or not ready:
        print("\n📋 ПОЛНЫЙ ЛОГ ДЛЯ ДИАГНОСТИКИ (последние 60 строк):")
        for line in log_lines[-60:]:
            print(line)

    print("\n🚀 Публикация ML-сервиса через CloudPub...")
    publish_proc = subprocess.Popen(
        ["./clo", "publish", "http", "8000"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
    )

    print("📡 Получение публичного URL:")
    public_url = None
    for i in range(30):
        line = publish_proc.stdout.readline()
        if line:
            print(line.rstrip())
            if "https://" in line and "cloudpub.ru" in line:
                url_match = re.search(r'https://[^\s]+\.cloudpub\.ru', line)
                if url_match:
                    public_url = url_match.group(0)
                    break
        if publish_proc.poll() is not None and i > 5:
            break

    if public_url:
        print(f"\n🔗 URL: {public_url}")
        print(f"Скопируйте и вставьте в .env:")
        print(f"CATVTON_API_URL={public_url}")
    else:
        print("❌ Не удалось получить публичный URL")