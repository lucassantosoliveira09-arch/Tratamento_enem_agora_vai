"""
Propósito: recortar excessos inferiores que possam ter ficado nas imagens, usando a faixa como referência
Autor: Alexandre Nassar de Peder
Criação: 02/10/2025
Atualização: 03/06/2026

OBS1: puxe a pasta "questoes" do passo 10 para este passo 11

OBS2: este código vai criar uma pasta de saída chamada "finalizadas", vai percorrer o pixel central de baixo para cima procurando pelo padrão visual, e vai recortar as imagens que tem rascunho analisando, salvando as imagens recortadas nessa pasta criada. As imagens que não tiverem rascunho, serão copiadas para a pasta de saída sem alterações.

OBS3: depende muito da sua prova. Tem provas que o rascunho é identificado por um padrão visual igual ao do início de uma questão; tem provas que o padrão é diferente. Tem provas que nem tem o padrão.

Nas provas em que o padrão visual do rascunho é igual ao do início de uma questão, provavelmente já recortou no passo 7.

Nas provas em que o padrão visual é diferente, você vai ter que identificar o padrão visual do rascunho, usar IA para mudar minimamente o código percorrendo o pixel de baixo para cima e procurar pelo padrão. Caso encontre, recorte antes de começar o padrão. Caso não encontre, significa que não tem rascunho e deve manter a imagem original, sem nenhuma alteração.

Nas provas que não tem padrão visual, pode ser interessante percorrer todos os pixels de baixo para cima, procurando por algum pixel que não seja branco. Enquanto encontrar linhas com pixels exclusivamente brancos, significa que ainda é rascunho. No momento que encontrar uma linha que tenha algum pixel que não seja branco, significa que acabou o rascunho e chegou nos pixels da alternativa E. Ou seja, deve-se cortar de modo que mantenha o pixel que não é branco.

CADA CASO É UM CASO. SEJA CRÍTICO. EXPLIQUE MUITO BEM PARA A IA!

OBS4: execute o código e abra as imagens para conferir se os excessos inferiores foram recortados corretamente. Se não, ajuste os valores de corte e execute novamente.
"""

from PIL import Image
import os
import shutil

