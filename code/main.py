import time
import re
import os
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class GoogleShoppingScraper:
    def __init__(self):
        # Setup Chrome options com configurações para evitar detecção de automação
        self.options = Options()
        
        # Configurações para evitar detecção como bot
        self.options.add_argument("--disable-blink-features=AutomationControlled")
        self.options.add_argument("--disable-infobars")
        self.options.add_argument("--window-size=1920,1080")  # Tamanho de janela comum
        self.options.add_argument("--start-maximized")
        
        # User agent de um navegador comum
        user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
        self.options.add_argument(f"user-agent={user_agent}")
        
        # Evitar sinais de automação
        self.options.add_experimental_option("excludeSwitches", ["enable-automation"])
        self.options.add_experimental_option("useAutomationExtension", False)
        
        # Inicializar o driver com as opções configuradas
        self.driver = webdriver.Chrome(options=self.options)
        
        # Modificar o navigator.webdriver para evitar detecção
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
    def human_like_typing(self, element, text):
        for char in text:
            element.send_keys(char)
            # Pausa aleatória entre 0.05 e 0.2 segundos
            time.sleep(random.uniform(0.05, 0.2))
    
    def random_sleep(self, min_seconds=2, max_seconds=5):
        time.sleep(random.uniform(min_seconds, max_seconds))
    
    def search_product(self, product_name):
        try:
            # Abrir o Google diretamente, não o Google Shopping (menos suspeito)
            print("Navegando até o Google...")
            self.driver.get("https://www.google.com.br")
            
            self.random_sleep(2, 4)
            
            # Verificar se há um botão de aceitar cookies e clicar nele
            try:
                accept_buttons = self.driver.find_elements(By.XPATH, 
                    "//button[contains(text(), 'Aceito') or contains(text(), 'Aceitar') or contains(text(), 'Concordo')]")
                if accept_buttons:
                    accept_buttons[0].click()
                    self.random_sleep(1, 2)
            except:
                print("Não foi necessário aceitar cookies.")
            
            # Mexer o mouse aleatoriamente para simular comportamento humano
            self.random_sleep(1, 3)
            
            # Encontrar o campo de busca do Google
            search_box = None
            
            # Tentar múltiplos seletores para o campo de busca
            selectors = ["input[name='q']", ".gLFyf", "#APjFqb", "input[title='Pesquisar']", "textarea[name='q']"]
            for selector in selectors:
                try:
                    search_box = WebDriverWait(self.driver, 3).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                    )
                    break
                except:
                    continue
            
            if not search_box:
                raise Exception("Não foi possível encontrar o campo de busca")
            
            # Clicar no campo de busca como um humano faria
            search_box.click()
            self.random_sleep(0.5, 1.5)
            
            # Limpar qualquer texto existente
            search_box.clear()
            self.random_sleep(0.5, 1)
            
            # Usar apenas o nome do produto como termo de busca
            search_term = product_name
            
            # Digitar como humano, com pausas entre caracteres
            self.human_like_typing(search_box, search_term)
            
            self.random_sleep(0.8, 2)
            
            # Pressionar Enter para pesquisar
            search_box.send_keys(Keys.RETURN)
            
            self.random_sleep(3, 5)
            
            # Clicar na aba Shopping usando o seletor específico
            try:
                shopping_tab = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "#hdtb-sc > div > div > div.crJ18e > div > div:nth-child(3) > a > div"))
                )
                shopping_tab.click()
            except Exception as e:
                
                # Lista de seletores alternativos para a aba Shopping
                alternative_selectors = [
                    "a[href*='tbm=shop']",
                    ".hdtb-mitem a[data-sc='shop']",
                    "div[jsname='BgbAdf'] a[data-sc='shop']",
                    "//a[contains(text(), 'Shopping')]",
                    "//div[contains(@class, 'hdtb-mitem')]//a[contains(text(), 'Shopping')]"
                ]
                
                found = False
                for selector in alternative_selectors:
                    try:
                        if selector.startswith("//"):
                            # xpath
                            element = WebDriverWait(self.driver, 5).until(
                                EC.element_to_be_clickable((By.XPATH, selector))
                            )
                        else:
                            # CSS Selector
                            element = WebDriverWait(self.driver, 5).until(
                                EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                            )
                        element.click()
                        found = True
                        break
                    except:
                        continue
                
                if not found:
                    print("Não foi possível encontrar a aba Shopping.")
            
            # Esperar que a página do Shopping carregue
            self.random_sleep(3, 5)
            
            # Se ainda precisar verificar CAPTCHA, pausar para interação manual
            if "captcha" in self.driver.page_source.lower() or "não sou um robô" in self.driver.page_source.lower():
                self.random_sleep(2, 3)
            
            # Extrair informações dos produtos
            return self.extract_product_info()
            
        except Exception as e:
            return []
    
    def extract_product_info(self):
        try:            
            # Esperar que a página carregue completamente
            self.random_sleep(4, 6)
            
            
            # Começar com o seletor específico mencionado
            results = []
            
            try:
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "#bGmlqc > div > div > div > div"))
                )
                
                elements = self.driver.find_elements(By.CSS_SELECTOR, "#bGmlqc > div > div > div > div")
                if elements:
                    for element in elements:
                        try:
                            text_content = element.text.strip()
                            if text_content:
                                results.append(text_content)
                        except Exception as e:
                            continue
            except Exception as e:
                print(f"Erro ao usar o seletor específico: {e}")
            
            if not results:
                try:
                    vplap_elements = self.driver.find_elements(By.CSS_SELECTOR, "[id^='vplap_']")
                    for element in vplap_elements:
                        text_content = element.text.strip()
                        if text_content:
                            results.append(text_content)
                except Exception as e:
                    print(f"Erro ao usar o seletor vplap: {e}")
            
            # Seletores possíveis para Google Shopping
            if not results:
                shopping_selectors = [
                    ".sh-dlr__list-result",
                    ".sh-dgr__grid-result",
                    ".sh-pr__product-result",
                    ".F4eCab",
                    ".dXQqNb",
                    ".jBQqof",
                    ".gm8XGd",
                    "div[data-pl]",
                    ".ZGFjDb",
                    ".i0X6df"
                ]
                
                for selector in shopping_selectors:
                    try:
                        elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                        if elements:
                            print(f"Encontrados {len(elements)} elementos com o seletor: {selector}")
                            for element in elements:
                                text_content = element.text.strip()
                                if text_content:
                                    results.append(text_content)
                                    print(f"Conteúdo encontrado: {text_content[:50]}...")
                    except Exception as e:
                        print(f"Erro ao usar seletor {selector}: {e}")
                        continue
            
            if not results:
                print("Tentando XPath para encontrar elementos de produto...")
                try:
                    product_elements = self.driver.find_elements(By.XPATH, "//div[contains(@class, 'sh-') and .//a[contains(@href, '/shopping/product')]]")
                    for element in product_elements:
                        text_content = element.text.strip()
                        if text_content:
                            results.append(text_content)
                except Exception as e:
                    print(f"Erro ao usar XPath: {e}")
            
            # Tentar método de scrolling para garantir que todos os elementos estejam carregados
            if not results or len(results) < 3: 
                #print("Tentando scroll para carregar mais conteúdo...")
                try:
                    for _ in range(3):
                        self.driver.execute_script("window.scrollBy(0, 500)")
                        self.random_sleep(1, 2)
                    
                    elements = self.driver.find_elements(By.CSS_SELECTOR, "#bGmlqc > div > div > div > div")
                    if elements:
                        for element in elements:
                            text_content = element.text.strip()
                            if text_content and text_content not in results:
                                results.append(text_content)
                                #print(f"Após scroll, conteúdo encontrado: {text_content[:50]}...")
                except Exception as e:
                    print(f"Erro durante scrolling: {e}")
            
            if not results:
                try:
                    # Obter todos os elementos com texto
                    all_elements = self.driver.find_elements(By.XPATH, "//*[not(self::script or self::style)][string-length(normalize-space(text())) > 10]")
                    for element in all_elements:
                        if element.is_displayed():
                            text = element.text.strip()
                            if text and len(text) > 15:  # Textos significativos
                                results.append(text)
                                #print(f"Texto visível encontrado: {text[:50]}...")
                except Exception as e:
                    print(f"Erro na coleta final de textos: {e}")
            
            # Se ainda não temos resultados, tentar acessar diretamente o primeiro produto
            if not results:
                #print("Tentando clicar no primeiro produto para obter detalhes...")
                try:
                    # Tentar clicar no primeiro produto
                    product_links = self.driver.find_elements(By.CSS_SELECTOR, "a[href*='/shopping/product']")
                    if product_links:
                        product_links[0].click()
                        self.random_sleep(3, 5)
                        
                        # Extrair informações da página de detalhes
                        details = self.driver.find_elements(By.XPATH, "//div[contains(@class, 'product-')]")
                        for detail in details:
                            text = detail.text.strip()
                            if text:
                                results.append(text)
                                #print(f"Detalhe de produto: {text[:50]}...")
                except Exception as e:
                    print(f"Erro ao acessar detalhes do produto: {e}")
            
            # Remover duplicatas e textos muito curtos
            cleaned_results = []
            seen = set()
            for result in results:
                if result not in seen and len(result) > 15:
                    cleaned_results.append(result)
                    seen.add(result)
            
            return cleaned_results
            
        except Exception as e:
            return []
    
    #função para: salvar os resultados em um arquivo de texto
    def save_to_file(self, product_name, results):
        if not os.path.exists("results"):
            os.makedirs("results")
            
        clean_name = re.sub(r'[\\/*?:"<>|]', "", product_name)
        clean_name = clean_name.replace(" ", "_")
        
        filename = f"results/{clean_name}_results.txt"
        
        # Processar os resultados para extrair produtos com preços
        produtos_processados = []
        
        print("Processando resultados para extrair informações de preço...")
        
        texto_completo = "\n".join(results)
        
        # Encontrar padrao de preço no texto completo
        todos_precos = re.findall(r'R\$\s*(\d+[,.]\d+)', texto_completo)
        
        # Processar cada bloco de resultado 
        for result in results:
            try:
                linhas = result.strip().split('\n')
                
                if len(linhas) < 2:
                    continue
                
                # Inicializar variáveis
                nome_produto = ""
                preco = ""
                valor_numerico = 9999999  
                loja = ""
                
                if not linhas[0].startswith("Patrocinado"):
                    nome_produto = linhas[0]
                elif len(linhas) > 1:
                    nome_produto = linhas[1]
                
                precos_encontrados = []
                indices_precos = []
                
                for i, linha in enumerate(linhas):
                    if "R$" in linha:
                        preco_match = re.search(r'R\$\s*(\d+[,.]\d+)', linha)
                        if preco_match:
                            
                            valor_texto = preco_match.group(1)
                            
                            valor = float(valor_texto.replace('.', '').replace(',', '.'))
                            
                            precos_encontrados.append({
                                'texto': linha.strip(),
                                'valor': valor,
                                'indice': i
                            })
                            indices_precos.append(i)
                
                # Se não encontrou preços, pular para o próximo resultado
                if not precos_encontrados:
                    continue
                
                # Usar o menor preço encontrado
                menor_preco = min(precos_encontrados, key=lambda x: x['valor'])
                preco = menor_preco['texto']
                valor_numerico = menor_preco['valor']
                indice_preco = menor_preco['indice']
                
                # Tentar encontrar a o nome da loja 
                if indice_preco + 1 < len(linhas) and "R$" not in linhas[indice_preco + 1]:
                    loja = linhas[indice_preco + 1]
                
                
                # Se encontramos as informações mínimas necessárias
                if nome_produto and preco:
                    produto = {
                        'nome': nome_produto,
                        'preco': preco,
                        'loja': loja,
                        'valor_numerico': valor_numerico,
                        'texto_original': result 
                    }
                    produtos_processados.append(produto)
                    print(f"Produto processado: {nome_produto} - {preco}")
            except Exception as e:
                
                continue

        
        produtos_ordenados = sorted(produtos_processados, key=lambda x: x['valor_numerico'])
        
        melhores_produtos = produtos_ordenados[:min(4, len(produtos_ordenados))]
        
        with open(filename, "w", encoding="utf-8") as file:
            file.write(f"Resultados da busca por: {product_name}\n")
            file.write("=" * 50 + "\n\n")
            file.write("MELHORES OFERTAS ENCONTRADAS:\n\n")
            
            if not melhores_produtos:
                file.write("Não foi possível identificar ofertas com preços.\n\n")
            else:
                for i, produto in enumerate(melhores_produtos, 1):
                    file.write(f"OFERTA {i}:\n")
                    file.write(f"Produto: {produto['nome']}\n")
                    file.write(f"Preço: {produto['preco']}\n")
                    if produto['loja']:
                        file.write(f"Loja: {produto['loja']}\n")
                    file.write("\n" + "-" * 40 + "\n\n")
            
            #add resultados no txt
            file.write("\nPRODUTOS ENCONTRADOS (dados brutos e sem tratamento q foram retirados da busca):\n")
            file.write("-" * 50 + "\n\n")
            
            for i, result in enumerate(results, 1):
                file.write(f"Item {i}:\n{result}\n\n")
                file.write("-" * 30 + "\n")
        
        return filename
    
    def close(self):
        if self.driver:
            self.driver.quit()


def main():
    product_name = input("informe o produto: ")
    
    if not product_name.strip():
        print("nome do porduto n pode ser vazio.")
        return
    
    # começa o scraper
    scraper = GoogleShoppingScraper()
    
    try:
        print(f"Produto buscadoo: {product_name}")
        results = scraper.search_product(product_name)
        
        if results:
            filename = scraper.save_to_file(product_name, results)
            print(f"Resultado salvo em: {filename}")
        else:
            print("Nada encontrado.")
    finally:
        scraper.close()


if __name__ == "__main__":
    main()