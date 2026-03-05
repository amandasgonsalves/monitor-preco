import concurrent.futures
import json
import os
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options

# Diretório para salvar os resultados
RESULTADOS_DIR = 'resultados'
os.makedirs(RESULTADOS_DIR, exist_ok=True)

def buscar_produto(produto):
    """Realiza a busca de um produto no Google Shopping."""
    options = Options()
    options.add_argument('--headless')  # Desativa a visualização do navegador
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')

    driver = webdriver.Chrome(service=Service(), options=options)

    try:
        driver.get("https://www.google.com.br/shopping")
        time.sleep(2)

        # Interagir com a barra de busca
        search_box = driver.find_element(By.NAME, "q")
        search_box.send_keys(produto)
        search_box.send_keys(Keys.RETURN)
        time.sleep(3)

        # Coletar resultados
        resultados = []
        items = driver.find_elements(By.CSS_SELECTOR, ".sh-dgr__grid-result")
        for item in items[:5]:  # Limitar a 5 resultados por produto
            try:
                nome = item.find_element(By.CSS_SELECTOR, ".sh-np__product-title").text
                preco = item.find_element(By.CSS_SELECTOR, ".T14wmb").text
                loja = item.find_element(By.CSS_SELECTOR, ".E5ocAb").text
                link = item.find_element(By.CSS_SELECTOR, "a").get_attribute("href")

                resultados.append({
                    "nome": nome,
                    "preco": preco,
                    "loja": loja,
                    "link": link
                })
            except Exception as e:
                print(f"Erro ao coletar informações de um item: {e}")

        return resultados

    finally:
        driver.quit()

def salvar_resultado(produto, resultado):
    """Salva o resultado da busca em um arquivo JSON."""
    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    arquivo = os.path.join(RESULTADOS_DIR, f"resultado_{produto}_{timestamp}.json")
    with open(arquivo, 'w', encoding='utf-8') as f:
        json.dump(resultado, f, ensure_ascii=False, indent=4)

def executar_busca(produto):
    """Executa a busca para um único produto e salva o resultado."""
    time.sleep(2)  # Adiciona um atraso para evitar conflitos entre threads
    resultado = buscar_produto(produto)
    salvar_resultado(produto, resultado)

def busca_em_massa(produtos):
    """Realiza buscas em massa de forma paralela com controle de threads."""
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:  # Limita o número de threads simultâneas
        executor.map(executar_busca, produtos)

if __name__ == "__main__":
    # Carregar produtos do arquivo temporário
    with open("produtos_temp.txt", "r", encoding="utf-8") as f:
        produtos = [linha.strip() for linha in f if linha.strip()]

    # Realizar buscas em massa
    busca_em_massa(produtos)
