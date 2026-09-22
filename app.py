import os
from flask import Flask, jsonify, request
from sqlalchemy import func
from flask_cors import CORS
from models import db, User, ServiceRequest, Proposal, Contract, SupportTicket

app = Flask(__name__)

ADMIN_KEY = os.environ.get("KAMBA_ADMIN_KEY", "kamba-empresa-2026")  # em produção, define KAMBA_ADMIN_KEY no Render

database_url = os.environ.get("DATABASE_URL", "sqlite:///kamba.db")

if database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)

app.config["SQLALCHEMY_DATABASE_URI"] = database_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

CORS(app)
db.init_app(app)

with app.app_context():
    db.create_all()


@app.get("/api/health")
def health():
    return jsonify({
        "ok": True,
        "service": "Kamba API"
    })


@app.get("/api/services")
def services():
    return jsonify([
        "Eletricidade",
        "Canalização",
        "Reparações",
        "Limpeza",
        "Tecnologia",
        "Design"
    ])


@app.post("/api/users")
def create_user():
    data = request.get_json(silent=True) or {}

    if not data.get("name") or not data.get("phone"):
        return jsonify({
            "error": "Nome e telefone são obrigatórios"
        }), 400

    user = User(
        name=data["name"],
        phone=data["phone"],
        email=data.get("email"),
        role=data.get("role", "client"),
        location=data.get("location"),
        specialty=data.get("specialty")
    )

    db.session.add(user)

    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        return jsonify({
            "error": "Telefone ou email já registado"
        }), 409

    return jsonify({
        "id": user.id,
        "name": user.name,
        "role": user.role
    }), 201


@app.get("/api/users/<int:user_id>")
def get_user(user_id):
    user = User.query.get_or_404(user_id)

    return jsonify({
        "id": user.id,
        "name": user.name,
        "phone": user.phone,
        "email": user.email,
        "role": user.role,
        "location": user.location,
        "specialty": user.specialty,
        "rating": user.rating
    })


@app.post("/api/requests")
def create_request():
    data = request.get_json(silent=True) or {}

    required = [
        "client_id",
        "service",
        "description",
        "location"
    ]

    missing = [field for field in required if not data.get(field)]

    if missing:
        return jsonify({
            "error": "Campos obrigatórios em falta",
            "fields": missing
        }), 400

    item = ServiceRequest(
        client_id=data["client_id"],
        service=data["service"],
        description=data["description"],
        location=data["location"],
        budget=data.get("budget"),
        date=data.get("date"),
        status="open"
    )

    db.session.add(item)
    db.session.commit()

    return jsonify(item.to_dict()), 201


@app.get("/api/requests")
def list_requests():
    items = ServiceRequest.query.order_by(
        ServiceRequest.id.desc()
    ).all()

    return jsonify([
        item.to_dict()
        for item in items
    ])


@app.get("/api/requests/client/<int:client_id>")
def list_client_requests(client_id):
    items = ServiceRequest.query.filter_by(
        client_id=client_id
    ).order_by(
        ServiceRequest.id.desc()
    ).all()

    return jsonify([
        item.to_dict()
        for item in items
    ])


@app.get("/api/requests/<int:request_id>")
def get_request(request_id):
    item = ServiceRequest.query.get_or_404(request_id)
    return jsonify(item.to_dict())


@app.get("/api/requests/<int:request_id>/proposals")
def list_proposals(request_id):
    items = Proposal.query.filter_by(
        request_id=request_id
    ).order_by(
        Proposal.id.desc()
    ).all()

    return jsonify([
        item.to_dict()
        for item in items
    ])


@app.post("/api/proposals")
def create_proposal():
    data = request.get_json(silent=True) or {}

    required = [
        "request_id",
        "professional_id",
        "price"
    ]

    missing = [
        field for field in required
        if data.get(field) is None
    ]

    if missing:
        return jsonify({
            "error": "Campos obrigatórios em falta",
            "fields": missing
        }), 400

    existing = Proposal.query.filter_by(
        request_id=data["request_id"],
        professional_id=data["professional_id"]
    ).first()

    if existing:
        return jsonify({
            "error": "Já enviaste uma proposta para este pedido."
        }), 409

    proposal = Proposal(
        request_id=data["request_id"],
        professional_id=data["professional_id"],
        price=data["price"],
        message=data.get("message", ""),
        status="pending"
    )

    db.session.add(proposal)
    db.session.commit()

    return jsonify(proposal.to_dict()), 201


@app.post("/api/contracts")
def create_contract():
    data = request.get_json(silent=True) or {}

    required = [
        "request_id",
        "proposal_id",
        "client_id",
        "professional_id",
        "price"
    ]

    missing = [
        field for field in required
        if data.get(field) is None
    ]

    if missing:
        return jsonify({
            "error": "Campos obrigatórios em falta",
            "fields": missing
        }), 400

    contract = Contract(
        request_id=data["request_id"],
        proposal_id=data["proposal_id"],
        client_id=data["client_id"],
        professional_id=data["professional_id"],
        price=data["price"],
        status="active"
    )

    db.session.add(contract)

    req = ServiceRequest.query.get(
        data["request_id"]
    )

    if req:
        req.status = "contracted"

    db.session.commit()

    return jsonify(contract.to_dict()), 201


