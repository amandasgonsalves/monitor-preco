#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import time
import subprocess
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
import random

def configurar_driver():
    """Configura e retorna o driver do Chrome com opções otimizadas - MODO HEADLESS"""
    chrome_options = Options()

    # CONFIGURAÇÕES PARA MODO HEADLESS
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")  # Desabilita GPU (importante para headless)
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

    # Configurações adicionais para estabilidade
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-web-security")
    chrome_options.add_argument("--allow-running-insecure-content")
    chrome_options.add_argument("--disable-features=VizDisplayCompositor")
    chrome_options.add_argument("--disable-logging")
    chrome_options.add_argument("--silent")
    chrome_options.add_argument("--window-size=1920,1080")  # Define tamanho mesmo invisível
    chrome_options.add_argument("--disable-background-timer-throttling")
    chrome_options.add_argument("--disable-backgrounding-occluded-windows")
    chrome_options.add_argument("--disable-renderer-backgrounding")

    # Método 1: Usar WebDriver Manager (recomendado para compatibilidade)
    try:
        print(" Configurando Chrome headless com WebDriver Manager...")
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        return driver
    except Exception as e:
        print(f"Erro com WebDriver Manager: {e}")

    # Método 2: Usar método direto do Chrome (Windows)
    try:
        print(" Última tentativa - Chrome headless com configurações específicas...")
        driver = webdriver.Chrome(options=chrome_options)
        return driver
    except Exception as e:
        print(f"Erro na configuração headless: {e}")

    return None

def simular_movimentos_mouse(driver, elemento):
    """Simula movimentos do mouse para um elemento."""
    try:
        acao = ActionChains(driver)
        acao.move_to_element(elemento).perform()
        time.sleep(random.uniform(0.5, 1.5))  # Atraso aleatório
    except Exception as e:
        print(f"Erro ao simular movimento do mouse: {e}")

def rolar_tela(driver):
    """Rola a tela para cima e para baixo para simular comportamento humano."""
    try:
        print("Rolando a tela para baixo...")
        driver.execute_script("window.scrollBy(0, 500);")
        time.sleep(random.uniform(1, 2))
        print("Rolando a tela para cima...")
        driver.execute_script("window.scrollBy(0, -500);")
        time.sleep(random.uniform(1, 2))
    except Exception as e:
        print(f"Erro ao rolar a tela: {e}")

