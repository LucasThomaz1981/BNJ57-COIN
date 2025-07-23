# 🚀 Guia de Deployment - Exchange ORSECA-BNJ57

## Visão Geral

Este guia fornece instruções detalhadas para fazer o deployment da Exchange ORSECA-BNJ57 em ambiente de produção. A arquitetura foi projetada para ser escalável, segura e de fácil manutenção.

## Pré-requisitos

### Infraestrutura Necessária

- **Servidor Principal**: 8 CPU cores, 16GB RAM, 500GB SSD
- **Banco de Dados**: PostgreSQL 14+ ou MySQL 8+
- **Cache**: Redis 6+
- **Load Balancer**: Nginx ou HAProxy
- **SSL Certificate**: Let's Encrypt ou certificado comercial
- **Domínio**: exchange.orseca.org (ou similar)

### Dependências de Software

- **Backend**: Python 3.11+, Flask, SQLAlchemy
- **Frontend**: Node.js 18+, React 18+, Vite
- **Containerização**: Docker 20+, Docker Compose
- **Monitoramento**: Prometheus, Grafana (opcional)

## Estrutura de Deployment

```
/opt/orseca-exchange/
├── backend/
│   ├── src/
│   ├── requirements.txt
│   ├── Dockerfile
│   └── docker-compose.yml
├── frontend/
│   ├── src/
│   ├── package.json
│   ├── Dockerfile
│   └── dist/
├── nginx/
│   ├── nginx.conf
│   └── ssl/
├── database/
│   ├── init.sql
│   └── migrations/
└── scripts/
    ├── deploy.sh
    ├── backup.sh
    └── update.sh
```

## Configuração do Backend

### 1. Preparação do Ambiente

```bash
# Criar usuário para a aplicação
sudo useradd -m -s /bin/bash orseca-exchange
sudo usermod -aG docker orseca-exchange

# Criar diretórios
sudo mkdir -p /opt/orseca-exchange
sudo chown -R orseca-exchange:orseca-exchange /opt/orseca-exchange

# Clonar repositório
cd /opt/orseca-exchange
git clone https://github.com/orseca/bnj57-exchange.git .
```

### 2. Configuração de Variáveis de Ambiente

```bash
# Criar arquivo .env
cat > /opt/orseca-exchange/.env << EOF
# Configurações da Aplicação
FLASK_ENV=production
SECRET_KEY=sua-chave-secreta-super-segura
JWT_SECRET_KEY=sua-chave-jwt-super-segura

# Banco de Dados
DATABASE_URL=postgresql://orseca_user:senha_segura@localhost:5432/orseca_exchange

# Redis
REDIS_URL=redis://localhost:6379/0

# APIs Externas
BLOCKCHAIN_RPC_URL=https://mainnet.infura.io/v3/seu-projeto-id
COINGECKO_API_KEY=sua-api-key-coingecko

# Configurações de Email
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=noreply@orseca.org
SMTP_PASSWORD=senha-do-email

# Configurações de Segurança
ALLOWED_HOSTS=exchange.orseca.org,www.exchange.orseca.org
CORS_ORIGINS=https://exchange.orseca.org

# Configurações de Upload
MAX_CONTENT_LENGTH=16777216
UPLOAD_FOLDER=/opt/orseca-exchange/uploads
EOF
```

### 3. Configuração do Docker Compose

```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  backend:
    build: 
      context: ./backend
      dockerfile: Dockerfile.prod
    container_name: orseca-backend
    restart: unless-stopped
    environment:
      - FLASK_ENV=production
    env_file:
      - .env
    volumes:
      - ./uploads:/app/uploads
      - ./logs:/app/logs
    depends_on:
      - database
      - redis
    networks:
      - orseca-network

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile.prod
    container_name: orseca-frontend
    restart: unless-stopped
    volumes:
      - ./frontend/dist:/usr/share/nginx/html
    networks:
      - orseca-network

  database:
    image: postgres:14
    container_name: orseca-db
    restart: unless-stopped
    environment:
      POSTGRES_DB: orseca_exchange
      POSTGRES_USER: orseca_user
      POSTGRES_PASSWORD: senha_segura
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./database/init.sql:/docker-entrypoint-initdb.d/init.sql
    networks:
      - orseca-network

  redis:
    image: redis:6-alpine
    container_name: orseca-redis
    restart: unless-stopped
    command: redis-server --appendonly yes
    volumes:
      - redis_data:/data
    networks:
      - orseca-network

  nginx:
    image: nginx:alpine
    container_name: orseca-nginx
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf
      - ./nginx/ssl:/etc/nginx/ssl
      - ./frontend/dist:/usr/share/nginx/html
    depends_on:
      - backend
      - frontend
    networks:
      - orseca-network

volumes:
  postgres_data:
  redis_data:

networks:
  orseca-network:
    driver: bridge
```

