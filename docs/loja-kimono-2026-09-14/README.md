# Kimono Competition e compartilhamento — 14/09/2026

Pedido: usar o desenho enviado como referência do Kimono BJ Sports Competition e incluir Compartilhar no card. A confirmação foi aplicada às versões branca, preta e azul royal. As imagens são representações ilustrativas, com frente e costas juntas; não são fotografias nem confirmação comercial de itens incluídos.

## Entrega

- Botão Compartilhar no card e nos detalhes; em navegadores compatíveis abre a interface do dispositivo. Nos demais, copia o link. Se a cópia não for permitida, mostra o endereço selecionável. Cancelar não dispara outra ação.
- Endereço `/loja.html?produto=BJJ-001&cor=branco` abre os detalhes na cor indicada. Cor inválida usa a primeira opção; produto inexistente não abre detalhes. O link não carrega outros parâmetros da página.
- Imagem, cor e preço existentes ficam sincronizados no card e nos detalhes. Alterar a cor mantém o tamanho escolhido. Filtros e ordenação usam o preço da cor selecionada.
- Imagens completas, controles de toque, foco visível, fechamento com Escape, retorno do foco e navegação de teclado dentro dos detalhes.
- Cadastro/edição de produtos, preços, estoque, ocultação e personalizações persistidas foram preservados. Somente caminhos conhecidos das imagens antigas do BJJ-001 são substituídos na leitura de personalizações; imagens enviadas pelos instrutores continuam prioritárias. Não há migração nem regravação do JSON comercial.

## Imagens e implementação

Geração pela ferramenta integrada image_gen, com o desenho do usuário como referência. Prompts em `prompts.md`. Arquivos versionados em `static/img/store/kimono_{branco,preto,azul}_frente_costas_v1.png`; originais preservados. As pequenas inscrições dos emblemas são uma interpretação visual gerada, não um arquivo de bordado para fabricação.

Sete arquivos de publicação em `manifesto.json`: catálogo Python, template, JavaScript, CSS e três imagens. A imagem Docker candidata parte da imagem atualmente publicada e incorpora somente esses sete arquivos.

Documentação técnica consultada: [Web Share](https://developer.mozilla.org/en-US/docs/Web/API/Navigator/share) e [Clipboard.writeText](https://developer.mozilla.org/en-US/docs/Web/API/Clipboard/writeText).

## Validação

- `tests/ui/store_sharing.py`: 360, 390 e 1440 px; três cores, links diretos, preço, tamanho, interesses, foco/teclado, cancelamento, permissões negadas e cópia manual; ausência de transbordamento horizontal e erros JavaScript.
- `tests/test_store_catalog.py`: preservação dos dados persistidos e das imagens personalizadas ao atualizar caminhos antigos.
- Suíte Flask/SQLite e suíte em PostgreSQL isolado. 113 testes passaram no SQLite e 113 no PostgreSQL. A interface publicada passou nas três larguras. Resultados em `validacao.json`, com capturas `publicado-card-390.png` e `publicado-modal-1440.png`.
- Compartilhamento nativo e clipboard são simulados no teste automatizado; nenhum destinatário recebe mensagem. A interface nativa em aparelho físico continua dependente do navegador/sistema operacional.

## Publicação e reversão

VPS `/data/bjsports`, aplicação `bjsports-app`. Backup em `/data/bjsports/backups/20260914-loja-kimono`: fonte, imagem Docker, volume persistente, PostgreSQL e cópia final feita com a aplicação parada. Restauração do PostgreSQL ensaiada em banco isolado; inicialização da candidata compara hashes das linhas existentes.

Reversão: `bash /data/bjsports/backups/20260914-loja-kimono/rollback.sh`. Restaura os quatro arquivos de código anteriores e a imagem Docker preservada. Não restaura o banco nem sobrescreve o volume, evitando perder cadastros ou edições posteriores à publicação. Novas imagens versionadas podem permanecer sem uso.

Os valores ilustrativos e textos comerciais preexistentes não foram homologados nesta entrega. A prévia de redes sociais continua usando os metadados gerais da loja; o link abre o produto e a cor.

Publicação concluída em 14/09/2026 às 08:03:16 UTC (05:03:16 Recife). Sete arquivos conferidos no container e cinco recursos estáticos conferidos pelo domínio público. Backup final restaurado: 21 tabelas, 23 cadastros preservados; 348 arquivos de código fora do pacote preservados. Banco e rede de ensaio removidos.