def buscar_produtos_patrocinados(produto, max_tentativas=2):
    """
    Busca produto no Google Shopping com sistema de retry
    """
    for tentativa in range(max_tentativas):
        driver = None
        try:
            print(f" Tentativa {tentativa + 1} de {max_tentativas}")
            driver = configurar_driver()
            
            resultados = {
                "produto_buscado": produto,
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "produtos_patrocinados": []
            }
            
            print(f" Acessando Google Shopping...")
            driver.get("https://www.google.com/shopping?hl=pt-BR")

            # Aguarda a página carregar com timeout maior
            wait = WebDriverWait(driver, 15)  # Reduzido de 20 para 15 segundos

            # Rola a tela para cima e para baixo antes de interagir com a busca
            rolar_tela(driver)

            print(f" Procurando campo de busca...")
            # Tenta diferentes seletores para o campo de busca
            campo_busca = None
            seletores_busca = [
                "textarea.gLFyf",  # Atualizado para usar o seletor mais confiável primeiro
                "#APjFqb", 
                "input[name='q']", 
                "input[type='search]"
            ]

            for seletor in seletores_busca:
                try:
                    campo_busca = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, seletor)))
                    simular_movimentos_mouse(driver, campo_busca)  # Simula movimento do mouse
                    break
                except TimeoutException:
                    print(f" Seletor {seletor} não funcionou, tentando próximo...")
                    continue

            if not campo_busca:
                raise Exception("Campo de busca não encontrado")

            # Garantir que o seletor correto seja clicado e o nome do produto seja digitado
            try:
                simular_movimentos_mouse(driver, campo_busca)  # Simula movimento do mouse
                campo_busca.click()
                print("Campo de busca clicado com sucesso.")

                print(f"Digitando: {produto}")
                campo_busca.clear()

                # Digitar o produto diretamente sem atrasos excessivos
                campo_busca.send_keys(produto)
                time.sleep(1)  # Reduzido o tempo de espera
                campo_busca.send_keys(Keys.ENTER)
            except Exception as e:
                raise Exception(f"Erro ao interagir com o campo de busca: {e}")

            print(" Aguardando resultados carregarem...")
            time.sleep(5)  # Reduzido o tempo de espera para resultados

            print(" Procurando produtos patrocinados...")

            # Simula rolagem na página
            for _ in range(3):
                driver.execute_script("window.scrollBy(0, 300);")
                time.sleep(random.uniform(1, 2))

            # Tenta diferentes padrões de produtos
            produtos_encontrados = []
            seletores_produtos = [
                "[id^='vplahcl_']",
                "[data-docid][jscontroller]", 
                ".sh-dgr__content",
                ".PLla-d",
                "[role='listitem']"
            ]

            for seletor in seletores_produtos:
                elementos = driver.find_elements(By.CSS_SELECTOR, seletor)
                if elementos:
                    produtos_encontrados = elementos
                    print(f" Encontrados {len(elementos)} elementos com seletor: {seletor}")
                    break

            if not produtos_encontrados:
                print(" Nenhum produto encontrado, tentando busca mais ampla...")
                produtos_encontrados = driver.find_elements(By.CSS_SELECTOR, "div[data-hveid], div[data-ved]")

            print(f" Processando {len(produtos_encontrados)} elementos...")

            for i, produto_elem in enumerate(produtos_encontrados[:20]):
                try:
                    simular_movimentos_mouse(driver, produto_elem)  # Simula movimento do mouse
                    produto_info = extrair_info_produto_melhorado(produto_elem, driver, i)
                    if produto_info and any(produto_info.values()):
                        resultados["produtos_patrocinados"].append(produto_info)
                        print(f"✅ Produto {i+1}: {produto_info.get('nome', 'N/A')[:50]}...")
                except Exception as e:
                    continue

            return resultados
            
        except Exception as e:
            print(f" Erro na tentativa {tentativa + 1}: {e}")
            if tentativa < max_tentativas - 1:
                print(" Tentando novamente em 5 segundos...")
                time.sleep(5)
        finally:
            if driver:
                try:
                    driver.quit()
                except:
                    pass
    
    # Se chegou aqui, todas as tentativas falharam
    return {
        "produto_buscado": produto,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "produtos_patrocinados": []
    }

