from PIL import Image
import os

def cores_iguais(cor1, cor2, tolerancia=15):
    """
    Verifica se duas cores RGB(A) são semelhantes dentro da tolerância dada.
    """
    r1, g1, b1 = cor1[:3]
    r2, g2, b2 = cor2[:3]
    return (abs(r1 - r2) <= tolerancia and
            abs(g1 - g2) <= tolerancia and
            abs(b1 - b2) <= tolerancia)

def verificar_faixa(pixels, x, y_inicio, altura_max, cor_alvo, min_px, max_px, tolerancia=15):
    """
    Conta quantos pixels consecutivos a partir de y_inicio correspondem à cor_alvo.
    Retorna a altura da faixa se estiver entre [min_px, max_px], senão retorna 0.
    """
    count = 0
    y = y_inicio
    while y < altura_max:
        if cores_iguais(pixels[x, y], cor_alvo, tolerancia):
            count += 1
            y += 1
        else:
            break
            
    if min_px <= count <= max_px:
        return count
    return 0

def verificar_padrao_no_ponto(pixels, x, y, altura_max, tolerancia=15):
    """
    Verifica se a partir da posição y existe o padrão de 3 faixas consecutivas:
    - Faixa 1: RGB (35, 31, 32) -> 6px (margem: 4 a 8px)
    - Faixa 2: RGB (211, 210, 210) -> 4px (margem: 2 a 6px)
    - Faixa 3: RGB (35, 31, 32) -> 3px (margem: 1 a 5px)
    
    Retorna o tamanho total do padrão se encontrado, ou 0 caso contrário.
    """
    cor1 = (35, 31, 32)
    cor2 = (211, 210, 210)
    cor3 = (35, 31, 32)

    # Faixa 1: 6px (6 ± 2 -> min 4, max 8)
    h1 = verificar_faixa(pixels, x, y, altura_max, cor1, 4, 8, tolerancia)
    if h1 == 0:
        return 0

    # Faixa 2: 4px (4 ± 2 -> min 2, max 6)
    y_f2 = y + h1
    h2 = verificar_faixa(pixels, x, y_f2, altura_max, cor2, 2, 6, tolerancia)
    if h2 == 0:
        return 0

    # Faixa 3: 3px (3 ± 2 -> min 1, max 5)
    y_f3 = y_f2 + h2
    h3 = verificar_faixa(pixels, x, y_f3, altura_max, cor3, 1, 5, tolerancia)
    if h3 == 0:
        return 0

    return h1 + h2 + h3

def encontrar_posicoes_corte(imagem, tolerancia=15):
    """
    Percorre o último pixel da direita de cima para baixo procurando o padrão.
    """
    largura, altura = imagem.size
    pixels = imagem.load()
    x_ultimo_pixel = largura - 2  # Último pixel da direita
    
    posicoes_corte = []
    y = 0
    
    while y < altura - 13: # Garante espaço mínimo para verificar o padrão completo
        tamanho_padrao = verificar_padrao_no_ponto(pixels, x_ultimo_pixel, y, altura, tolerancia)
        
        if tamanho_padrao > 0:
            # Corta 21 pixels antes de começar o padrão
            posicao_corte = y - 21
            if posicao_corte < 0:
                posicao_corte = 0
                
            posicoes_corte.append(posicao_corte)
            print(f"Padrão visual encontrado em y={y}, cortando em y={posicao_corte}")
            
            # Avança o ponteiro após o padrão detectado para evitar detecção duplicada
            y += tamanho_padrao
        else:
            y += 1
            
    return posicoes_corte

def dividir_imagem_por_faixas(caminho_imagem, pasta_saida):
    """
    Divide a imagem verticalmente com base nas posições de corte identificadas.
    """
    imagem = Image.open(caminho_imagem)
    largura, altura = imagem.size
    
    print(f"Imagem carregada: {largura}x{altura} pixels")
    
    posicoes_corte = encontrar_posicoes_corte(imagem)
    
    if not posicoes_corte:
        print("Nenhum padrão visual encontrado na imagem!")
        return
    
    print(f"Encontradas {len(posicoes_corte)} ocorrências do padrão para corte")
    os.makedirs(pasta_saida, exist_ok=True)
    
    posicao_anterior = 0
    
    for i, posicao_corte in enumerate(posicoes_corte):
        if posicao_corte <= posicao_anterior:
            continue
            
        area_corte = (0, posicao_anterior, largura, posicao_corte)
        secao = imagem.crop(area_corte)
        
        nome_arquivo = f"parte_{i+1:03d}.png"
        caminho_completo = os.path.join(pasta_saida, nome_arquivo)
        secao.save(caminho_completo)
        print(f"Salvo: {caminho_completo} ({secao.width}x{secao.height}px)")
        
        posicao_anterior = posicao_corte
    
    # Seção final da imagem
    if posicao_anterior < altura:
        area_corte = (0, posicao_anterior, largura, altura)
        secao = imagem.crop(area_corte)
        
        nome_arquivo = f"parte_{len(posicoes_corte)+1:03d}.png"
        caminho_completo = os.path.join(pasta_saida, nome_arquivo)
        secao.save(caminho_completo)
        print(f"Salvo: {caminho_completo} ({secao.width}x{secao.height}px)")

if __name__ == "__main__":
    caminho_imagem = "colunas_concatenadas_verticalmente.png"  # Substitua pelo caminho da sua imagem
    pasta_saida = "questoes"           # Substitua pelo nome da pasta de saída
    
    dividir_imagem_por_faixas(caminho_imagem, pasta_saida)
    print("Divisão concluída!")