def encontrar_faixa_inferior(imagem, cor_alvo, tolerancia=15):
    """
    Encontra a faixa descrita de baixo para cima
    Retorna a posição Y onde deve ser feito o corte (acima da faixa) ou None se não encontrar
    """
    largura, altura = imagem.size
    pixels = imagem.load()
    
    # Percorre a imagem de baixo para cima
    for y in range(altura - 1, 15, -1):  # Começa do fundo, precisa de pelo menos 12 pixels
        # Verifica o padrão da faixa: 4px azul, 4px branco, 4px azul
        faixa_encontrada = True
        
        # Verifica os 4 pixels azuis inferiores (y-11 até y-8)
        for dy in range(4):
            pixel_y = y - 11 + dy
            if pixel_y < 0:
                faixa_encontrada = False
                break
                
            pixel = pixels[largura // 2, pixel_y]
            if len(pixel) == 4:  # RGBA
                r, g, b, a = pixel
            else:  # RGB
                r, g, b = pixel[:3]
            
            # Verifica se é azul (dentro da tolerância)
            if (abs(r - cor_alvo[0]) > tolerancia or 
                abs(g - cor_alvo[1]) > tolerancia or 
                abs(b - cor_alvo[2]) > tolerancia):
                faixa_encontrada = False
                break
        
        if not faixa_encontrada:
            continue
            
        # Verifica os 4 pixels brancos do meio (y-7 até y-4)
        for dy in range(4):
            pixel_y = y - 7 + dy
            pixel = pixels[largura // 2, pixel_y]
            if len(pixel) == 4:  # RGBA
                r, g, b, a = pixel
            else:  # RGB
                r, g, b = pixel[:3]
            
            # Verifica se é branco (dentro da tolerância)
            if (abs(r - 255) > tolerancia or 
                abs(g - 255) > tolerancia or 
                abs(b - 255) > tolerancia):
                faixa_encontrada = False
                break
        
        if not faixa_encontrada:
            continue
            
        # Verifica os 4 pixels azuis superiores (y-3 até y)
        for dy in range(4):
            pixel_y = y - 3 + dy
            pixel = pixels[largura // 2, pixel_y]
            if len(pixel) == 4:  # RGBA
                r, g, b, a = pixel
            else:  # RGB
                r, g, b = pixel[:3]
            
            # Verifica se é azul (dentro da tolerância)
            if (abs(r - cor_alvo[0]) > tolerancia or 
                abs(g - cor_alvo[1]) > tolerancia or 
                abs(b - cor_alvo[2]) > tolerancia):
                faixa_encontrada = False
                break
        
        if faixa_encontrada:
            print(f"Faixa encontrada! Cortando na posição y={y-11}")
            return y - 11  # Retorna a posição acima da faixa completa
    
    return None

def processar_imagens(pasta_origem, pasta_destino, cor_alvo):
    """
    Processa todas as imagens da pasta origem, recortando as que têm faixa azul inferior
    e copiando todas para a pasta destino
    """
    # Cria a pasta de destino se não existir
    os.makedirs(pasta_destino, exist_ok=True)
    
    # Lista todos os arquivos da pasta origem
    arquivos = [f for f in os.listdir(pasta_origem) 
                if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tiff'))]
    
    print(f"Encontrados {len(arquivos)} arquivos para processar")
    
    for arquivo in arquivos:
        caminho_origem = os.path.join(pasta_origem, arquivo)
        caminho_destino = os.path.join(pasta_destino, arquivo)
        
        try:
            # Abre a imagem
            with Image.open(caminho_origem) as imagem:
                print(f"\nProcessando: {arquivo} ({imagem.width}x{imagem.height})")
                
                # Procura pela faixa inferior
                posicao_corte = encontrar_borda_inferior(imagem, cor_alvo)
                
                if posicao_corte is not None and posicao_corte > 0:
                    # Se encontrou a faixa, recorta a imagem
                    area_corte = (0, 0, imagem.width, posicao_corte)
                    imagem_recortada = imagem.crop(area_corte)
                    imagem_recortada.save(caminho_destino)
                    print(f"✓ Imagem recortada: {imagem_recortada.width}x{imagem_recortada.height}")
                else:
                    # Se não encontrou faixa, copia a imagem original
                    shutil.copy2(caminho_origem, caminho_destino)
                    print(f"✓ Imagem mantida original (sem faixa detectada)")
                    
        except Exception as e:
            print(f"✗ Erro ao processar {arquivo}: {e}")
            # Tenta copiar o arquivo mesmo com erro
            try:
                shutil.copy2(caminho_origem, caminho_destino)
                print(f"✓ Arquivo copiado mesmo com erro")
            except:
                print(f"✗ Não foi possível copiar o arquivo")

# Função principal
if __name__ == "__main__":
    # Configurações
    pasta_origem = "./questoes"
    pasta_destino = "finalizadas"
    cor_alvo = (64, 193, 243)  # RGB 0a255 da cor da faixa do caderno (atualize com o RGB correto usando o GIMP)
    
    print("Iniciando processamento de imagens...")
    print(f"Pasta origem: {pasta_origem}")
    print(f"Pasta destino: {pasta_destino}")
    print(f"Cor alvo: RGB{cor_alvo}")
    
    # Verifica se a pasta origem existe
    if not os.path.exists(pasta_origem):
        print(f"Erro: A pasta '{pasta_origem}' não existe!")
        exit(1)
    
    # Executa o processamento
    processar_imagens(pasta_origem, pasta_destino, cor_alvo)
    
    print("\n" + "="*50)
    print("Processamento concluído!")
    print(f"Todas as imagens foram salvas em: {pasta_destino}")