def extrair_info_produto_melhorado(elemento, driver, index):
    """Versão melhorada da extração com mais fallbacks e debug"""
    produto_info = {
        "nome": None,
        "preco": None,
        "loja": None,
        "link": None
    }
    
    try:
        # Debug: imprimir o HTML do elemento para análise
        if index < 3:  # Só para os primeiros elementos para não poluir
            try:
                html_snippet = elemento.get_attribute('outerHTML')[:500]
                print(f"DEBUG - Elemento {index+1} HTML: {html_snippet}...")
            except:
                pass
        
        # Extração do nome - baseado na estrutura real do Google Shopping
        seletores_nome = [
            "span.pymv4e",  # Classe específica vista na imagem
            "span[class*='pymv4e']",
            ".pymv4e",
            "h3", "h4", "h2",
            "[aria-label]",
            "[title]",
            ".sh-np__product-title",
            ".PLla-d",
            "a[href] span",
            "a[href] div",
            "span[role='link']",
            "*[class*='title']",
            "*[class*='name']",
            "*[class*='product']"
        ]
        
        for seletor in seletores_nome:
            try:
                elementos_nome = elemento.find_elements(By.CSS_SELECTOR, seletor)
                for elem in elementos_nome:
                    # Tenta diferentes métodos para extrair o texto
                    textos_possiveis = [
                        elem.text.strip(),
                        elem.get_attribute("textContent"),
                        elem.get_attribute("innerText"),
                        elem.get_attribute("title"),
                        elem.get_attribute("aria-label")
                    ]
                    
                    for texto in textos_possiveis:
                        if texto and len(texto) > 5 and not texto.startswith('R$'):
                            # Filtra textos que claramente não são nomes de produto
                            texto_lower = texto.lower()
                            filtros_invalidos = [
                                'custava', 'reais', 'ver mais', 'comprar', 'classificado como',
                                'estrelas', 'avaliação', 'nota', 'rating', 'review',
                                'de 5', 'promoção', 'desconto', 'frete', 'de amazon',
                                'de mercadolivre', 'de pichau', 'de kabum'
                            ]
                            
                            if not any(filtro in texto_lower for filtro in filtros_invalidos):
                                produto_info["nome"] = texto
                                break
                    
                    if produto_info["nome"]:
                        break
                
                if produto_info["nome"]:
                    break
            except:
                continue
        
        # Extração via JavaScript para casos difíceis
        if not produto_info["nome"]:
            try:
                js_script = """
                function findProductName(element) {
                    // Procura especificamente pela classe pymv4e
                    let nameElement = element.querySelector('span.pymv4e');
                    if (nameElement && nameElement.textContent) {
                        return nameElement.textContent.trim();
                    }
                    
                    // Fallback: procura por spans com texto relevante
                    const spans = element.querySelectorAll('span');
                    for (let span of spans) {
                        const text = span.textContent || span.innerText || '';
                        if (text.length > 10 && 
                            !text.includes('R$') && 
                            !text.includes('Custava') &&
                            !text.includes('De ') &&
                            !text.includes('Classificado') &&
                            !text.includes('estrelas')) {
                            return text.trim();
                        }
                    }
                    
                    return null;
                }
                return findProductName(arguments[0]);
                """
                
                nome_js = driver.execute_script(js_script, elemento)
                if nome_js and len(nome_js) > 5:
                    produto_info["nome"] = nome_js
            except:
                pass
        
        # Se não encontrou nome pelos seletores, analisa todo o texto do elemento
        if not produto_info["nome"]:
            try:
                texto_completo = elemento.text.strip()
                if texto_completo:
                    linhas = [linha.strip() for linha in texto_completo.split('\n') if linha.strip()]
                    
                    # Procura a primeira linha que parece ser um nome de produto
                    for linha in linhas:
                        if (len(linha) > 8 and 
                            not linha.startswith('R$') and 
                            'custava' not in linha.lower() and
                            'reais' not in linha.lower() and
                            not linha.isdigit()):
                            produto_info["nome"] = linha
                            break
            except:
                pass
        
        # Extração do preço - versão melhorada baseado na estrutura real
        if not produto_info["preco"]:
            # Força o carregamento de conteúdo dinâmico
            try:
                driver.execute_script("arguments[0].scrollIntoView(true);", elemento)
                time.sleep(0.5)
            except:
                pass
            
            # Seletores específicos para preços no Google Shopping
            seletores_preco_especificos = [
                "div[class*='qptdjc']",  # Classe comum para preços
                "span[class*='qptdjc']",
                ".qptdjc",
                "div[style*='webkit-line-clamp']",  # Preços com truncamento
                "[class*='13vB']",  # Padrão de classe para preços
                "[class*='RRDx']",  # Outro padrão comum
                "[class*='hdYIY']",  # Classe encontrada no debug
                "div[data-offer-id] span",
                "div[data-offer-id] div"
            ]
            
            for seletor in seletores_preco_especificos:
                try:
                    elementos_preco = elemento.find_elements(By.CSS_SELECTOR, seletor)
                    for elem_preco in elementos_preco:
                        # Tenta diferentes atributos e propriedades
                        textos_possiveis = [
                            elem_preco.text.strip(),
                            elem_preco.get_attribute("textContent"),
                            elem_preco.get_attribute("innerText"),
                            elem_preco.get_attribute("aria-label"),
                            elem_preco.get_attribute("title")
                        ]
                        
                        for texto_preco in textos_possiveis:
                            if texto_preco and 'R$' in texto_preco:
                                import re
                                # Limpa e valida o preço
                                match = re.search(r'R\$\s*[\d,.]+', texto_preco)
                                if match:
                                    produto_info["preco"] = match.group(0)
                                    break
                        
                        if produto_info["preco"]:
                            break
                    
                    if produto_info["preco"]:
                        break
                except:
                    continue
        
        # Extração via JavaScript como alternativa
        if not produto_info["preco"]:
            try:
                # Usa JavaScript para procurar preços no elemento
                js_script = r"""
                function findPriceInElement(element) {
                    // Procura por elementos que contêm R$
                    const allElements = element.querySelectorAll('*');
                    for (let el of allElements) {
                        const text = el.textContent || el.innerText || '';
                        if (text.includes('R$') && text.match(/R\$\s*[\d,.]+/)) {
                            return text.match(/R\$\s*[\d,.]+/)[0];
                        }
                    }
                    return null;
                }
                return findPriceInElement(arguments[0]);
                """
                
                preco_js = driver.execute_script(js_script, elemento)
                if preco_js:
                    produto_info["preco"] = preco_js.strip()
            except:
                pass
        
        # Debug adicional para preços (apenas primeiros elementos)
        if index < 3:
            try:
                # Mostra todos os elementos que contêm R$ para debug
                elementos_com_rs = elemento.find_elements(By.XPATH, ".//*[contains(text(), 'R$')]")
                if elementos_com_rs:
                    print(f"DEBUG - Elementos com R$ encontrados no produto {index+1}:")
                    for i, elem in enumerate(elementos_com_rs[:3]):  # Mostra apenas os 3 primeiros
                        try:
                            texto = elem.text.strip()
                            classe = elem.get_attribute("class")
                            print(f"  - Elemento {i+1}: '{texto}' (classe: {classe})")
                        except:
                            pass
            except:
                pass
        
        # Extração da loja do link se não encontrou por seletores
        try:
            # Primeiro tenta encontrar um link
            link_elem = None
            if elemento.tag_name == "a":
                link_elem = elemento
            else:
                link_elem = elemento.find_element(By.CSS_SELECTOR, "a[href]")
            
            if link_elem:
                link = link_elem.get_attribute("href")
                produto_info["link"] = link
                
                # Extrai loja do domínio
                if link:
                    import re
                    match = re.search(r'https?://(?:www\.)?([^/]+)', link)
                    if match:
                        dominio = match.group(1)
                        if 'amazon' in dominio:
                            produto_info["loja"] = "Amazon"
                        elif 'mercadolivre' in dominio:
                            produto_info["loja"] = "Mercado Livre"
                        elif 'pichau' in dominio:
                            produto_info["loja"] = "Pichau"
                        elif 'kabum' in dominio:
                            produto_info["loja"] = "KaBuM!"
                        else:
                            # Pega o nome principal do domínio
                            nome_loja = dominio.split('.')[0].replace('www', '').strip()
                            if nome_loja:
                                produto_info["loja"] = nome_loja.capitalize()
        except:
            pass
        
        # Se ainda não tem nome, tenta extrair do link
        if not produto_info["nome"] and produto_info["link"]:
            try:
                from urllib.parse import unquote
                link = unquote(produto_info["link"])
                
                # Tenta extrair nome do produto da URL
                import re
                patterns = [
                    r'/([^/]+?)(?:-\d+|/dp/|/p/)',  # Amazon e Mercado Livre
                    r'/([^/]+?)(?:\?|$)',           # Genérico
                ]
                
                for pattern in patterns:
                    match = re.search(pattern, link)
                    if match:
                        nome_url = match.group(1)
                        # Limpa e formata o nome
                        nome_url = nome_url.replace('-', ' ').replace('_', ' ')
                        nome_url = re.sub(r'%[0-9A-F]{2}', ' ', nome_url)  # Remove códigos URL
                        nome_url = ' '.join(nome_url.split())  # Remove espaços extras
                        
                        if len(nome_url) > 5:
                            produto_info["nome"] = nome_url
                            break
            except:
                pass
        
        return produto_info
        
    except Exception as e:
        print(f"Erro ao processar elemento {index}: {e}")
        return produto_info

