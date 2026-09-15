# Rashguards e fight shorts — 14/09/2026

Atualização das imagens de quatro produtos da loja. Geração pela ferramenta integrada image_gen, usando as artes anteriormente publicadas como referência. A imagem de rashguard preta enviada pelo usuário orienta a modelagem, o volume e a textura, mantendo a identidade visual das estampas.

| Produto | Imagem final em `static/img/store/` | Apresentação |
| --- | --- | --- |
| Rashguard Ranked Eagle (Manga Longa), BJJ-004 | `rashguard_eagle_studio_v1.png` | Frente e costas, mangas longas, águia cinza, painéis vermelhos e marcas existentes. |
| Camiseta de Treino Camuflada BJ Sports, BJJ-007 | `rashguard_camuflada_studio_v1.png` | Frente e costas, mangas curtas, tecido de compressão e camuflado vermelho/cinza. |
| Fight Shorts Pro Brasil BJ Sports, BJJ-006 | `fight_shorts_brasil_studio_v1.png` | Vista frontal com volume, bandeira, lettering lateral e detalhes vermelhos/brancos. |
| Fight Shorts Grappling (Preto/Vermelho), BJJ-005 | `fight_shorts_grappling_studio_v1.png` | Frente e costas alinhadas, tecido preto e arte vermelha existente. |

As quatro imagens usam fundo claro de estúdio. Removidos os logos e elementos promocionais externos às peças presentes nos cartazes antigos. As imagens são representações ilustrativas; detalhes de lettering gerado não substituem a arte original para confecção. Originais preservados. Prompts completos em `prompts.md`.

Os quatro cards usam enquadramento quadrado e exibem a imagem inteira, com os selos na parte inferior para evitar cobrir o cós. Código do produto com contraste ajustado. Detalhes, cores e compartilhamento mantidos.

Preços, descrições, tamanhos, estoque e demais campos comerciais preservados. Personalizações com caminhos conhecidos de imagens antigas recebem a nova referência somente durante a leitura; imagens próprias enviadas pelos instrutores continuam prioritárias. Nenhum JSON persistido é regravado. Não há alteração de esquema ou migração do banco.

## Validação

- Comparação de todos os campos comerciais do catálogo anterior e atual, incluindo estoque, preço, ocultação e imagem personalizada.
- Teste existente de compatibilidade das personalizações.
- `tests/ui/store_product_images.py`: quatro produtos em 360, 390 e 1440 px, imagem completa, detalhes, preço, link compartilhado, abertura direta e ausência de transbordamento horizontal e erros JavaScript. Compartilhamento simulado, sem envio de mensagens.
- Restauração de PostgreSQL e volume em ambiente isolado; comparação das linhas existentes antes/depois da inicialização da aplicação candidata. Não foi repetida a suíte de regras de cadastro/check-in, pois esta entrega altera imagens e apresentação do catálogo.

## Publicação e reversão

Pacote de sete arquivos em `manifesto.json`: catálogo, CSS, template e quatro PNGs. A candidata parte da imagem Docker publicada que já inclui o kimono e o compartilhamento.

Backup histórico: `/data/bjsports/backups/20260914-loja-vestuario`. Os arquivos de recuperação dessa pasta foram encontrados incompletos na retomada; ela não é mais referência de reversão disponível. A segunda entrega preparou uma nova recuperação completa, incluindo estas imagens, descrita em [cadastro e portal](../segunda-entrega-2026-09-14/README.md).

Resultados em `validacao.json`. Capturas históricas permanecem nos arquivos operacionais da validação.
