from src.models.user import db
from datetime import datetime
from enum import Enum
import uuid

class ORSECALevel(Enum):
    ASPIRANTE = "aspirante"  # Sementes
    INICIADO = "iniciado"    # Brotos
    ADEPTO = "adepto"        # Ramos
    MESTRE = "mestre"        # Troncos
    GUARDIAO = "guardiao"    # Raízes

class OrderType(Enum):
    MARKET = "market"
    LIMIT = "limit"
    STOP_LIMIT = "stop_limit"

class OrderSide(Enum):
    BUY = "buy"
    SELL = "sell"

class OrderStatus(Enum):
    PENDING = "pending"
    PARTIAL = "partial"
    FILLED = "filled"
    CANCELLED = "cancelled"

class TradingPair(Enum):
    BNJ57_BTC = "BNJ57/BTC"
    BNJ57_ETH = "BNJ57/ETH"
    BNJ57_USDT = "BNJ57/USDT"
    BNJ57_BRL = "BNJ57/BRL"

class ORSECAMember(db.Model):
    __tablename__ = 'orseca_members'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    orseca_id = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    level = db.Column(db.Enum(ORSECALevel), nullable=False, default=ORSECALevel.ASPIRANTE)
    is_active = db.Column(db.Boolean, default=True)
    joined_date = db.Column(db.DateTime, default=datetime.utcnow)
    last_activity = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relacionamentos
    wallets = db.relationship('Wallet', backref='member', lazy=True)
    orders = db.relationship('Order', backref='member', lazy=True)
    transactions = db.relationship('Transaction', backref='member', lazy=True)
    
    def __repr__(self):
        return f'<ORSECAMember {self.name} ({self.level.value})>'
    
    def get_trading_limits(self):
        """Retorna limites de trading baseado no nível ORSECA"""
        limits = {
            ORSECALevel.ASPIRANTE: {
                'daily_limit': 1000.0,
                'single_order_limit': 100.0,
                'advanced_orders': False
            },
            ORSECALevel.INICIADO: {
                'daily_limit': 10000.0,
                'single_order_limit': 1000.0,
                'advanced_orders': True
            },
            ORSECALevel.ADEPTO: {
                'daily_limit': 50000.0,
                'single_order_limit': 5000.0,
                'advanced_orders': True
            },
            ORSECALevel.MESTRE: {
                'daily_limit': 100000.0,
                'single_order_limit': 10000.0,
                'advanced_orders': True
            },
            ORSECALevel.GUARDIAO: {
                'daily_limit': float('inf'),
                'single_order_limit': float('inf'),
                'advanced_orders': True
            }
        }
        return limits.get(self.level, limits[ORSECALevel.ASPIRANTE])

class Wallet(db.Model):
    __tablename__ = 'wallets'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    member_id = db.Column(db.String(36), db.ForeignKey('orseca_members.id'), nullable=False)
    currency = db.Column(db.String(10), nullable=False)  # BNJ57, BTC, ETH, USDT, BRL
    balance = db.Column(db.Numeric(20, 8), default=0.0)
    locked_balance = db.Column(db.Numeric(20, 8), default=0.0)  # Saldo bloqueado em ordens
    address = db.Column(db.String(100))  # Endereço da carteira (para criptos)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Wallet {self.currency}: {self.balance}>'
    
    def available_balance(self):
        """Retorna saldo disponível (total - bloqueado)"""
        return float(self.balance) - float(self.locked_balance)

class Order(db.Model):
    __tablename__ = 'orders'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    member_id = db.Column(db.String(36), db.ForeignKey('orseca_members.id'), nullable=False)
    trading_pair = db.Column(db.Enum(TradingPair), nullable=False)
    order_type = db.Column(db.Enum(OrderType), nullable=False)
    side = db.Column(db.Enum(OrderSide), nullable=False)
    quantity = db.Column(db.Numeric(20, 8), nullable=False)
    price = db.Column(db.Numeric(20, 8))  # Null para market orders
    stop_price = db.Column(db.Numeric(20, 8))  # Para stop-limit orders
    filled_quantity = db.Column(db.Numeric(20, 8), default=0.0)
    status = db.Column(db.Enum(OrderStatus), default=OrderStatus.PENDING)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    trades = db.relationship('Trade', backref='order', lazy=True)
    
    def __repr__(self):
        return f'<Order {self.side.value} {self.quantity} {self.trading_pair.value}>'
    
    def remaining_quantity(self):
        """Retorna quantidade restante para ser executada"""
        return float(self.quantity) - float(self.filled_quantity)

class Trade(db.Model):
    __tablename__ = 'trades'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    order_id = db.Column(db.String(36), db.ForeignKey('orders.id'), nullable=False)
    trading_pair = db.Column(db.Enum(TradingPair), nullable=False)
    quantity = db.Column(db.Numeric(20, 8), nullable=False)
    price = db.Column(db.Numeric(20, 8), nullable=False)
    total = db.Column(db.Numeric(20, 8), nullable=False)
    fee = db.Column(db.Numeric(20, 8), default=0.0)
    executed_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Trade {self.quantity} @ {self.price}>'

class Transaction(db.Model):
    __tablename__ = 'transactions'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    member_id = db.Column(db.String(36), db.ForeignKey('orseca_members.id'), nullable=False)
    transaction_type = db.Column(db.String(20), nullable=False)  # deposit, withdrawal, trade, reward
    currency = db.Column(db.String(10), nullable=False)
    amount = db.Column(db.Numeric(20, 8), nullable=False)
    fee = db.Column(db.Numeric(20, 8), default=0.0)
    status = db.Column(db.String(20), default='pending')  # pending, confirmed, failed
    blockchain_hash = db.Column(db.String(100))  # Hash da transação na blockchain
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    confirmed_at = db.Column(db.DateTime)
    
    def __repr__(self):
        return f'<Transaction {self.transaction_type} {self.amount} {self.currency}>'

class MarketData(db.Model):
    __tablename__ = 'market_data'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    trading_pair = db.Column(db.Enum(TradingPair), nullable=False)
    price = db.Column(db.Numeric(20, 8), nullable=False)
    volume_24h = db.Column(db.Numeric(20, 8), default=0.0)
    high_24h = db.Column(db.Numeric(20, 8), default=0.0)
    low_24h = db.Column(db.Numeric(20, 8), default=0.0)
    change_24h = db.Column(db.Numeric(10, 4), default=0.0)  # Percentual
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<MarketData {self.trading_pair.value}: {self.price}>'

class ORSECAReward(db.Model):
    __tablename__ = 'orseca_rewards'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    member_id = db.Column(db.String(36), db.ForeignKey('orseca_members.id'), nullable=False)
    reward_type = db.Column(db.String(50), nullable=False)  # participation, achievement, referral, etc.
    amount = db.Column(db.Numeric(20, 8), nullable=False)
    description = db.Column(db.Text)
    granted_at = db.Column(db.DateTime, default=datetime.utcnow)
    claimed_at = db.Column(db.DateTime)
    is_claimed = db.Column(db.Boolean, default=False)
    
    def __repr__(self):
        return f'<ORSECAReward {self.reward_type}: {self.amount} BNJ57>'

