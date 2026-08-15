# 🔍 Registro de Postmortem — Incidentes & Lições Aprendidas

Bem-vindo(a) ao registro de incidentes do repositório Receitas. Acreditamos que falhas não são motivos de vergonha, mas oportunidades de evolução e fortalecimento da nossa infraestrutura. Este documento visa documentar o que deu errado, entender as causas raízes de forma colaborativa e, o mais importante, definir ações práticas para garantir que nunca mais tenhamos o mesmo problema.

> [!IMPORTANT]
> **Regra de Alimentação Incremental:** Novas entradas devem ser inseridas sempre **no topo** da tabela. Nunca apague registros antigos. O histórico completo é essencial para auditoria e aprendizado contínuo.

## Registro de Incidentes

| # | Data | Incidente | Causa Raiz | Ação Corretiva | Responsável | Status |
|---|------|-----------|------------|----------------|-------------|--------|
| 1 | 2026-08-14 | Arquivo `.env` commitado acidentalmente | Falta do `.env` no arquivo `.gitignore` global e no repositório local | Remoção do arquivo do histórico do Git, invalidação das credenciais (rotação de chaves) e atualização do `.gitignore` padrão. | Equipe DevOps | Concluído |

## Template para Novo Incidente

Para adicionar um novo postmortem, copie a linha abaixo, preencha os dados e insira no topo da tabela acima.

```markdown
| Número sequencial | YYYY-MM-DD | Descrição breve do erro | O que causou o erro técnico ou humano? | O que foi ou será feito para evitar repetição? | Quem liderou a resolução | Status (Ex: Em andamento, Concluído) |
```

## Métricas

Manteremos um controle de nossas métricas para acompanhar a saúde e maturidade operacional do time:
- **MTTR (Mean Time to Recovery)**: Tempo médio gasto desde a detecção do incidente até sua completa mitigação.
- **Frequência de Incidentes**: Número total de incidentes reportados em um determinado período (ex: mensalmente).
- **Taxa de Recorrência**: Porcentagem de vezes em que o mesmo incidente se repetiu, o que indica se as ações corretivas de postmortems anteriores foram eficazes.
