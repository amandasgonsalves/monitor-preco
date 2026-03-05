#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import time
import subprocess
import os
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
import random

# Importa undetected-chromedriver para contornar CAPTCHA
try:
    import undetected_chromedriver as uc
    UC_DISPONIVEL = True
    print("✅ undetected-chromedriver disponível")
except ImportError:
    UC_DISPONIVEL = False
    print("⚠️ undetected-chromedriver não disponível, usando selenium padrão")
    from selenium import webdriver
    from webdriver_manager.chrome import ChromeDriverManager

# User-agents reais e atualizados para rotação
USER_AGENTS = [
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64; rv:132.0) Gecko/20100101 Firefox/132.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:132.0) Gecko/20100101 Firefox/132.0",
]

def obter_user_agent():
    """Retorna um User-Agent aleatório para rotação"""
    return random.choice(USER_AGENTS)

def configurar_driver():
    """Configura e retorna o driver do Chrome com proteção anti-CAPTCHA usando undetected-chromedriver"""
    
    user_agent = obter_user_agent()
    
    if UC_DISPONIVEL:
        # ========== MÉTODO PRINCIPAL: undetected-chromedriver ==========
        # Este método é o mais eficaz contra CAPTCHA pois:
        # - Remove automaticamente flags de automação do Chrome
        # - Modifica o binário do ChromeDriver para evitar detecção
        # - Contorna o CDP (Chrome DevTools Protocol) fingerprinting
        try:
            print(" 🛡️ Configurando Chrome com undetected-chromedriver (anti-CAPTCHA)...")
            
            chrome_options = uc.ChromeOptions()
            
            # Modo headless (usa a versão nova que é menos detectável)
            chrome_options.add_argument("--headless=new")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument(f"--user-agent={user_agent}")
            
            # Configurações de janela realistas
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument("--start-maximized")
            
            # Desabilita features que denunciam automação
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_argument("--disable-features=VizDisplayCompositor")
            chrome_options.add_argument("--disable-background-timer-throttling")
            chrome_options.add_argument("--disable-backgrounding-occluded-windows")
            chrome_options.add_argument("--disable-renderer-backgrounding")
            
            # Idioma e localização para parecer brasileiro
            chrome_options.add_argument("--lang=pt-BR")
            chrome_options.add_argument("--accept-lang=pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7")
            
            # Cria o driver com undetected-chromedriver
            driver = uc.Chrome(
                options=chrome_options,
                use_subprocess=True,
                version_main=None,  # Detecta automaticamente a versão do Chrome
            )
            
            # Scripts adicionais para mascarar fingerprint
            _aplicar_stealth_scripts(driver)
            
            print(" ✅ Chrome anti-CAPTCHA configurado com sucesso!")
            return driver
            
        except Exception as e:
            print(f"⚠️ Erro com undetected-chromedriver: {e}")
            print(" Tentando método alternativo...")
    
    # ========== MÉTODO FALLBACK: Selenium padrão com stealth ==========
    try:
        print(" Configurando Chrome padrão com proteções anti-detecção...")
        chrome_options = Options()
        
        chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_argument(f"--user-agent={user_agent}")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--lang=pt-BR")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-background-timer-throttling")
        chrome_options.add_argument("--disable-backgrounding-occluded-windows")
        chrome_options.add_argument("--disable-renderer-backgrounding")
        
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        # Aplica stealth scripts
        _aplicar_stealth_scripts(driver)
        
        return driver
    except Exception as e:
        print(f"Erro na configuração: {e}")
    
    return None

def _aplicar_stealth_scripts(driver):
    """Aplica scripts JavaScript para mascarar fingerprints de automação"""
    stealth_scripts = [
        # Remove a propriedade webdriver do navigator
        "Object.defineProperty(navigator, 'webdriver', {get: () => undefined});",
        
        # Simula plugins reais do Chrome
        """
        Object.defineProperty(navigator, 'plugins', {
            get: () => [
                { name: 'Chrome PDF Plugin', filename: 'internal-pdf-viewer' },
                { name: 'Chrome PDF Viewer', filename: 'mhjfbmdgcfjbbpaeojofohoefgiehjai' },
                { name: 'Native Client', filename: 'internal-nacl-plugin' }
            ]
        });
        """,
        
        # Simula idiomas reais
        """
        Object.defineProperty(navigator, 'languages', {
            get: () => ['pt-BR', 'pt', 'en-US', 'en']
        });
        """,
        
        # Mascara o Chrome DevTools Protocol
        """
        const originalQuery = window.navigator.permissions.query;
        window.navigator.permissions.query = (parameters) => (
            parameters.name === 'notifications' ?
                Promise.resolve({ state: Notification.permission }) :
                originalQuery(parameters)
        );
        """,
        
        # Simula WebGL vendor/renderer reais
        """
        const getParameter = WebGLRenderingContext.prototype.getParameter;
        WebGLRenderingContext.prototype.getParameter = function(parameter) {
            if (parameter === 37445) return 'Intel Inc.';
            if (parameter === 37446) return 'Intel Iris OpenGL Engine';
            return getParameter.apply(this, arguments);
        };
        """,
        
        # Remove chrome.runtime (sinaliza extensões de automação)
        """
        window.chrome = {
            runtime: {},
            loadTimes: function() {},
            csi: function() {},
            app: {}
        };
        """,
        
        # Define platform consistente
        "Object.defineProperty(navigator, 'platform', {get: () => 'Linux x86_64'});",
        
        # Simula hardware concurrency real
        "Object.defineProperty(navigator, 'hardwareConcurrency', {get: () => 8});",
        
        # Simula deviceMemory real
        "Object.defineProperty(navigator, 'deviceMemory', {get: () => 8});",
    ]
    
    for script in stealth_scripts:
        try:
            driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {"source": script})
        except Exception:
            try:
                driver.execute_script(script)
            except Exception:
                pass

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

