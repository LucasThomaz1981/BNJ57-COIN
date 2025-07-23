# 🤝 Guia de Contribuição - BNJ57

Bem-vindo à comunidade BNJ57! Este guia irá ajudá-lo a contribuir de forma efetiva para o projeto. Estamos empolgados para ter você a bordo desta jornada revolucionária!

## 📋 Índice

1. [Código de Conduta](#código-de-conduta)
2. [Como Contribuir](#como-contribuir)
3. [Configuração do Ambiente](#configuração-do-ambiente)
4. [Padrões de Código](#padrões-de-código)
5. [Processo de Pull Request](#processo-de-pull-request)
6. [Tipos de Contribuição](#tipos-de-contribuição)
7. [Comunidade e Suporte](#comunidade-e-suporte)

---

## 🌟 Código de Conduta

### Nossa Promessa

Nós, como membros, contribuidores e líderes, nos comprometemos a fazer da participação em nossa comunidade uma experiência livre de assédio para todos, independentemente de idade, tamanho corporal, deficiência visível ou invisível, etnia, características sexuais, identidade e expressão de gênero, nível de experiência, educação, status socioeconômico, nacionalidade, aparência pessoal, raça, religião ou identidade e orientação sexual.

### Nossos Padrões

Exemplos de comportamento que contribuem para um ambiente positivo:

- Demonstrar empatia e bondade com outras pessoas
- Ser respeitoso com opiniões, pontos de vista e experiências diferentes
- Dar e aceitar feedback construtivo de forma elegante
- Aceitar responsabilidade e pedir desculpas aos afetados por nossos erros
- Focar no que é melhor não apenas para nós como indivíduos, mas para a comunidade como um todo

### Comportamentos Inaceitáveis

- Uso de linguagem ou imagens sexualizadas e atenção sexual indesejada
- Trolling, comentários insultuosos ou depreciativos, e ataques pessoais ou políticos
- Assédio público ou privado
- Publicar informações privadas de outros sem permissão explícita
- Outras condutas que poderiam ser consideradas inadequadas em um ambiente profissional

---

## 🚀 Como Contribuir

### 1. Encontre uma Issue

- Navegue pelas [issues abertas](https://github.com/bnj57/bnj57/issues)
- Procure por labels como `good first issue` ou `help wanted`
- Leia a descrição completa e os comentários
- Comente na issue se tiver dúvidas

### 2. Fork e Clone

```bash
# Fork o repositório no GitHub
# Clone seu fork localmente
git clone https://github.com/SEU_USERNAME/bnj57.git
cd bnj57

# Adicione o repositório original como upstream
git remote add upstream https://github.com/bnj57/bnj57.git
```

### 3. Crie uma Branch

```bash
# Crie uma branch para sua feature/fix
git checkout -b feature/nome-da-sua-feature

# Ou para bug fixes
git checkout -b fix/nome-do-bug
```

### 4. Faça suas Mudanças

- Siga os [padrões de código](#padrões-de-código)
- Adicione testes para novas funcionalidades
- Atualize a documentação se necessário
- Commit suas mudanças com mensagens descritivas

### 5. Teste Localmente

```bash
# Execute os testes
npm test  # Para frontend
pytest    # Para backend

# Verifique a qualidade do código
npm run lint
flake8 .
```

### 6. Submeta um Pull Request

- Push sua branch para seu fork
- Abra um Pull Request no repositório original
- Preencha o template de PR completamente
- Aguarde o review da equipe

---

## ⚙️ Configuração do Ambiente

### Pré-requisitos

- **Node.js** 18+ e npm
- **Python** 3.9+ e pip
- **Docker** e Docker Compose
- **Git**
- **PostgreSQL** (para desenvolvimento local)
- **Redis** (para cache e filas)

### Setup Completo

#### 1. Clone e Instale Dependências

```bash
# Clone o repositório
git clone https://github.com/bnj57/bnj57.git
cd bnj57

# Instale dependências do backend
cd exchange-backend
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Instale dependências do frontend
cd ../exchange-platform
npm install
```

#### 2. Configuração do Banco de Dados

```bash
# Inicie PostgreSQL e Redis com Docker
docker-compose up -d postgres redis

# Execute as migrações
cd exchange-backend
flask db upgrade
```

#### 3. Variáveis de Ambiente

Crie um arquivo `.env` na raiz do projeto:

```env
# Database
DATABASE_URL=postgresql://bnj57:password@localhost:5432/bnj57_dev
REDIS_URL=redis://localhost:6379/0

# Blockchain
ETHEREUM_RPC_URL=https://mainnet.infura.io/v3/YOUR_PROJECT_ID
ETHEREUM_TESTNET_RPC_URL=https://goerli.infura.io/v3/YOUR_PROJECT_ID

# Security
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-here

# External APIs
COINBASE_API_KEY=your-coinbase-api-key
ETHERSCAN_API_KEY=your-etherscan-api-key
```

#### 4. Inicie os Serviços

```bash
# Terminal 1: Backend
cd exchange-backend
flask run --debug

# Terminal 2: Frontend
cd exchange-platform
npm start

# Terminal 3: Worker (para processamento assíncrono)
cd exchange-backend
celery -A app.celery worker --loglevel=info
```

### Verificação da Instalação

- Frontend: http://localhost:3000
- Backend API: http://localhost:5000
- API Docs: http://localhost:5000/docs

---

## 📝 Padrões de Código

### Python (Backend)

#### Estilo de Código

```python
# Use PEP 8 como base
# Imports organizados
import os
import sys
from datetime import datetime

from flask import Flask, request
from sqlalchemy import Column, Integer, String

# Docstrings em todas as funções públicas
def calculate_recovery_probability(wallet_address: str) -> float:
    """
    Calcula a probabilidade de recuperação de uma carteira.
    
    Args:
        wallet_address: Endereço da carteira a ser analisada
        
    Returns:
        Probabilidade entre 0.0 e 1.0
        
    Raises:
        ValueError: Se o endereço for inválido
    """
    pass

# Type hints sempre que possível
def process_claim(claim_id: int, user_id: int) -> Dict[str, Any]:
    pass
```

#### Estrutura de Arquivos

```
exchange-backend/
├── app/
│   ├── __init__.py
│   ├── models/
│   ├── routes/
│   ├── services/
│   ├── utils/
│   └── tests/
├── migrations/
├── requirements.txt
└── config.py
```

#### Testes

```python
import pytest
from app import create_app, db
from app.models import User, Claim

@pytest.fixture
def client():
    app = create_app('testing')
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            db.drop_all()

def test_create_claim(client):
    """Testa a criação de uma nova reivindicação."""
    response = client.post('/api/v1/claims', json={
        'wallet_address': '0x742d35Cc6634C0532925a3b8D',
        'description': 'Lost access to my wallet'
    })
    assert response.status_code == 201
```

### JavaScript/TypeScript (Frontend)

#### Estilo de Código

```typescript
// Use TypeScript sempre que possível
interface WalletClaim {
  id: string;
  walletAddress: string;
  status: 'pending' | 'processing' | 'completed' | 'rejected';
  createdAt: Date;
}

// Componentes funcionais com hooks
const ClaimForm: React.FC = () => {
  const [walletAddress, setWalletAddress] = useState<string>('');
  const [isLoading, setIsLoading] = useState<boolean>(false);
  
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    
    try {
      await submitClaim(walletAddress);
    } catch (error) {
      console.error('Error submitting claim:', error);
    } finally {
      setIsLoading(false);
    }
  };
  
  return (
    <form onSubmit={handleSubmit}>
      {/* JSX aqui */}
    </form>
  );
};
```

#### Estrutura de Componentes

```
exchange-platform/src/
├── components/
│   ├── common/
│   ├── forms/
│   └── layout/
├── hooks/
├── services/
├── types/
├── utils/
└── __tests__/
```

#### Testes

```typescript
import { render, screen, fireEvent } from '@testing-library/react';
import { ClaimForm } from '../ClaimForm';

describe('ClaimForm', () => {
  it('should submit form with valid wallet address', async () => {
    render(<ClaimForm />);
    
    const input = screen.getByLabelText(/wallet address/i);
    const button = screen.getByRole('button', { name: /submit/i });
    
    fireEvent.change(input, { 
      target: { value: '0x742d35Cc6634C0532925a3b8D' } 
    });
    fireEvent.click(button);
    
    expect(screen.getByText(/claim submitted/i)).toBeInTheDocument();
  });
});
```

### Solidity (Smart Contracts)

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";

/**
 * @title BNJ57Token
 * @dev Token ERC20 para o ecossistema BNJ57
 */
contract BNJ57Token is ERC20, Ownable, ReentrancyGuard {
    uint256 public constant MAX_SUPPLY = 1_000_000_000 * 10**18;
    
    event TokensMinted(address indexed to, uint256 amount);
    
    constructor() ERC20("BNJ57", "BNJ57") {}
    
    /**
     * @dev Mint tokens para um endereço específico
     * @param to Endereço que receberá os tokens
     * @param amount Quantidade de tokens a serem mintados
     */
    function mint(address to, uint256 amount) external onlyOwner {
        require(totalSupply() + amount <= MAX_SUPPLY, "Exceeds max supply");
        _mint(to, amount);
        emit TokensMinted(to, amount);
    }
}
```

---

## 🔄 Processo de Pull Request

### 1. Antes de Submeter

- [ ] Código segue os padrões estabelecidos
- [ ] Testes passam localmente
- [ ] Documentação foi atualizada
- [ ] Commit messages são descritivas
- [ ] Branch está atualizada com main

### 2. Template de PR

Ao abrir um PR, preencha todas as seções do template:

```markdown
## Descrição
Breve descrição das mudanças implementadas.

## Tipo de Mudança
- [ ] Bug fix
- [ ] Nova feature
- [ ] Breaking change
- [ ] Documentação

## Como Testar
Passos para testar as mudanças.

## Checklist
- [ ] Testes passam
- [ ] Código revisado
- [ ] Documentação atualizada
```

### 3. Processo de Review

1. **Automated Checks**: CI/CD executa testes automaticamente
2. **Code Review**: Pelo menos 2 aprovações de maintainers
3. **Testing**: Testes manuais se necessário
4. **Merge**: Squash and merge para manter histórico limpo

### 4. Após o Merge

- Branch será deletada automaticamente
- Deploy automático para staging
- Notificação na issue relacionada

---

## 🎯 Tipos de Contribuição

### 🐛 Bug Reports

Encontrou um bug? Ajude-nos a corrigi-lo:

1. Verifique se já não existe uma issue similar
2. Use o template de bug report
3. Inclua passos para reproduzir
4. Adicione screenshots se aplicável
5. Especifique seu ambiente (OS, browser, etc.)

### ✨ Feature Requests

Tem uma ideia para melhorar a BNJ57?

1. Verifique o roadmap para ver se já está planejado
2. Use o template de feature request
3. Explique o problema que a feature resolve
4. Descreva a solução proposta
5. Considere alternativas

### 📚 Documentação

A documentação é crucial para o sucesso do projeto:

- Corrija erros de digitação
- Melhore explicações existentes
- Adicione exemplos de código
- Traduza para outros idiomas
- Crie tutoriais e guias

### 🧪 Testes

Ajude a melhorar a cobertura de testes:

- Adicione testes para código não coberto
- Melhore testes existentes
- Crie testes de integração
- Desenvolva testes de performance

### 🎨 Design e UX

Contribua para a experiência do usuário:

- Melhore a interface existente
- Crie novos componentes
- Otimize para mobile
- Melhore acessibilidade

---

## 🏆 Reconhecimento

### Contribuidores

Todos os contribuidores são reconhecidos em:

- README principal do projeto
- Página de contribuidores no site
- Releases notes
- Redes sociais

### Programa de Recompensas

- **First Contribution**: Badge especial + 100 BNJ57
- **Bug Bounty**: Até 10,000 BNJ57 para bugs críticos
- **Feature Implementation**: Recompensas baseadas na complexidade
- **Documentation**: 50-500 BNJ57 por contribuição

### Níveis de Contribuidor

1. **Contributor**: Primeira contribuição aceita
2. **Regular Contributor**: 5+ PRs merged
3. **Core Contributor**: 20+ PRs + review de outros PRs
4. **Maintainer**: Acesso de escrita + responsabilidades especiais

---

## 🤝 Comunidade e Suporte

### Canais de Comunicação

- **Discord**: [Servidor BNJ57](https://discord.gg/bnj57) - Chat em tempo real
- **Telegram**: [@BNJ57Developers](https://t.me/BNJ57Developers) - Discussões técnicas
- **GitHub Discussions**: Para discussões longas e planejamento
- **Twitter**: [@BNJ57Dev](https://twitter.com/BNJ57Dev) - Atualizações e anúncios

### Horários de Suporte

- **Segunda a Sexta**: 9h às 18h (UTC-3)
- **Fins de Semana**: Suporte limitado
- **Emergências**: 24/7 via Discord

### Mentoria

Novo no projeto? Temos um programa de mentoria:

- Pareamento com contribuidores experientes
- Sessões de onboarding semanais
- Revisão de código personalizada
- Suporte técnico dedicado

### Eventos

- **Weekly Dev Sync**: Terças, 15h UTC-3
- **Monthly Community Call**: Primeira sexta do mês
- **Hackathons**: Trimestrais
- **Conferences**: Presença em eventos da comunidade

---

## 📞 Precisa de Ajuda?

Não hesite em pedir ajuda! Estamos aqui para apoiá-lo:

- **Dúvidas Gerais**: Discord #general
- **Questões Técnicas**: Discord #dev-help
- **Bugs**: Abra uma issue no GitHub
- **Ideias**: GitHub Discussions
- **Privado**: dev@bnj57.io

---

**Obrigado por contribuir para a BNJ57! Juntos, estamos construindo o futuro da recuperação descentralizada de criptomoedas.** 🚀

---

*Última atualização: 22 de Julho de 2025*