## Configuração do Frontend

### 1. Build de Produção

```bash
# Instalar dependências
cd /opt/orseca-exchange/frontend
npm install

# Configurar variáveis de ambiente
cat > .env.production << EOF
VITE_API_BASE_URL=https://api.exchange.orseca.org
VITE_WS_URL=wss://api.exchange.orseca.org/ws
VITE_ENVIRONMENT=production
VITE_SENTRY_DSN=sua-dsn-do-sentry
EOF

# Build de produção
npm run build
```

### 2. Dockerfile de Produção

```dockerfile
# frontend/Dockerfile.prod
FROM node:18-alpine as builder

WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

## Configuração do Nginx

### 1. Configuração Principal

```nginx
# nginx/nginx.conf
events {
    worker_connections 1024;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    # Configurações de segurança
    server_tokens off;
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
    limit_req_zone $binary_remote_addr zone=login:10m rate=1r/s;

    # Upstream para backend
    upstream backend {
        server backend:5000;
    }

    # Redirecionamento HTTP para HTTPS
    server {
        listen 80;
        server_name exchange.orseca.org www.exchange.orseca.org;
        return 301 https://$server_name$request_uri;
    }

    # Servidor HTTPS principal
    server {
        listen 443 ssl http2;
        server_name exchange.orseca.org www.exchange.orseca.org;

        # Configurações SSL
        ssl_certificate /etc/nginx/ssl/fullchain.pem;
        ssl_certificate_key /etc/nginx/ssl/privkey.pem;
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;
        ssl_prefer_server_ciphers off;

        # Frontend
        location / {
            root /usr/share/nginx/html;
            index index.html;
            try_files $uri $uri/ /index.html;
            
            # Cache para assets estáticos
            location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
                expires 1y;
                add_header Cache-Control "public, immutable";
            }
        }

        # API Backend
        location /api/ {
            limit_req zone=api burst=20 nodelay;
            
            proxy_pass http://backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            
            # Timeouts
            proxy_connect_timeout 30s;
            proxy_send_timeout 30s;
            proxy_read_timeout 30s;
        }

        # WebSocket para dados em tempo real
        location /ws/ {
            proxy_pass http://backend;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # Endpoint de login com rate limiting mais restritivo
        location /api/auth/login {
            limit_req zone=login burst=5 nodelay;
            proxy_pass http://backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
    }
}
```

## Configuração do Banco de Dados

### 1. Inicialização

```sql
-- database/init.sql
CREATE DATABASE orseca_exchange;
CREATE USER orseca_user WITH ENCRYPTED PASSWORD 'senha_segura';
GRANT ALL PRIVILEGES ON DATABASE orseca_exchange TO orseca_user;

-- Configurações de performance
ALTER SYSTEM SET shared_buffers = '256MB';
ALTER SYSTEM SET effective_cache_size = '1GB';
ALTER SYSTEM SET maintenance_work_mem = '64MB';
ALTER SYSTEM SET checkpoint_completion_target = 0.9;
ALTER SYSTEM SET wal_buffers = '16MB';
ALTER SYSTEM SET default_statistics_target = 100;
```

### 2. Backup Automático

```bash
#!/bin/bash
# scripts/backup.sh

BACKUP_DIR="/opt/orseca-exchange/backups"
DATE=$(date +%Y%m%d_%H%M%S)
DB_NAME="orseca_exchange"

# Criar diretório de backup
mkdir -p $BACKUP_DIR

# Backup do banco de dados
docker exec orseca-db pg_dump -U orseca_user $DB_NAME | gzip > $BACKUP_DIR/db_backup_$DATE.sql.gz

# Backup de arquivos de upload
tar -czf $BACKUP_DIR/uploads_backup_$DATE.tar.gz /opt/orseca-exchange/uploads/

# Manter apenas os últimos 30 backups
find $BACKUP_DIR -name "*.gz" -mtime +30 -delete

echo "Backup concluído: $DATE"
```

## Scripts de Deployment

### 1. Script de Deploy

```bash
#!/bin/bash
# scripts/deploy.sh

set -e

echo "🚀 Iniciando deployment da Exchange ORSECA..."

# Verificar se está executando como usuário correto
if [ "$USER" != "orseca-exchange" ]; then
    echo "❌ Execute como usuário orseca-exchange"
    exit 1
fi

# Navegar para diretório da aplicação
cd /opt/orseca-exchange

# Fazer backup antes do deploy
echo "📦 Criando backup..."
./scripts/backup.sh

# Atualizar código
echo "📥 Atualizando código..."
git pull origin main

# Parar serviços
echo "⏹️ Parando serviços..."
docker-compose -f docker-compose.prod.yml down

# Build das imagens
echo "🔨 Construindo imagens..."
docker-compose -f docker-compose.prod.yml build

# Executar migrações
echo "🗄️ Executando migrações..."
docker-compose -f docker-compose.prod.yml run --rm backend python -m flask db upgrade

# Iniciar serviços
echo "▶️ Iniciando serviços..."
docker-compose -f docker-compose.prod.yml up -d

# Verificar saúde dos serviços
echo "🔍 Verificando saúde dos serviços..."
sleep 30

if curl -f http://localhost/api/health > /dev/null 2>&1; then
    echo "✅ Deployment concluído com sucesso!"
else
    echo "❌ Falha no deployment - verificar logs"
    docker-compose -f docker-compose.prod.yml logs
    exit 1
fi
```

### 2. Script de Monitoramento

```bash
#!/bin/bash
# scripts/monitor.sh

# Verificar status dos containers
echo "📊 Status dos Containers:"
docker-compose -f docker-compose.prod.yml ps

# Verificar uso de recursos
echo -e "\n💾 Uso de Memória:"
docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}"