def digitar_como_humano(campo, texto):
    """Digita texto caractere por caractere com delays aleatórios, simulando digitação humana"""
    for char in texto:
        campo.send_keys(char)
        time.sleep(random.uniform(0.05, 0.20))  # Delay entre 50ms e 200ms por tecla
    time.sleep(random.uniform(0.3, 0.8))

def detectar_captcha(driver):
    """Detecta se a página está exibindo um CAPTCHA"""
    indicadores_captcha = [
        "//iframe[contains(@src, 'recaptcha')]",
        "//iframe[contains(@src, 'captcha')]",
        "//div[contains(@id, 'captcha')]",
        "//form[@id='captcha-form']",
        "//div[contains(@class, 'captcha')]",
        "//div[contains(@class, 'g-recaptcha')]",
    ]
    
    for xpath in indicadores_captcha:
        try:
            elementos = driver.find_elements(By.XPATH, xpath)
            if elementos:
                print("🚨 CAPTCHA detectado na página!")
                return True
        except:
            continue
    
    # Verifica pelo texto da página
    try:
        page_source = driver.page_source.lower()
        captcha_texts = [
            'unusual traffic',
            'tráfego incomum',
            'não sou um robô',
            'i\'m not a robot',
            'verificação de segurança',
            'automated queries',
            'consultas automatizadas',
            'sistemas detectaram tráfego incomum',
        ]
        for text in captcha_texts:
            if text in page_source:
                print(f"🚨 CAPTCHA detectado! Texto encontrado: '{text}'")
                return True
    except:
        pass
    
    return False

def espera_aleatoria(min_seg=2, max_seg=5):
    """Faz uma pausa aleatória para simular comportamento humano"""
    tempo = random.uniform(min_seg, max_seg)
    time.sleep(tempo)