def extrair_produtos_generico(driver):
    """Abordagem genérica para extrair produtos quando os seletores específicos falham"""
    produtos = []
    
    try:
        seletores_produtos = [
            ".sh-dgr__content",
            "[data-docid]",
            ".PLla-d",
            ".sh-dlr__list-result"
        ]
        
        for seletor in seletores_produtos:
            elementos = driver.find_elements(By.CSS_SELECTOR, seletor)
            if elementos:
                print(f"Encontrados {len(elementos)} produtos com seletor: {seletor}")
                
                for i, elem in enumerate(elementos[:10]):
                    try:
                        produto = {
                            "nome": None,
                            "preco": None,
                            "loja": None,
                            "link": None
                        }
                        
                        # Tenta extrair nome
                        try:
                            nome = elem.find_element(By.CSS_SELECTOR, "h3, [role='link'], .sh-dlr__list-result-title")
                            produto["nome"] = nome.text.strip()
                        except:
                            pass
                        
                        # Tenta extrair preço
                        try:
                            preco = elem.find_element(By.CSS_SELECTOR, "[aria-label*='R$'], .a-price, .sh-dlr__list-result-price")
                            produto["preco"] = preco.text.strip() or preco.get_attribute("aria-label")
                        except:
                            pass
                        
                        # Tenta extrair loja
                        try:
                            loja = elem.find_element(By.CSS_SELECTOR, ".sh-dlr__list-result-merchant, [data-test-id='merchant-name']")
                            produto["loja"] = loja.text.strip()
                        except:
                            pass
                        
                        # Tenta extrair link
                        try:
                            link = elem.find_element(By.CSS_SELECTOR, "a[href]")
                            produto["link"] = link.get_attribute("href")
                        except:
                            pass
                        
                        if any(produto.values()):
                            produtos.append(produto)
                            
                    except Exception as e:
                        continue
                
                if produtos:
                    break
                    
    except Exception as e:
        print(f"Erro na extração genérica: {e}")
    
    return produtos