# Verificar logs de erro
echo -e "\n🚨 Últimos Erros:"
docker-compose -f docker-compose.prod.yml logs --tail=50 | grep -i error

# Verificar conectividade
echo -e "\n🌐 Teste de Conectividade:"
curl -s -o /dev/null -w "API Status: %{http_code}\n" http://localhost/api/health
curl -s -o /dev/null -w "Frontend Status: %{http_code}\n" http://localhost/
```

## Configuração de SSL

### 1. Certificado Let's Encrypt

```bash
# Instalar Certbot
sudo apt update
sudo apt install certbot python3-certbot-nginx

# Obter certificado
sudo certbot --nginx -d exchange.orseca.org -d www.exchange.orseca.org

# Configurar renovação automática
sudo crontab -e
# Adicionar linha:
# 0 12 * * * /usr/bin/certbot renew --quiet
```

### 2. Configuração Manual de SSL

```bash
# Criar diretório SSL
mkdir -p /opt/orseca-exchange/nginx/ssl

# Copiar certificados
cp /path/to/fullchain.pem /opt/orseca-exchange/nginx/ssl/
cp /path/to/privkey.pem /opt/orseca-exchange/nginx/ssl/

# Definir permissões
chmod 600 /opt/orseca-exchange/nginx/ssl/*
chown root:root /opt/orseca-exchange/nginx/ssl/*
```

## Monitoramento e Logs

### 1. Configuração de Logs

```yaml
# Adicionar ao docker-compose.prod.yml
logging:
  driver: "json-file"
  options:
    max-size: "10m"
    max-file: "3"
```

### 2. Monitoramento com Prometheus

```yaml
# monitoring/docker-compose.monitoring.yml
version: '3.8'

services:
  prometheus:
    image: prom/prometheus
    container_name: orseca-prometheus
    restart: unless-stopped
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    networks:
      - orseca-network

  grafana:
    image: grafana/grafana
    container_name: orseca-grafana
    restart: unless-stopped
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=senha_admin
    volumes:
      - grafana_data:/var/lib/grafana
    networks:
      - orseca-network

volumes:
  prometheus_data:
  grafana_data:

networks:
  orseca-network:
    external: true
```

## Segurança

### 1. Firewall

```bash
# Configurar UFW
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

### 2. Fail2Ban

```bash
# Instalar Fail2Ban
sudo apt install fail2ban

# Configurar para Nginx
cat > /etc/fail2ban/jail.local << EOF
[nginx-http-auth]
enabled = true
filter = nginx-http-auth
logpath = /var/log/nginx/error.log
maxretry = 3
bantime = 3600

[nginx-limit-req]
enabled = true
filter = nginx-limit-req
logpath = /var/log/nginx/error.log
maxretry = 10
bantime = 600
EOF

sudo systemctl restart fail2ban
```

## Manutenção

### 1. Atualizações Regulares

```bash
# Criar cron job para atualizações
cat > /etc/cron.d/orseca-maintenance << EOF
# Backup diário às 2:00 AM
0 2 * * * orseca-exchange /opt/orseca-exchange/scripts/backup.sh

# Limpeza de logs às 3:00 AM
0 3 * * * orseca-exchange docker system prune -f

# Verificação de saúde a cada 5 minutos
*/5 * * * * orseca-exchange /opt/orseca-exchange/scripts/health-check.sh
EOF
```

### 2. Procedimentos de Emergência

```bash
# Script de rollback
#!/bin/bash
# scripts/rollback.sh