def buscar_produtos_patrocinados(produto, max_tentativas=3):
    """
    Busca produto no Google Shopping com sistema de retry (3 tentativas)
    Inclui proteção anti-CAPTCHA com delays aleatórios e rotação de User-Agent
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
            
            # Delay aleatório entre tentativas para parecer humano
            if tentativa > 0:
                delay = random.uniform(8, 15)
                print(f" ⏳ Aguardando {delay:.1f}s antes da nova tentativa...")
                time.sleep(delay)
            
            # Primeiro acessa o Google normal para pegar cookies (reduz chance de CAPTCHA)
            print(f" 🌐 Acessando Google para estabelecer sessão...")
            driver.get("https://www.google.com.br")
            espera_aleatoria(2, 4)
            
            # Verifica CAPTCHA já na página inicial
            if detectar_captcha(driver):
                print("🚨 CAPTCHA na página inicial! Trocando User-Agent e tentando novamente...")
                driver.quit()
                driver = None
                time.sleep(random.uniform(10, 20))
                continue
            
            # Agora navega para o Google Shopping
            print(f" 🛒 Acessando Google Shopping...")
            driver.get("https://www.google.com/shopping?hl=pt-BR")
            espera_aleatoria(3, 6)
            
            # Verifica CAPTCHA na página do Shopping
            if detectar_captcha(driver):
                print("🚨 CAPTCHA detectado no Google Shopping! Tentando contornar...")
                driver.quit()
                driver = None
                time.sleep(random.uniform(15, 30))
                continue

            # Aguarda a página carregar com timeout maior
            wait = WebDriverWait(driver, 22)  # Reduzido de 20 para 15 segundos

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

                # Digitar como humano (caractere por caractere com delays aleatórios)
                digitar_como_humano(campo_busca, produto)
                espera_aleatoria(0.5, 1.5)
                campo_busca.send_keys(Keys.ENTER)
            except Exception as e:
                raise Exception(f"Erro ao interagir com o campo de busca: {e}")

            print(" Aguardando resultados carregarem...")
            espera_aleatoria(4, 7)
            
            # Verifica CAPTCHA nos resultados
            if detectar_captcha(driver):
                print("🚨 CAPTCHA detectado nos resultados! Tentando novamente...")
                raise Exception("CAPTCHA detectado")

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
        # Lista de nomes de lojas conhecidas para filtrar (não confundir com nome do produto)
        lojas_conhecidas = [
            'lojas mm', 'magazine luiza', 'magalu', 'casas bahia', 'amazon', 'amazon.com.br',
            'mercado livre', 'mercadolivre', 'madeiramadeira', 'madeira madeira',
            'kabum', 'pichau', 'colombo', 'lojas colombo', 'multiloja', 'shopee',
            'americanas', 'submarino', 'ponto frio', 'extra', 'carrefour',
            'loja veneza', 'valdar móveis', 'valdar moveis', 'zoom', 'buscape',
            'shoptime', 'girafa', 'fast shop', 'fastshop', 'pontofrio',
            'walmart', 'ali express', 'aliexpress', 'wish', 'shein',
        ]

        seletores_nome = [
            ".bXPcId",          # Classe do nome do produto dentro de pla-unit
            ".rgHvZc",          # Outra classe comum para nome de produto
            ".EI11Pd",          # Nome do produto em cards do Shopping
            "span.pymv4e",     # Classe específica para nome de produto
            "span[class*='pymv4e']",
            ".pymv4e",
            ".sh-np__product-title",  # Título do produto no Shopping
            "h3",
            "h4",
            ".PLla-d",
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
                            texto_limpo = texto.strip()
                            texto_lower = texto_limpo.lower()
                            
                            # Filtra textos que claramente não são nomes de produto
                            filtros_invalidos = [
                                'custava', 'reais', 'ver mais', 'comprar', 'classificado como',
                                'estrelas', 'avaliação', 'nota', 'rating', 'review',
                                'de 5', 'promoção', 'desconto', 'frete',
                            ]
                            
                            # Verifica se o texto é nome de loja (e não nome do produto)
                            eh_loja = any(loja in texto_lower for loja in lojas_conhecidas)
                            
                            if not any(filtro in texto_lower for filtro in filtros_invalidos) and not eh_loja:
                                produto_info["nome"] = texto_limpo
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
                    // Lista de nomes de lojas para ignorar
                    const lojas = ['lojas mm', 'magazine luiza', 'magalu', 'casas bahia', 
                        'amazon', 'amazon.com.br', 'mercado livre', 'mercadolivre',
                        'madeiramadeira', 'madeira madeira', 'kabum', 'pichau', 
                        'colombo', 'lojas colombo', 'multiloja', 'shopee',
                        'americanas', 'submarino', 'ponto frio', 'extra', 'carrefour',
                        'loja veneza', 'valdar móveis', 'valdar moveis', 'fast shop',
                        'fastshop', 'pontofrio', 'shoptime', 'girafa', 'zoom', 'buscape'];
                    
                    function ehLoja(text) {
                        const lower = text.toLowerCase().trim();
                        return lojas.some(l => lower === l || lower.includes(l));
                    }
                    
                    // 1. Procura pela classe bXPcId (nome do produto no card PLA)
                    let nameEl = element.querySelector('.bXPcId');
                    if (nameEl) {
                        const t = (nameEl.textContent || '').trim();
                        if (t.length > 5 && !ehLoja(t)) return t;
                    }
                    
                    // 2. Procura pela classe rgHvZc
                    nameEl = element.querySelector('.rgHvZc');
                    if (nameEl) {
                        const t = (nameEl.textContent || '').trim();
                        if (t.length > 5 && !ehLoja(t)) return t;
                    }
                    
                    // 3. Procura pela classe EI11Pd
                    nameEl = element.querySelector('.EI11Pd');
                    if (nameEl) {
                        const t = (nameEl.textContent || '').trim();
                        if (t.length > 5 && !ehLoja(t)) return t;
                    }
                    
                    // 4. Procura pela classe pymv4e
                    nameEl = element.querySelector('span.pymv4e');
                    if (nameEl) {
                        const t = (nameEl.textContent || '').trim();
                        if (t.length > 5 && !ehLoja(t)) return t;
                    }
                    
                    // 5. Procura pelo título do produto via aria-label do link
                    const links = element.querySelectorAll('a[aria-label]');
                    for (let link of links) {
                        const label = link.getAttribute('aria-label') || '';
                        if (label.length > 10 && !label.includes('R$') && !ehLoja(label)) {
                            return label.trim();
                        }
                    }
                    
                    // 6. Fallback: procura por spans com texto longo que não seja loja
                    const spans = element.querySelectorAll('span, div');
                    for (let span of spans) {
                        // Pega apenas o texto direto, não de filhos
                        let text = '';
                        for (let node of span.childNodes) {
                            if (node.nodeType === 3) text += node.textContent;
                        }
                        text = text.trim();
                        if (text.length > 15 && 
                            !text.includes('R$') && 
                            !text.includes('Custava') &&
                            !text.includes('Classificado') &&
                            !text.includes('estrelas') &&
                            !ehLoja(text)) {
                            return text;
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
                    
                    # Procura a primeira linha que parece ser um nome de produto (não loja)
                    for linha in linhas:
                        linha_lower = linha.lower()
                        eh_loja = any(loja in linha_lower for loja in lojas_conhecidas)
                        if (len(linha) > 8 and 
                            not linha.startswith('R$') and 
                            'custava' not in linha_lower and
                            'reais' not in linha_lower and
                            not linha.isdigit() and
                            not eh_loja):
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
        
        # Extração da loja - primeiro tenta seletores específicos do Google Shopping
        seletores_loja = [
            ".aULzUe",          # Classe comum para nome da loja no Google Shopping
            ".LbUacb",          # Outra classe para loja
            ".E5ocAb",          # Nome do merchant
            ".zPEcBd",          # Nome da loja em cards PLA
            ".IuHnof",          # Loja em resultados de shopping
        ]
        
        for seletor in seletores_loja:
            try:
                elem_loja = elemento.find_element(By.CSS_SELECTOR, seletor)
                texto_loja = (elem_loja.text or elem_loja.get_attribute("textContent") or "").strip()
                if texto_loja and len(texto_loja) > 1:
                    produto_info["loja"] = texto_loja
                    break
            except:
                continue
        
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
                
                # Extrai loja do domínio (apenas se não encontrou por seletores)
                if link and not produto_info["loja"]:
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
    """Configura o navegador - usa a mesma configuração anti-CAPTCHA do configurar_driver"""
    return configurar_driver()

def buscar_produto(produto):
    """Realiza a busca de um produto no Google Shopping.
    Redireciona para buscar_produtos_patrocinados que já tem proteção anti-CAPTCHA."""
    return buscar_produtos_patrocinados(produto)

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

        MAX_TENTATIVAS_MASSA = 3

        # Estrutura para controlar tentativas: {produto: tentativa_atual}
        fila_produtos = {produto: 0 for produto in produtos_para_buscar}
        produtos_concluidos = set()

        # Sistema de tentativas intercaladas para busca em massa
        for rodada in range(1, MAX_TENTATIVAS_MASSA + 1):
            produtos_para_tentar = [p for p, t in fila_produtos.items() if t < rodada and p not in produtos_concluidos]
            
            if not produtos_para_tentar:
                break

            print(f"\n{'='*60}")
            print(f"📋 RODADA {rodada} DE {MAX_TENTATIVAS_MASSA} - {len(produtos_para_tentar)} produto(s) para buscar")
            print(f"{'='*60}")

            for produto in produtos_para_tentar:
                fila_produtos[produto] = rodada
                print(f"\n🔄 Tentativa {rodada}/{MAX_TENTATIVAS_MASSA} para: '{produto}'")
                
                resultado = main(produto_busca=produto, batch_id=batch_id)
                
                # Verifica se a busca retornou produtos
                if resultado and len(resultado.get("produtos_patrocinados", [])) > 0:
                    produtos_concluidos.add(produto)
                    print(f"✅ Busca concluída com sucesso para: '{produto}'")
                else:
                    if rodada < MAX_TENTATIVAS_MASSA:
                        print(f"⚠️ Nenhum produto encontrado para: '{produto}' - será tentado novamente na próxima rodada")
                        time.sleep(3)  # Pausa antes de tentar o próximo
                    else:
                        print(f"❌ Todas as {MAX_TENTATIVAS_MASSA} tentativas falharam para: '{produto}'")

        # Resumo final
        produtos_falhados = [p for p in produtos_para_buscar if p not in produtos_concluidos]
        print(f"\n{'='*60}")
        print(f"📊 RESUMO DA BUSCA EM MASSA")
        print(f"{'='*60}")
        print(f"Total de produtos: {len(produtos_para_buscar)}")
        print(f"Concluídos com sucesso: {len(produtos_concluidos)}")
        print(f"Sem resultados após {MAX_TENTATIVAS_MASSA} tentativas: {len(produtos_falhados)}")
        if produtos_falhados:
            print(f"Produtos sem resultado: {', '.join(produtos_falhados)}")

        # Remover arquivo temporário após processamento
        if os.path.exists('produtos_temp.txt'):
            try:
                os.remove('produtos_temp.txt')
            except Exception as e:
                print(f"Erro ao remover o arquivo temporário: {e}")

    except Exception as e:
        print(f"Erro ao executar buscas: {e}")
        exit(1)