def salvar_resultados(resultados, nome_arquivo="resultados_google_shopping.json", batch_id=None):
    """Salva os resultados em um arquivo JSON na pasta 'resultados'"""
    try:
        # Cria a pasta 'resultados' se não existir
        pasta_resultados = "resultados"
        if not os.path.exists(pasta_resultados):
            os.makedirs(pasta_resultados)

        # Adiciona batch_id ao resultado para agrupar buscas em massa
        if batch_id:
            resultados["batch_id"] = batch_id

        # Define o caminho completo do arquivo
        caminho_arquivo = os.path.join(pasta_resultados, nome_arquivo)

        with open(caminho_arquivo, 'w', encoding='utf-8') as f:
            json.dump(resultados, f, indent=2, ensure_ascii=False)
        print(f"\nResultados salvos em: {caminho_arquivo}")
        return True
    except Exception as e:
        print(f"Erro ao salvar arquivo: {e}")
        return False

def exibir_resultados(resultados):
    """Exibe os resultados da busca de forma estruturada na tela."""
    print("\n" + "="*50)
    print("RESULTADOS DA BUSCA")
    print("="*50)
    print(f"Produto buscado: {resultados['produto_buscado']}")
    print(f"Timestamp: {resultados['timestamp']}")
    print(f"Produtos encontrados: {len(resultados['produtos_patrocinados'])}")

    if resultados['produtos_patrocinados']:
        print("\n" + "="*50)
        print("PRODUTOS PATROCINADOS ENCONTRADOS")
        print("="*50)

        for i, produto in enumerate(resultados['produtos_patrocinados'], 1):
            print(f"\n[PRODUTO {i}]")
            print(f"Nome: {produto.get('nome', 'N/A')}")
            print(f"Preço: {produto.get('preco', 'N/A')}")
            print(f"Loja: {produto.get('loja', 'N/A')}")
            print(f"Link: {produto.get('link', 'N/A')}")
            print("-" * 40)
    else:
        print("\nNenhum produto patrocinado foi encontrado.")

def configurar_navegador():
    """Configura o navegador no modo headless."""
    options = Options()
    options.add_argument('--headless')  # Desativa a visualização do navegador
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    return options

