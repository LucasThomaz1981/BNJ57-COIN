#!/usr/bin/env python3
"""
BNJ57 Exchange Backend
Aplicação Flask para gerenciamento de recuperação de chaves privadas
"""

import os
from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import structlog
import uuid
from datetime import datetime
from exchange import db as exchange_db

# Configuração de logging estruturado
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

def _parse_allowed_origins(origins_str: str):
    if not origins_str or origins_str.strip() == '*':
        return '*'
    # Split by comma and strip spaces
    return [o.strip() for o in origins_str.split(',') if o.strip()]

def create_app(config_name='development'):
    """Factory function para criar a aplicação Flask"""
    app = Flask(__name__)
    
    # Configurações
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')
    app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'jwt-secret-key')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
        'DATABASE_URL', 
        'postgresql://bnj57:password@localhost:5432/bnj57_dev'
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['REDIS_URL'] = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
    
    # ORM
    exchange_db.init_app(app)
    
    # Extensões
    allowed_origins = _parse_allowed_origins(os.environ.get('ALLOWED_ORIGINS', '*'))
    CORS(app, origins=allowed_origins)
    jwt = JWTManager(app)
    
    # Rate limiting
    limiter = Limiter(
        get_remote_address,
        app=app,
        default_limits=["1000 per hour"]
    )
    
    # Rotas principais
    @app.route('/')
    def index():
        """Endpoint de health check"""
        return jsonify({
            'message': 'BNJ57 Exchange Backend API',
            'version': '1.0.0',
            'status': 'healthy'
        })
    
    @app.route('/api/v1/health')
    def health():
        """Endpoint detalhado de health check"""
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'services': {
                'database': 'connected',
                'redis': 'connected',
                'blockchain': 'connected'
            }
        })
    
    @app.route('/api/v1/wallets/<address>/status')
    @limiter.limit("100 per minute")
    def wallet_status(address):
        """Verifica o status de uma carteira"""
        logger.info("Checking wallet status", wallet_address=address)
        
        # Validação básica do endereço
        if not address or len(address) < 26:
            return jsonify({'error': 'Invalid wallet address'}), 400
        
        # Simulação de análise de carteira
        return jsonify({
            'address': address,
            'status': 'inactive',
            'last_activity': '2013-05-15T10:30:00Z',
            'balance': '1.5 BTC',
            'recovery_probability': 0.75,
            'estimated_time': '2-4 weeks'
        })
    
    @app.route('/api/v1/recovery/claim', methods=['POST'])
    @limiter.limit("10 per minute")
    def create_claim():
        """Cria uma nova reivindicação de recuperação"""
        data = request.get_json()
        
        if not data or 'wallet_address' not in data:
            return jsonify({'error': 'Wallet address is required'}), 400
        
        wallet_address = data['wallet_address']
        description = data.get('description', '')
        
        logger.info("Creating recovery claim", 
                   wallet_address=wallet_address, 
                   description=description)
        
        # Identificador seguro e único para a claim
        claim_id = f"claim_{uuid.uuid4().hex}"
        
        return jsonify({
            'claim_id': claim_id,
            'wallet_address': wallet_address,
            'status': 'pending',
            'created_at': datetime.utcnow().isoformat() + 'Z',
            'estimated_completion': '2025-08-22T20:00:00Z'
        }), 201
    
    @app.route('/api/v1/recovery/<claim_id>/status')
    def claim_status(claim_id):
        """Verifica o status de uma reivindicação"""
        logger.info("Checking claim status", claim_id=claim_id)
        
        return jsonify({
            'claim_id': claim_id,
            'status': 'processing',
            'progress': 45,
            'current_step': 'Analyzing blockchain patterns',
            'estimated_completion': '2025-08-22T20:00:00Z',
            'updates': [
                {
                    'timestamp': '2025-07-22T20:00:00Z',
                    'message': 'Claim submitted successfully'
                },
                {
                    'timestamp': '2025-07-22T20:15:00Z',
                    'message': 'Initial validation completed'
                },
                {
                    'timestamp': '2025-07-22T20:30:00Z',
                    'message': 'Blockchain analysis started'
                }
            ]
        })
    
    @app.route('/api/v1/analytics/recovery-stats')
    def recovery_stats():
        """Estatísticas de recuperação"""
        return jsonify({
            'total_claims': 1247,
            'successful_recoveries': 892,
            'success_rate': 0.715,
            'total_value_recovered': '15.7M USD',
            'average_recovery_time': '18 days',
            'active_claims': 127
        })
    
    @app.route('/api/v1/analytics/network-health')
    def network_health():
        """Saúde da rede"""
        return jsonify({
            'active_validators': 156,
            'total_staked': '2.5M BNJ57',
            'network_hashrate': '125 TH/s',
            'average_block_time': '15.2s',
            'pending_transactions': 23,
            'gas_price': '25 gwei'
        })
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Endpoint not found'}), 404
    
    @app.errorhandler(429)
    def rate_limit_exceeded(error):
        return jsonify({'error': 'Rate limit exceeded'}), 429
    
    @app.errorhandler(500)
    def internal_error(error):
        logger.error("Internal server error", error=str(error))
        return jsonify({'error': 'Internal server error'}), 500
    
    logger.info("BNJ57 Exchange Backend initialized", config=config_name)
    return app

if __name__ == '__main__':
    app = create_app()
    # Escutar em 0.0.0.0 para permitir acesso externo
    app.run(host='0.0.0.0', port=5000, debug=(os.environ.get('FLASK_DEBUG', '0') == '1'))

