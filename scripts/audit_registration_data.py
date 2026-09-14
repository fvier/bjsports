#!/usr/bin/env python3
"""Audita CPFs sem carregar o app (que possui migrações na importação).
DATABASE_URL obrigatório. --apply-index cria somente o índice de unicidade.
Não imprime CPFs, senhas ou nomes. Não mescla/exclui/reescreve contas.
"""
import argparse
import json
import os
import re
from sqlalchemy import create_engine, inspect, text

parser = argparse.ArgumentParser()
parser.add_argument('--apply-index', action='store_true')
args = parser.parse_args()
engine = create_engine(os.environ['DATABASE_URL'])
with engine.begin() as conn:
    if args.apply_index and engine.dialect.name == 'postgresql':
        conn.execute(text('LOCK TABLE "user" IN SHARE ROW EXCLUSIVE MODE'))
    rows = conn.execute(text('SELECT id, cpf FROM "user"')).all()
    groups, unsupported = {}, []
    for user_id, cpf in rows:
        normalized = re.sub(r'[^0-9]', '', cpf or '')
        groups.setdefault(normalized, []).append(user_id)
        if normalized != (cpf or '').replace('.', '').replace('-', '').replace(' ', '') or len(normalized) != 11:
            unsupported.append(user_id)
    collisions = [ids for ids in groups.values() if len(ids) > 1]
    report = {'accounts':len(rows), 'cpf_collision_user_ids':collisions,
              'cpf_unsupported_format_user_ids':unsupported, 'index_applied':False}
    if args.apply_index:
        if collisions or unsupported:
            print(json.dumps(report)); raise SystemExit('Índice não aplicado: revisão manual necessária; nenhuma conta foi alterada.')
        conn.execute(text('CREATE UNIQUE INDEX IF NOT EXISTS uq_user_cpf_normalized ON "user" (replace(replace(replace(cpf, \'.\', \'\'), \'-\', \'\'), \' \', \'\'))'))
        report['index_applied'] = True
    print(json.dumps(report))
