import os
import json
import hashlib
from PIL import Image

LOG_FILE = os.path.join(os.path.dirname(__file__), 'instance', 'optimized_image_log.json')

def load_optimization_log():
    if os.path.exists(LOG_FILE):
        try:
            with open(LOG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_optimization_log(log_data):
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    with open(LOG_FILE, 'w', encoding='utf-8') as f:
        json.dump(log_data, f, ensure_ascii=False, indent=2)

def compute_file_hash(filepath):
    hasher = hashlib.sha256()
    try:
        with open(filepath, 'rb') as f:
            while chunk := f.read(65536):
                hasher.update(chunk)
        return hasher.hexdigest()
    except Exception:
        return ""

def scan_and_analyze_images(static_folder):
    """
    Modo Auditoria (Dry-Run): Realiza varredura completa das imagens sem modificar arquivos.
    """
    log = load_optimization_log()
    img_dir = os.path.join(static_folder, 'img')
    
    target_extensions = {'.jpg', '.jpeg', '.png', '.webp'}
    items = []
    
    total_bytes = 0
    heavy_count = 0
    estimated_savings_bytes = 0
    optimized_count = 0
    pending_count = 0

    if os.path.exists(img_dir):
        for root, _, files in os.walk(img_dir):
            for file in files:
                ext = os.path.splitext(file)[1].lower()
                if ext not in target_extensions:
                    continue

                filepath = os.path.join(root, file)
                rel_path = os.path.relpath(filepath, static_folder).replace('\\', '/')
                
                try:
                    file_size = os.path.getsize(filepath)
                except OSError:
                    continue

                total_bytes += file_size
                size_kb = round(file_size / 1024, 1)
                size_mb = round(file_size / (1024 * 1024), 2)
                
                width, height, fmt = 0, 0, ext.replace('.', '').upper()
                try:
                    with Image.open(filepath) as img:
                        width, height = img.size
                        fmt = img.format or fmt
                except Exception:
                    pass

                file_hash = compute_file_hash(filepath)
                is_logged = file_hash in log or rel_path in log

                # Categorização
                rel_lower = rel_path.lower()
                if 'banner' in rel_lower or 'hero' in rel_lower:
                    category = 'Banners'
                elif 'store' in rel_lower or 'product' in rel_lower:
                    category = 'Produtos'
                elif 'brand' in rel_lower or 'logo' in rel_lower or 'marca' in rel_lower:
                    category = 'Marcas / Drops'
                elif 'catraca' in rel_lower:
                    category = 'Catraca / Equipamentos'
                else:
                    category = 'Institucional'

                is_heavy = size_kb > 250
                if is_heavy:
                    heavy_count += 1

                if is_logged or (ext == '.webp' and not is_heavy):
                    status = 'otimizada'
                    status_label = 'Otimizada'
                    badge_color = 'green'
                    optimized_count += 1
                    est_savings = 0
                elif is_heavy:
                    status = 'pesada'
                    status_label = 'Pesada (>250KB)'
                    badge_color = 'red'
                    pending_count += 1
                    est_savings = int(file_size * 0.65)
                else:
                    status = 'pendente'
                    status_label = 'Pendente (JPG/PNG)'
                    badge_color = 'yellow'
                    pending_count += 1
                    est_savings = int(file_size * 0.45)

                estimated_savings_bytes += est_savings

                items.append({
                    'rel_path': rel_path,
                    'filename': file,
                    'category': category,
                    'size_bytes': file_size,
                    'size_kb': size_kb,
                    'size_mb': size_mb,
                    'width': width,
                    'height': height,
                    'format': fmt,
                    'is_heavy': is_heavy,
                    'status': status,
                    'status_label': status_label,
                    'badge_color': badge_color,
                    'estimated_savings_kb': round(est_savings / 1024, 1),
                    'hash': file_hash
                })

    # Ordenar por tamanho decrescente
    items.sort(key=lambda x: x['size_bytes'], reverse=True)

    summary = {
        'total_scanned': len(items),
        'total_weight_mb': round(total_bytes / (1024 * 1024), 2),
        'heavy_count': heavy_count,
        'projected_savings_mb': round(estimated_savings_bytes / (1024 * 1024), 2),
        'optimized_count': optimized_count,
        'pending_count': pending_count
    }

    return {
        'summary': summary,
        'items': items
    }

def optimize_images(file_paths, profile='balanced', static_folder=None):
    """
    Executa a compressão/conversão das imagens com base no perfil selecionado.
    Perfis disponíveis:
      - 'balanced': max 1280px, qualidade 80
      - 'ultra': max 1000px, qualidade 72
      - 'hq': max 1400px, qualidade 85
    """
    log = load_optimization_log()
    
    profiles_map = {
        'balanced': {'max_dim': 1280, 'quality': 80},
        'ultra': {'max_dim': 1000, 'quality': 72},
        'hq': {'max_dim': 1400, 'quality': 85}
    }
    config = profiles_map.get(profile, profiles_map['balanced'])
    max_dim = config['max_dim']
    quality = config['quality']

    results = []
    total_saved_bytes = 0

    if not static_folder:
        return {'success': False, 'error': 'static_folder não fornecido.'}

    for rel_path in file_paths:
        filepath = os.path.join(static_folder, rel_path.replace('/', os.sep))
        if not os.path.exists(filepath):
            results.append({'rel_path': rel_path, 'success': False, 'error': 'Arquivo não encontrado.'})
            continue

        try:
            original_size = os.path.getsize(filepath)
            with Image.open(filepath) as img:
                orig_width, orig_height = img.size
                img_format = img.format or 'JPEG'

                # Redimensionar se exceder max_dim
                new_width, new_height = orig_width, orig_height
                if orig_width > max_dim or orig_height > max_dim:
                    if orig_width >= orig_height:
                        new_width = max_dim
                        new_height = int(orig_height * (max_dim / orig_width))
                    else:
                        new_height = max_dim
                        new_width = int(orig_width * (max_dim / orig_height))
                    img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

                # Converter modo RGBA para RGB se salvar em JPEG/WebP sem alfa
                if img.mode in ('RGBA', 'LA', 'P') and img_format.upper() in ('JPEG', 'JPG'):
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                    img = background
                elif img.mode not in ('RGB', 'RGBA'):
                    img = img.convert('RGB')

                # Salvar otimizado
                save_kwargs = {'quality': quality, 'optimize': True}
                if filepath.lower().endswith('.webp'):
                    save_kwargs['method'] = 6
                    img.save(filepath, 'WEBP', **save_kwargs)
                else:
                    if filepath.lower().endswith(('.jpg', '.jpeg')):
                        img.save(filepath, 'JPEG', **save_kwargs)
                    elif filepath.lower().endswith('.png'):
                        img.save(filepath, 'PNG', optimize=True)

            new_size = os.path.getsize(filepath)
            saved_bytes = max(0, original_size - new_size)
            total_saved_bytes += saved_bytes
            new_hash = compute_file_hash(filepath)

            log[new_hash] = {
                'rel_path': rel_path,
                'original_size': original_size,
                'new_size': new_size,
                'profile': profile,
                'dimensions': [new_width, new_height]
            }
            log[rel_path] = new_hash

            results.append({
                'rel_path': rel_path,
                'success': True,
                'original_size_kb': round(original_size / 1024, 1),
                'new_size_kb': round(new_size / 1024, 1),
                'saved_kb': round(saved_bytes / 1024, 1),
                'dimensions': f"{new_width}x{new_height}"
            })
        except Exception as e:
            results.append({'rel_path': rel_path, 'success': False, 'error': str(e)})

    save_optimization_log(log)

    return {
        'success': True,
        'profile_used': profile,
        'total_processed': len(results),
        'total_saved_mb': round(total_saved_bytes / (1024 * 1024), 2),
        'details': results
    }
