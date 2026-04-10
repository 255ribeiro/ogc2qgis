# 📦 Estrutura do Pacote ogc2qgis

## ✅ Estrutura Correta

```
ogc2qgis/                          ← Pasta raiz do projeto
│
├── 📄 Configuração & Documentação
│   ├── pyproject.toml             ← Poetry config (BUILD SYSTEM)
│   ├── README.md                  ← Documentação principal
│   ├── QUICKSTART.md              ← Guia rápido
│   ├── PUBLISHING.md              ← Como publicar no PyPI
│   ├── CHANGELOG.md               ← Histórico de versões
│   ├── LICENSE                    ← MIT License
│   ├── MANIFEST.in                ← Arquivos para incluir no build
│   └── .gitignore                 ← Git ignore rules
│
├── 💻 Código Fonte
│   └── src/
│       └── ogc2qgis/
│           ├── __init__.py        ← API pública
│           ├── core.py            ← Funções principais
│           │
│           ├── parsers/           ← Parsers OGC
│           │   ├── __init__.py
│           │   ├── wms.py         ← Parser WMS
│           │   ├── wcs.py         ← Parser WCS
│           │   └── wfs.py         ← Parser WFS
│           │
│           └── cli/               ← Interface CLI
│               ├── __init__.py
│               └── main.py        ← Entry point
│
├── 🧪 Testes
│   └── tests/
│       └── test_basic.py          ← Suite de testes
│
├── 📚 Exemplos
│   └── examples/
│       ├── library_usage.py       ← Como usar como biblioteca
│       └── cli_usage.sh           ← Como usar CLI
│
└── 🤖 CI/CD
    └── .github/
        └── workflows/
            └── ci.yml             ← GitHub Actions
```

## 🚀 Como Usar Esta Estrutura

### 1️⃣ **Download**
Baixe a pasta `ogc2qgis/` completa

### 2️⃣ **Navegue**
```bash
cd ogc2qgis
```

### 3️⃣ **Instale Poetry**
```bash
pip install poetry
```

### 4️⃣ **Instale Dependências**
```bash
poetry install
```

### 5️⃣ **Teste**
```bash
# Rodar testes
poetry run pytest

# Testar CLI
poetry run ogc2qgis --help
```

### 6️⃣ **Publique no PyPI**
```bash
# Configure seu token PyPI
poetry config pypi-token.pypi SEU_TOKEN

# Build e publish
poetry publish --build
```

## 📂 Arquivos Importantes

### **pyproject.toml** (O MAIS IMPORTANTE!)
Este é o **coração do projeto**. Contém:
- Nome do pacote: `ogc2qgis`
- Versão: `0.1.0`
- Dependências: nenhuma!
- Entry point CLI: `ogc2qgis`
- Configuração do Poetry

### **src/ogc2qgis/**
O código fonte do pacote. Estrutura padrão:
```
src/
└── ogc2qgis/      ← Nome do pacote
    ├── __init__.py ← Define API pública
    ├── *.py        ← Módulos
    └── */          ← Subpacotes
```

### **tests/**
Testes com pytest:
```bash
poetry run pytest
```

## ❌ Não Há ZIP Dentro de ZIP

A estrutura correta é:
```
Você baixa: ogc2qgis/  (uma pasta)
    ├── pyproject.toml
    ├── src/
    ├── tests/
    └── ...
```

**NÃO** há outro ZIP dentro!

## ✅ Checklist de Arquivos

Execute na pasta `ogc2qgis/`:
```bash
# Verificar estrutura
ls -la

# Deve mostrar:
# - pyproject.toml ✓
# - src/ ✓
# - tests/ ✓
# - README.md ✓
# - .github/ ✓

# Verificar código Python
find src -name "*.py"

# Deve mostrar:
# src/ogc2qgis/__init__.py ✓
# src/ogc2qgis/core.py ✓
# src/ogc2qgis/parsers/wms.py ✓
# src/ogc2qgis/parsers/wcs.py ✓
# src/ogc2qgis/parsers/wfs.py ✓
# src/ogc2qgis/cli/main.py ✓
```

## 🎯 Próximo Passo

```bash
cd ogc2qgis
poetry install
poetry run pytest
```

Se tudo funcionar, está pronto para publicar! 🚀