@app.get("/api/contracts/<int:contract_id>")
def get_contract(contract_id):
    contract = Contract.query.get_or_404(contract_id)
    return jsonify(contract.to_dict())


@app.post("/api/support")
def create_support_ticket():
    data = request.get_json(silent=True) or {}

    required = [
        "name",
        "contact",
        "topic",
        "message"
    ]

    missing = [
        field for field in required
        if not data.get(field)
    ]

    if missing:
        return jsonify({
            "error": "Campos obrigatórios em falta",
            "fields": missing
        }), 400

    ticket = SupportTicket(
        name=data["name"],
        contact=data["contact"],
        topic=data["topic"],
        message=data["message"],
        status="open"
    )

    db.session.add(ticket)
    db.session.commit()

    return jsonify({
        "ok": True,
        "message": "Pedido de suporte recebido",
        "ticket": ticket.to_dict()
    }), 201


@app.get("/api/support")
def list_support_tickets():
    tickets = SupportTicket.query.order_by(
        SupportTicket.id.desc()
    ).all()

    return jsonify([
        ticket.to_dict()
        for ticket in tickets
    ])



@app.post("/api/login")
def login():
    data = request.get_json(silent=True) or {}
    phone = data.get("phone")

    if not phone:
        return jsonify({
            "error": "Telefone é obrigatório"
        }), 400

    user = User.query.filter_by(phone=phone).first()

    if not user:
        return jsonify({
            "error": "Utilizador não encontrado"
        }), 404

    return jsonify({
        "id": user.id,
        "name": user.name,
        "phone": user.phone,
        "email": user.email,
        "role": user.role,
        "location": user.location,
        "specialty": user.specialty,
        "rating": user.rating
    })



def check_admin():
    phone = request.headers.get("X-Admin-Phone")

    if not phone:
        return False

    user = User.query.filter_by(phone=phone, role="admin").first()
    return user is not None


@app.post("/api/admin/team-login")
def team_login():
    data = request.get_json(silent=True) or {}
    phone = data.get("phone")

    if not phone:
        return jsonify({"error": "Telefone é obrigatório"}), 400

    user = User.query.filter_by(phone=phone, role="admin").first()

    if not user:
        return jsonify({"error": "Não autorizado"}), 403

    return jsonify({
        "id": user.id,
        "name": user.name,
        "phone": user.phone,
        "role": user.role
    })


@app.post("/api/admin/team")
def create_team_member():
    master_key = request.headers.get("X-Master-Key")

    if master_key != ADMIN_KEY:
        return jsonify({"error": "Chave mestra inválida"}), 403

    data = request.get_json(silent=True) or {}

    if not data.get("name") or not data.get("phone"):
        return jsonify({
            "error": "Nome e telefone são obrigatórios"
        }), 400

    user = User(
        name=data["name"],
        phone=data["phone"],
        email=data.get("email"),
        role="admin",
        location=data.get("location")
    )

    db.session.add(user)

    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        return jsonify({
            "error": "Telefone já registado"
        }), 409

    return jsonify({
        "id": user.id,
        "name": user.name,
        "role": user.role
    }), 201


@app.get("/api/admin/stats")
def admin_stats():
    if not check_admin():
        return jsonify({"error": "Acesso negado"}), 403

    total_contract_value = db.session.query(
        func.coalesce(func.sum(Contract.price), 0)
    ).scalar()

    return jsonify({
        "total_users": User.query.count(),
        "total_clients": User.query.filter_by(role="client").count(),
        "total_professionals": User.query.filter_by(role="professional").count(),
        "total_requests": ServiceRequest.query.count(),
        "requests_open": ServiceRequest.query.filter_by(status="open").count(),
        "requests_contracted": ServiceRequest.query.filter_by(status="contracted").count(),
        "total_contracts": Contract.query.count(),
        "total_contract_value": total_contract_value,
        "total_proposals": Proposal.query.count(),
        "total_support_tickets": SupportTicket.query.count(),
        "support_open": SupportTicket.query.filter_by(status="open").count()
    })


@app.get("/api/admin/monthly")
def admin_monthly():
    if not check_admin():
        return jsonify({"error": "Acesso negado"}), 403

    requests_by_month = db.session.query(
        func.strftime("%Y-%m", ServiceRequest.created_at).label("month"),
        func.count(ServiceRequest.id)
    ).group_by("month").order_by("month").all()

    contracts_by_month = db.session.query(
        func.strftime("%Y-%m", Contract.created_at).label("month"),
        func.count(Contract.id),
        func.coalesce(func.sum(Contract.price), 0)
    ).group_by("month").order_by("month").all()

    requests_map = {month: count for month, count in requests_by_month}
    contracts_map = {month: (count, value) for month, count, value in contracts_by_month}

    months = sorted(set(list(requests_map.keys()) + list(contracts_map.keys())))

    result = []
    for month in months:
        c_count, c_value = contracts_map.get(month, (0, 0))
        result.append({
            "month": month,
            "requests": requests_map.get(month, 0),
            "contracts": c_count,
            "revenue": c_value
        })

    return jsonify(result)


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000)),
        debug=os.environ.get("FLASK_DEBUG", "0") == "1"
    )
