from __future__ import annotations

import json,argparse
from src.load import loading
from src.embed import ejecutar_embeddings
from src.index import index_2_chroma
from src.retrieve import search_k,generar_context
from src.logic import responder
from src.generate import ejecutar_evaluacion,evaluar_k

def _cmd_prepare(create:bool=False) -> None:   
    loading()
    print()
    ejecutar_embeddings(max_embed=None,create=create)


def _cmd_index(create: bool=False) -> None:      
    index_2_chroma(create=create)


def _cmd_query(pregunta: str, top_k: int | None) -> None:   
    resultados,modelo_embeddign = search_k(pregunta=pregunta, top_k=top_k)
    print(generar_context(resultados=resultados))


def _cmd_ask(pregunta: str, top_k: int | None) -> None:
    resultado = responder(pregunta=pregunta, top_k=top_k)
    print(json.dumps(
        {
            "respuesta": resultado.get("respuesta"),
            "fuentes": resultado.get("fuentes"),
            "error": resultado.get("error"),
        },
        ensure_ascii=False,
        indent=2,
    ))


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Live Review S10 — generación RAG calidad del aire"
    )
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--prepare", action="store_true")
    parser.add_argument("--index", action="store_true")
    parser.add_argument("--create-index", action="store_true")
    parser.add_argument("--create-prepare", action="store_true")
    parser.add_argument("--query", type=str, help="Solo retrieval (debug S9)")
    parser.add_argument("--ask", type=str, help="RAG completo: responder()")
    parser.add_argument("--top-k", type=int, default=None)
    parser.add_argument("--eval", action="store_true", help="Eval respuestas")
    parser.add_argument("--kEval", type=str, help="Eval top_k misma respuesta")

    args = parser.parse_args()

    if not any(
        [args.check, args.prepare, args.index, args.query, args.ask, args.eval, args.kEval]
    ):
        parser.print_help()
        print(
            "\nEjemplo:\n"
            "  python main.py --prepare --index\n"
            '  python main.py --ask "¿Qué mide la magnitud 83?"\n'
            "  python main.py --eval\n"
            '  python main.py --ask "¿Qué mide la magnitud 83?"\n'
            "  streamlit run app.py"
        )
        return

    if args.prepare or args.create_prepare:
        _cmd_prepare(create=args.create_prepare)
    if args.index or args.create_index:
        _cmd_index(create=args.create_index)
    if args.query:
        _cmd_query(args.query, args.top_k)
    if args.ask:
        _cmd_ask(args.ask, args.top_k)
    if args.eval:
        ejecutar_evaluacion()
    if args.kEval:
        evaluar_k(pregunta=args.kEval)


if __name__ == "__main__":
    main()
