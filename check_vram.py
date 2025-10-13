import pynvml

try:
    pynvml.nvmlInit()
    handle = pynvml.nvmlDeviceGetHandleByIndex(0)
    info = pynvml.nvmlDeviceGetMemoryInfo(handle)
    
    total_gb = info.total / (1024**3)
    free_gb = info.free / (1024**3)
    
    print(f"--- GPU Hardware Check ---")
    print(f"GPU Name: {pynvml.nvmlDeviceGetName(handle)}")
    print(f"Total VRAM: {total_gb:.2f} GB")
    print(f"Free VRAM: {free_gb:.2f} GB")
    
except pynvml.NVMLError as e:
    print(f"Could not find an NVIDIA GPU or pynvml error: {e}")
    print("If you have an AMD GPU, you will need to check VRAM using a different tool (e.g., 'rocm-smi').")

finally:
    try:
        pynvml.nvmlShutdown()
    except:
        pass
