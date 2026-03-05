import concurrent.futures
import json
import os
import time
import random
from datetime import datetime

# Importa do main que já tem proteção anti-CAPTCHA
from main import buscar_produtos_patrocinados, salvar_resultados

# Diretório para salvar os resultados
RESULTADOS_DIR = 'resultados'
os.makedirs(RESULTADOS_DIR, exist_ok=True)

def executar_busca(produto, batch_id=None):
    """Executa a busca para um único produto usando o buscador com anti-CAPTCHA."""
    # Delay aleatório entre buscas para evitar detecção
    delay = random.uniform(5, 12)
    print(f"⏳ Aguardando {delay:.1f}s antes de buscar '{produto}'...")
    time.sleep(delay)
    
    resultado = buscar_produtos_patrocinados(produto)
    
    if resultado:
        nome_arquivo = f"resultado_{produto.replace(' ', '_').lower().replace('/', '_')}.json"
        salvar_resultados(resultado, nome_arquivo, batch_id=batch_id)
    
    return resultado

def busca_em_massa(produtos):
    """Realiza buscas em massa de forma SEQUENCIAL para evitar CAPTCHA.
    Buscas paralelas aumentam muito a chance de detecção pelo Google."""
    batch_id = time.strftime("%Y%m%d_%H%M%S")
    
    print(f"\n{'='*60}")
    print(f"🔍 BUSCA EM MASSA - {len(produtos)} produtos")
    print(f"📋 Batch ID: {batch_id}")
    print(f"⚠️ Modo sequencial para evitar CAPTCHA")
    print(f"{'='*60}\n")
    
    resultados = []
    for i, produto in enumerate(produtos, 1):
        print(f"\n[{i}/{len(produtos)}] Buscando: {produto}")
        resultado = executar_busca(produto, batch_id=batch_id)
        resultados.append(resultado)
    
    return resultados

if __name__ == "__main__":
    # Carregar produtos do arquivo temporário
    with open("produtos_temp.txt", "r", encoding="utf-8") as f:
        produtos = [linha.strip() for linha in f if linha.strip()]

    # Realizar buscas em massa
    busca_em_massa(produtos)
