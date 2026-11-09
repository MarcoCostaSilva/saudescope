"""
SaúdeScope — upload_supabase.py
Sobe todas as tabelas do projeto para o Supabase (Postgres).

COMO USAR (na raiz da pasta saudescope):
  pip install sqlalchemy psycopg2-binary pandas pyarrow
  python scripts/upload_supabase.py
"""

import json
import os
from getpass import getpass
from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL

# ---------------------------------------------------------------------------
# CONFIGURAÇÃO
# ---------------------------------------------------------------------------
# Caminho calculado a partir do próprio script: funciona de qualquer pasta.
RAIZ = Path(__file__).resolve().parent.parent
PASTA_DADOS = RAIZ / "data" / "processed"

# Conexão via Session pooler (funciona em redes sem IPv6)
DB_HOST = "aws-0-us-west-2.pooler.supabase.com"
DB_USER = "postgres.wtspfogpwbwtphfrhtwz"
DB_PORT = 5432
DB_NAME = "postgres"

# Tabelas derivadas de arquivos .parquet
TABELAS_PARQUET = {
    "pns_2019_sp_tratado.parquet":            "pessoas_pns_sp",
    "resumo_prevalencias_ponderadas.parquet": "resumo_prevalencias",
    "resultados_modelos_ml.parquet":          "resultados_modelos",
    "layout_variaveis_interesse.parquet":     "dicionario_variaveis",
    "insights_finais_saudescope.parquet":     "insights_saudescope",
}


def criar_engine():
    """A senha vem de variável de ambiente ou é digitada (não fica salva no código)."""
    senha = os.environ.get("SUPABASE_PASSWORD") or getpass("Senha do banco Supabase: ")
    url = URL.create(
        "postgresql+psycopg2",
        username=DB_USER,
        password=senha,
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
    )
    return create_engine(url)


def preparar_para_sql(df: pd.DataFrame) -> pd.DataFrame:
    """Converte tipos pandas nullable/category para tipos aceitos pelo Postgres."""
    df = df.copy()
    for col in df.columns:
        tipo = str(df[col].dtype)
        if tipo in ("Int64", "Int32", "Float64", "Float32"):
            df[col] = df[col].astype("float64")
        elif tipo == "category":
            df[col] = df[col].astype(str)
        elif tipo == "boolean":
            df[col] = df[col].astype("object").where(df[col].notna(), None)
    return df


def upload_config_modelo(engine, caminho_json: Path):
    """Sobe o config do modelo como uma única linha na tabela config_modelo."""
    with open(caminho_json, encoding="utf-8") as f:
        cfg = json.load(f)
    m = cfg["metricas_limiar_recomendado"]
    df_cfg = pd.DataFrame([{
        "modelo": cfg["modelo"],
        "limiar_recomendado": cfg["limiar_recomendado"],
        "limiar_padrao": cfg["limiar_padrao"],
        "auc_roc_teste": cfg["auc_roc_teste"],
        "acuracia": m["Acurácia"],
        "precisao": m["Precisão"],
        "recall": m["Recall"],
        "f1": m["F1"],
        "observacao": cfg["observacao"],
    }])
    df_cfg.to_sql("config_modelo", engine, if_exists="replace", index=False)
    print("[OK] config_modelo_hipertensao.json -> 'config_modelo' (1 linha)")


def main():
    print("=== SaúdeScope — Upload para Supabase ===\n")
    print(f"Pasta de dados: {PASTA_DADOS}\n")
    engine = criar_engine()

    # 1) Testar conexão
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
    except Exception as erro:
        print("[ERRO] Não foi possível conectar ao Supabase.\n")
        print(f"Detalhe: {str(erro).splitlines()[0]}\n")
        print("Dicas:")
        print("  - 'Tenant or user not found': confira DB_USER e DB_HOST.")
        print("  - 'password authentication failed': senha incorreta.")
        print("    Redefina em Supabase > Project Settings > Database.")
        return
    print("[OK] Conexão estabelecida.\n")

    # 2) Tabelas de parquet
    tabelas_criadas = []
    for nome_arquivo, nome_tabela in TABELAS_PARQUET.items():
        caminho = PASTA_DADOS / nome_arquivo
        if not caminho.exists():
            print(f"[AVISO] Arquivo não encontrado, pulando: {caminho}")
            continue
        df = preparar_para_sql(pd.read_parquet(caminho))
        df.to_sql(nome_tabela, engine, if_exists="replace", index=False,
                  chunksize=500, method="multi")
        tabelas_criadas.append(nome_tabela)
        print(f"[OK] {nome_arquivo:42s} -> '{nome_tabela}' ({len(df):,} linhas)")

    # 3) JSON do modelo
    caminho_cfg = PASTA_DADOS / "config_modelo_hipertensao.json"
    if caminho_cfg.exists():
        upload_config_modelo(engine, caminho_cfg)
        tabelas_criadas.append("config_modelo")
    else:
        print(f"[AVISO] Arquivo não encontrado, pulando: {caminho_cfg}")

    # 4) Conferência: conta as linhas direto no banco
    print("\n--- Conferência no banco ---")
    with engine.connect() as conn:
        for tabela in tabelas_criadas:
            n = conn.execute(text(f'SELECT COUNT(*) FROM "{tabela}"')).scalar()
            print(f"  {tabela:25s} {n:>7,} linhas")

    print("\n=== Upload concluído ===")
    print("Confira em Supabase > Table Editor.")


if __name__ == "__main__":
    main()