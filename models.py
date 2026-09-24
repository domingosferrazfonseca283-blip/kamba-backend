from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(30), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True)
    role = db.Column(db.String(30), default="client")
    location = db.Column(db.String(200))
    specialty = db.Column(db.String(120))
    rating = db.Column(db.Float, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class ServiceRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, nullable=False)
    service = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=False)
    location = db.Column(db.String(200), nullable=False)
    budget = db.Column(db.Float)
    date = db.Column(db.String(50))
    status = db.Column(db.String(30), default="open")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "client_id": self.client_id,
            "service": self.service,
            "description": self.description,
            "location": self.location,
            "budget": self.budget,
            "date": self.date,
            "status": self.status,
            "created_at": self.created_at.isoformat()
        }


class Proposal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    request_id = db.Column(db.Integer, nullable=False)
    professional_id = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
    message = db.Column(db.Text, default="")
    status = db.Column(db.String(30), default="pending")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "request_id": self.request_id,
            "professional_id": self.professional_id,
            "price": self.price,
            "message": self.message,
            "status": self.status,
            "created_at": self.created_at.isoformat()
        }


class Contract(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    request_id = db.Column(db.Integer, nullable=False)
    proposal_id = db.Column(db.Integer, nullable=False)
    client_id = db.Column(db.Integer, nullable=False)
    professional_id = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(30), default="active")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "request_id": self.request_id,
            "proposal_id": self.proposal_id,
            "client_id": self.client_id,
            "professional_id": self.professional_id,
            "price": self.price,
            "status": self.status,
            "created_at": self.created_at.isoformat()
        }


class SupportTicket(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    contact = db.Column(db.String(120), nullable=False)
    topic = db.Column(db.String(120), nullable=False)
    message = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(30), default="open")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "contact": self.contact,
            "topic": self.topic,
            "message": self.message,
            "status": self.status,
            "created_at": self.created_at.isoformat()
        }


class Company(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    key = db.Column(db.String(120), nullable=False)
    area = db.Column(db.String(60), default="general")
    is_admin = db.Column(db.Boolean, default=False)
    token = db.Column(db.String(64))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