echo "🔄 Iniciando rollback..."

# Parar serviços atuais
docker-compose -f docker-compose.prod.yml down

# Restaurar backup mais recente
LATEST_BACKUP=$(ls -t /opt/orseca-exchange/backups/db_backup_*.sql.gz | head -1)
gunzip -c $LATEST_BACKUP | docker exec -i orseca-db psql -U orseca_user orseca_exchange

# Voltar para commit anterior
git reset --hard HEAD~1

# Rebuild e restart
docker-compose -f docker-compose.prod.yml build
docker-compose -f docker-compose.prod.yml up -d

echo "✅ Rollback concluído"
```

## Checklist de Deployment

### Pré-Deployment
- [ ] Servidor configurado com recursos adequados
- [ ] Domínio configurado e DNS apontando para servidor
- [ ] Certificado SSL obtido e configurado
- [ ] Variáveis de ambiente configuradas
- [ ] Backup do ambiente atual (se aplicável)

### Durante Deployment
- [ ] Código atualizado do repositório
- [ ] Imagens Docker construídas
- [ ] Migrações de banco executadas
- [ ] Serviços iniciados
- [ ] Testes de conectividade realizados

### Pós-Deployment
- [ ] Monitoramento configurado
- [ ] Logs verificados
- [ ] Performance testada
- [ ] Backup automático configurado
- [ ] Documentação atualizada

## Troubleshooting

### Problemas Comuns

1. **Container não inicia**
   ```bash
   docker-compose logs [service_name]
   docker inspect [container_name]
   ```

2. **Erro de conexão com banco**
   ```bash
   docker exec -it orseca-db psql -U orseca_user orseca_exchange
   ```

3. **Problemas de SSL**
   ```bash
   openssl s_client -connect exchange.orseca.org:443
   ```

4. **Performance lenta**
   ```bash
   docker stats
   htop
   iotop
   ```

### Contatos de Suporte

- **Técnico**: tech@orseca.org
- **Emergência**: +55 11 9999-9999
- **Documentação**: https://docs.exchange.orseca.org

---

*Este guia deve ser atualizado conforme a evolução da plataforma e mudanças na infraestrutura.*

**Versão**: 1.0  
**Data**: 22 de Julho de 2025  
**Responsável**: Equipe DevOps ORSECA

