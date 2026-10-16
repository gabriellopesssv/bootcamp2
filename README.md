# Clima em Foco

Aplicação web colaborativa para salvar cidades e consultar as condições atuais do tempo. Os dados das cidades ficam persistidos em SQLite; a localização e o clima são consultados na API pública Open-Meteo, sem chave de acesso.

**Repositório:** https://github.com/gabriellopesssv/bootcamp2

## Integrantes

| Nome | Matrícula | GitHub | Funcionalidade | PR principal |
|---|---:|---|---|---|
| Gabriel Lopes da Silva | 22611427 | [@gabriellopesssv](https://github.com/gabriellopesssv) | Interface e fluxo de consulta do clima (proposta) | A preencher após sua PR |
| Enzo Rodrigues Nascimento | 22612071 | [@enzorodrigues-source](https://github.com/enzorodrigues-source) | Persistência SQLite, integração com Open-Meteo e testes | [PR da aplicação](https://github.com/gabriellopesssv/bootcamp2/pull/1) |

A divisão da funcionalidade de Gabriel é uma proposta para confirmar com o grupo. Cada integrante deve ter ao menos uma PR de código revisada por outro membro.

## Tecnologias e serviços

- Python 3.12 e biblioteca padrão (servidor HTTP e testes `unittest`).
- SQLite para persistir as cidades salvas.
- [Open-Meteo Geocoding API](https://open-meteo.com/en/docs/geocoding-api) para localizar cidades e [Forecast API](https://open-meteo.com/en/docs) para consultar as condições atuais.

## Executar localmente

Requer Python 3.10 ou superior. Não é necessário instalar dependências externas.

```bash
python app.py
```

Acesse http://localhost:8000. Por padrão, o banco é criado em `data/cities.db`. Para usar outro caminho ou porta:

```bash
DATABASE_PATH=./data/cities.db PORT=8000 python app.py
```

No PowerShell:

```powershell
$env:DATABASE_PATH = ".\data\cities.db"
$env:PORT = "8000"
python app.py
```

## Testes

```bash
python -m unittest discover -s tests -v
```

Os testes cobrem a busca e normalização de cidades, descrições de condições meteorológicas e as operações de criar, listar e excluir cidades no SQLite. As chamadas externas são simuladas nos testes.

## Docker

Construa a imagem localmente:

```bash
docker build -t clima-em-foco .
```

Execute com armazenamento persistente:

```bash
docker run --rm -p 8000:8000 -v clima-data:/data enzoorodrigues/clima-em-foco:latest
```

Acesse http://localhost:8000. O volume `clima-data` preserva o banco entre execuções.

**Docker Hub:** [enzoorodrigues/clima-em-foco](https://hub.docker.com/r/enzoorodrigues/clima-em-foco)

## CI e fluxo de contribuição

O workflow `.github/workflows/ci.yml` executa os testes em cada pull request para `main` e em cada push para `main`. Configure a proteção da `main` no GitHub para exigir uma aprovação e o check **Testes automatizados** antes do merge. Faça cada funcionalidade em uma branch `feature/...`, abra uma PR e solicite revisão de outro integrante.

## Evidências da entrega

- **PR bloqueada por falha no CI:** adicionar aqui o print de uma PR real com o check de testes reprovado.
- **Conflito de merge resolvido:** relatar aqui um conflito real resolvido pelo grupo, se ocorrer. Não houve conflito registrado neste repositório até o momento.

As configurações de proteção, revisões e publicação no Docker Hub precisam ser feitas na conta do grupo; este repositório não registra nem simula essas ações.