def buscar_produto(produto):
    """Realiza a busca de um produto no Google Shopping."""
    options = configurar_navegador()
    driver = webdriver.Chrome(service=Service(), options=options)

    try:
        print(f" Buscando por: {produto}")
        driver.get("https://www.google.com.br/shopping")

        # Aguarda a página carregar com timeout maior
        wait = WebDriverWait(driver, 15)  # Aumentado para 15 segundos

        # Rola a tela para baixo para carregar mais resultados
        rolar_tela(driver)

        print(f" Procurando campo de busca...")
        # Tenta diferentes seletores para o campo de busca
        campo_busca = None
        seletores_busca = [
            "textarea.gLFyf",  # Atualizado para usar o seletor mais confiável primeiro
            "#APjFqb", 
            "input[name='q']", 
            "input[type='search]"
        ]

        for seletor in seletores_busca:
            try:
                campo_busca = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, seletor)))
                simular_movimentos_mouse(driver, campo_busca)  # Simula movimento do mouse
                break
            except TimeoutException:
                print(f" Seletor {seletor} não funcionou, tentando próximo...")
                continue

        if not campo_busca:
            raise Exception("Campo de busca não encontrado")

        # Garantir que o seletor correto seja clicado e o nome do produto seja digitado
        try:
            simular_movimentos_mouse(driver, campo_busca)  # Simula movimento do mouse
            campo_busca.click()
            print("Campo de busca clicado com sucesso.")

            print(f"Digitando: {produto}")
            campo_busca.clear()

            # Digitar o produto diretamente sem atrasos excessivos
            campo_busca.send_keys(produto)
            time.sleep(1)  # Reduzido o tempo de espera
            campo_busca.send_keys(Keys.ENTER)
        except Exception as e:
            raise Exception(f"Erro ao interagir com o campo de busca: {e}")

        print(" Aguardando resultados carregarem...")
        time.sleep(5)  # Reduzido o tempo de espera para resultados

        print(" Procurando produtos patrocinados...")

        # Simula rolagem na página
        for _ in range(3):
            driver.execute_script("window.scrollBy(0, 300);")
            time.sleep(random.uniform(1, 2))

        # Tenta diferentes padrões de produtos
        produtos_encontrados = []
        seletores_produtos = [
            "[id^='vplahcl_']",
            "[data-docid][jscontroller]", 
            ".sh-dgr__content",
            ".PLla-d",
            "[role='listitem']"
        ]

        for seletor in seletores_produtos:
            elementos = driver.find_elements(By.CSS_SELECTOR, seletor)
            if elementos:
                produtos_encontrados = elementos
                print(f" Encontrados {len(elementos)} elementos com seletor: {seletor}")
                break

        if not produtos_encontrados:
            print(" Nenhum produto encontrado, tentando busca mais ampla...")
            produtos_encontrados = driver.find_elements(By.CSS_SELECTOR, "div[data-hveid], div[data-ved]")

        print(f" Processando {len(produtos_encontrados)} elementos...")

        for i, produto_elem in enumerate(produtos_encontrados[:20]):
            try:
                simular_movimentos_mouse(driver, produto_elem)  # Simula movimento do mouse
                produto_info = extrair_info_produto_melhorado(produto_elem, driver, i)
                if produto_info and any(produto_info.values()):
                    resultados["produtos_patrocinados"].append(produto_info)
                    print(f"✅ Produto {i+1}: {produto_info.get('nome', 'N/A')[:50]}...")
            except Exception as e:
                continue

        return resultados
            
    except Exception as e:
        print(f" Erro na tentativa {tentativa + 1}: {e}")
        if tentativa < max_tentativas - 1:
            print(" Tentando novamente em 5 segundos...")
            time.sleep(5)
    finally:
        if driver:
            try:
                driver.quit()
            except:
                pass

def main(produto_busca, batch_id=None):
    """Função principal"""
    print("=== Buscador de Produtos Google Shopping (Área Patrocinados) ===\n")

    if not produto_busca:
        print("Erro: Você deve digitar um produto para buscar.")
        return

    print(f"\nIniciando busca por: '{produto_busca}'")
    print("Focando na área de produtos patrocinados...")
    print("Isso pode levar alguns segundos...\n")

    resultados = buscar_produtos_patrocinados(produto_busca)

    # Exibir os resultados na tela
    exibir_resultados(resultados)

    nome_arquivo = f"resultado_{produto_busca.replace(' ', '_').lower().replace('/', '_')}.json"
    if salvar_resultados(resultados, nome_arquivo, batch_id=batch_id):
        print(f"\n Busca concluída! Verifique o arquivo na pasta 'resultados' para todos os resultados.")

    return resultados

if __name__ == "__main__":
    # Verificar se o arquivo produtos_temp.txt existe e usá-lo para buscas
    try:
        # Carregar produtos do arquivo produtos_temp.txt
        produtos_para_buscar = []
        arquivo_produtos = 'produtos_temp.txt'

        if os.path.exists(arquivo_produtos):
            with open(arquivo_produtos, 'r', encoding='utf-8') as f:
                produtos_para_buscar = [linha.strip() for linha in f if linha.strip()]

            if not produtos_para_buscar:
                print("O arquivo produtos_temp.txt está vazio. Não é possível realizar a busca.")
                exit(1)
        else:
            print("O arquivo produtos_temp.txt não foi encontrado. Não é possível realizar a busca.")
            exit(1)

        print(f"Iniciando busca para {len(produtos_para_buscar)} produtos...")

        # Gera um batch_id único para agrupar todas as buscas em massa
        batch_id = time.strftime("%Y%m%d_%H%M%S")

        # Realizar busca para cada produto individualmente
        for produto in produtos_para_buscar:
            main(produto_busca=produto, batch_id=batch_id)

        # Remover arquivo temporário após processamento
        if os.path.exists('produtos_temp.txt'):
            try:
                os.remove('produtos_temp.txt')
            except Exception as e:
                print(f"Erro ao remover o arquivo temporário: {e}")

    except Exception as e:
        print(f"Erro ao executar buscas: {e}")
        exit(1)